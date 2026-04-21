mamba activate FastOMA-release
# unfiltered
UNFILTERED_ALN=concat_64
mkdir -p ${UNFILTERED_ALN}
python ./DessimozLab-f1000_PhylogeneticTree-0de208e/concat_alignments.py -o ${UNFILTERED_ALN}/concat_msa.phy ./OGs_64_aln/OG*.aln
sbatch ./scripts/iqtree.sh ${UNFILTERED_ALN}/concat_msa.phy
