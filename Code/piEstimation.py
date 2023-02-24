from pyspark.sql import SparkSession

spark = SparkSession.builder \
    .master("local[2]") \
    .appName("COM6012 Pi") \
    .config("spark.local.dir","/fastdata/USERNAME") \
    .getOrCreate()

sc = spark.sparkContext
sc.setLogLevel("WARN")

from random import random

def inside(p):
    x, y = random(), random()
    return x*x + y*y < 1

NUM_SAMPLES = 10000000
count = sc.parallelize(range(0, NUM_SAMPLES),8).filter(inside).count()
print("Pi is roughly %f" % (4.0 * count / NUM_SAMPLES))

spark.stop()