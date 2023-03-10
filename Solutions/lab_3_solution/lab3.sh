#!/bin/bash
#$ -l h_rt=1:00:00  #time needed
#$ -pe smp 4 #number of cores
#$ -l rmem=10G #number of memery
#$ -P rse-com6012 # require a com6012-reserved node
#$ -q rse-com6012.q # specify com6012 queue
#$ -o ../Output/Lab3.txt  #This is where your output and errors are logged.
#$ -j y # normal and error outputs into a single file (the file above)
#$ -cwd # Run job from current directory

module load apps/java/jdk1.8.0_102/binary

module load apps/python/conda

source activate myspark

spark-submit ../Code/lab3.py
