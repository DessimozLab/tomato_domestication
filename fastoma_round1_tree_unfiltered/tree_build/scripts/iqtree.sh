#!/bin/bash
#SBATCH --cpus-per-task=48
#SBATCH --mem=90GB
#SBATCH --time=11:00:00
#SBATCH --job-name=iqtree
#SBATCH --output=logs/iqtree_%A_%a.out

#module load iqtree2
mamba activate FastOMA-release

iqtree3 -s ${1} -m LG+F+G4 -T 48 -B 1000
