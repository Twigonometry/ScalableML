#!/bin/bash
#$ -l h_rt=6:00:00  
#$ -pe smp 4 
#$ -l rmem=10G 
#$ -o ../Output/Output.txt  
#$ -j y # normal and error outputs into a single file (the file above)
#$ -M youremail@shef.ac.uk 
#$ -m ea #Email you when it finished or aborted
#$ -cwd 

module load apps/java/jdk1.8.0_102/binary

module load apps/python/conda

source activate myspark

spark-submit --driver-memory 20g --executor-memory 10g Code/bikesGLMs.py  