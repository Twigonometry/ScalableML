import numpy as np
from pyspark.sql import SparkSession

spark = SparkSession.builder \
    .master("local[4]") \
    .appName("Logistic Regression Spambase") \
    .config("spark.local.dir","/fastdata/YOUR_USERNAME") \
    .getOrCreate()

sc = spark.sparkContext
sc.setLogLevel("WARN")  # This can only affect the log level after it is executed.

rawdata = spark.read.csv('../Data/spambase.data')
rawdata.cache()
ncolumns = len(rawdata.columns)
spam_names = [spam_names.rstrip('\n') for spam_names in open('./Data/spambase.data.names')]
number_names = np.shape(spam_names)[0]
for i in range(number_names):
    local = spam_names[i]
    colon_pos = local.find(':')
    spam_names[i] = local[:colon_pos]

# For being able to save files in a Parquet file format, later on, we need to rename
# two columns with invalid characters ; and (
spam_names[spam_names.index('char_freq_;')] = 'char_freq_semicolon'
spam_names[spam_names.index('char_freq_(')] = 'char_freq_leftp'

schemaNames = rawdata.schema.names
spam_names[ncolumns-1] = 'labels'#extract the labels column
for i in range(ncolumns):
    rawdata = rawdata.withColumnRenamed(schemaNames[i], spam_names[i])

# cast to Double

from pyspark.sql.types import DoubleType
for i in range(ncolumns):
    rawdata = rawdata.withColumn(spam_names[i], rawdata[spam_names[i]].cast(DoubleType()))

# split and save the data in parquet format

(trainingDatag, testDatag) = rawdata.randomSplit([0.7, 0.3], 42)

trainingDatag.write.mode("overwrite").parquet('../Data/spamdata_training.parquet')
testDatag.write.mode("overwrite").parquet('../Data/spamdata_test.parquet')

trainingData = spark.read.parquet('../Data/spamdata_training.parquet')
testData = spark.read.parquet('../Data/spamdata_test.parquet')

from pyspark.ml.feature import VectorAssembler
vecAssembler = VectorAssembler(inputCols = spam_names[0:ncolumns-1], outputCol = 'features')

from pyspark.ml.classification import LogisticRegression
lr = LogisticRegression(featuresCol='features', labelCol='labels', maxIter=50, regParam=0, family="binomial")

from pyspark.ml import Pipeline

# Combine stages into pipeline
stages = [vecAssembler, lr]#vectorises then regresses
pipeline = Pipeline(stages=stages)

pipelineModel = pipeline.fit(trainingData)#trains the model

predictions = pipelineModel.transform(testData)#makes predictions

#evaluate the predictions
from pyspark.ml.evaluation import MulticlassClassificationEvaluator
evaluator = MulticlassClassificationEvaluator\
      (labelCol="labels", predictionCol="prediction", metricName="accuracy")
accuracy = evaluator.evaluate(predictions)
print("Accuracy = %g " % accuracy)

w_no_reg = pipelineModel.stages[-1].coefficients.values

#train using only l1-reg - adds a lambda parameter and weights towards l1 only
lrL1 = LogisticRegression(featuresCol='features', labelCol='labels', maxIter=50, regParam=0.01, \
                          elasticNetParam=1, family="binomial")

# Pipeline for the second model with L1 regularisation - same process as before
stageslrL1 = [vecAssembler, lrL1]
pipelinelrL1 = Pipeline(stages=stageslrL1)
pipelineModellrL1 = pipelinelrL1.fit(trainingData)

predictions = pipelineModellrL1.transform(testData)

# With Predictions
evaluator = MulticlassClassificationEvaluator\
      (labelCol="labels", predictionCol="prediction", metricName="accuracy")
accuracy = evaluator.evaluate(predictions)
print("Accuracy = %g " % accuracy)

w_L1 = pipelineModellrL1.stages[-1].coefficients.values

#plot the coefficients of w (our learned parameters) for both cases
import matplotlib 
matplotlib.use('Agg')
import matplotlib.pyplot as plt
f, (ax1, ax2) = plt.subplots(1, 2, sharey=True)
ax1.plot(w_no_reg)
ax1.set_title('No regularisation')
ax2.plot(w_L1)
ax2.set_title('L1 regularisation')
plt.savefig("Output/w_with_and_without_reg.png")

spark.stop()