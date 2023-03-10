import numpy as np
from pyspark.sql import SparkSession

spark = SparkSession.builder \
    .master("local[4]") \
    .appName("Bikes Poisson GLM") \
    .config("spark.local.dir","/fastdata/YOUR_USERNAME") \
    .getOrCreate()

sc = spark.sparkContext
sc.setLogLevel("WARN")  # This can only affect the log level after it is executed.

#read
rawdata = spark.read.csv('./Data/hour.csv', header=True)
rawdata.cache()

#select features we need

schemaNames = rawdata.schema.names
ncolumns = len(rawdata.columns)
new_rawdata = rawdata.select(schemaNames[2:ncolumns])

#cast to doubles

new_schemaNames = new_rawdata.schema.names
from pyspark.sql.types import DoubleType
new_ncolumns = len(new_rawdata.columns)
for i in range(new_ncolumns):
    new_rawdata = new_rawdata.withColumn(new_schemaNames[i], new_rawdata[new_schemaNames[i]].cast(DoubleType()))

#split data
(trainingData, testData) = new_rawdata.randomSplit([0.7, 0.3], 42)

#vectorize
from pyspark.ml.feature import VectorAssembler
assembler = VectorAssembler(inputCols = new_schemaNames[0:new_ncolumns-3], outputCol = 'features')

#instantiate GLM - with regularisation

from pyspark.ml.regression import GeneralizedLinearRegression
glm_poisson = GeneralizedLinearRegression(featuresCol='features', labelCol='cnt', maxIter=50, regParam=0.01,\
                                          family='poisson', link='log')

from pyspark.ml import Pipeline
stages = [assembler, glm_poisson]
pipeline = Pipeline(stages=stages)

#train model
pipelineModel = pipeline.fit(trainingData)

#predict
predictions = pipelineModel.transform(testData)
from pyspark.ml.evaluation import RegressionEvaluator
evaluator = RegressionEvaluator\
      (labelCol="cnt", predictionCol="prediction", metricName="rmse")
rmse = evaluator.evaluate(predictions)
print("RMSE = %g " % rmse)

from pyspark.ml.linalg import Vectors
ohe = OneHotEncoder()
ohe.setInputCols(["

spark.stop()