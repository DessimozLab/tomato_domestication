#!/bin/bash
#SBATCH --cpus-per-task=1
#SBATCH --mem=24G
#SBATCH --time=6:00:00
#SBATCH --job-name=hogprop
#SBATCH --output=logs/hogprop_%A_%a.out
#SBATCH --array=1-500

MYID=${SLURM_ARRAY_TASK_ID}
NJOBS=${SLURM_ARRAY_TASK_MAX}

mamba activate FastOMA-release
hogprop --obo ../data/geneontology/go.obo \
	--gaf ../data/functional_predictions/all_predictions_filtered_viridiplantae.gaf.gz \
	--go_filter all \
	--combination_func max \
	--oxml ./result/FastOMA_HOGs_relabel.orthoxml \
	--no_convert --results hogprop_results/output.h5 --myid ${MYID} --njobs ${NJOBS}
