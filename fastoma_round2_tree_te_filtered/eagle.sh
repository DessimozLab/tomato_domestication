#!/bin/bash
#SBATCH --cpus-per-task=1
#SBATCH --mem=8G
#SBATCH --time=6:00:00
#SBATCH --job-name=eagle
#SBATCH --output=logs/eagle_%A_%a.out
#SBATCH --array=1-100

MYID=${SLURM_ARRAY_TASK_ID}
NJOBS=${SLURM_ARRAY_TASK_MAX}

mamba activate FastOMA-release

TREE_NAME=`basename ${PWD}| cut -d '_' -f3-`

# get top level hog filter file
FILTER_FN=hogs_to_keep_no_misplaced.txt

# get relabelled tree
NWK_FN=../labelled_trees/${TREE_NAME}.nwk

RESULTS_PATH=./eagle_results
mkdir -p ${RESULTS_PATH}

eagle --obo ../data/geneontology/go.obo \
      --oxml ./result/FastOMA_HOGs_relabel.orthoxml \
      --nwk ${NWK_FN} \
      --hogprop_results ./hogprop_output.h5 \
      --results ${RESULTS_PATH} \
      --skip_terminal \
      --include_genelist \
      --write_extant_genelist \
      --root_hogs_to_use ${FILTER_FN} \
      --myid ${MYID} --njobs ${NJOBS}
