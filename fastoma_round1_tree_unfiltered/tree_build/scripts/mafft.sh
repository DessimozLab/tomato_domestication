#!/bin/bash
#SBATCH --cpus-per-task=4
#SBATCH --mem=10GB
#SBATCH --time=02:00:00
#SBATCH --job-name=mafft_OGs
#SBATCH --output=logs/mafft_%A_%a.out

module load mafft

IN_FILE=${1}
OUT_FILE=${2}

mkdir -p `dirname ${OUT_FILE}`
mafft --thread 4 --maxiterate 1000 --localpair "${IN_FILE}" > ${OUT_FILE}
