"""Log mining on big data"""

from pyspark.sql import SparkSession

spark = SparkSession.builder \
    .master("local[2]") \
    .appName("COM6012 Spark Intro") \
    .config("spark.local.dir","/fastdata/uname") \
    .getOrCreate()

sc = spark.sparkContext
sc.setLogLevel("WARN")  # This can only affect the log level after it is executed.

#runs from ScalableML/HPC (.sh script)
logFile=spark.read.text("../Data/NASA_access_log_Aug95.gz").cache()

hostsJapan = logFile.filter(logFile.value.contains(".jp")).count()
hostsUK = logFile.filter(logFile.value.contains(".uk")).count()
requestsTotal = logFile.count()
reqsGateway = logFile.filter(logFile.value.contains("gateway.timken.com")).cache()
reqsGatewayCount = reqsGateway.count()
reqs15Aug = logFile.filter(logFile.value.contains("15/Aug/1995")).cache()
reqs15AugCount = reqs15Aug.count()
reqs404 = logFile.filter(logFile.value.contains(" 404 ")).count()
reqs15Aug404 = reqs15Aug.filter(reqs15Aug.value.contains(" 404 ")).cache()
reqs15Aug404Count = reqs15Aug404.count()
reqs15Aug404Gateway = reqs15Aug404.filter(reqs15Aug404.value.contains("gateway.timken.com")).count()

print("\n\nHello Spark: There are %i hosts from UK.\n" % (hostsUK))
print("Hello Spark: There are %i hosts from Japan.\n\n" % (hostsJapan))
print("Hello Spark: There are %i gateway.timken.com requests.\n\n" % (reqsGatewayCount))
print("Hello Spark: There are %i requests on 15 Aug.\n\n" % (reqs15AugCount))
print("Hello Spark: There are %i 404 requests.\n\n" % (reqs404))
print("Hello Spark: There are %i 404 requests on 15 Aug.\n\n" % (reqs15Aug404Count))
print("Hello Spark: There are %i 404 requests on 15 Aug from gateway.timken.com.\n\n" % (reqs15Aug404Gateway))


spark.stop()
