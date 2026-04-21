## Run script
mamba activate FastOMA-release
FASTA_OG_PATH=../result/OrthologousGroupsFasta
python ./DessimozLab-f1000_PhylogeneticTree-0de208e/filter_groups.py --min-nr-species 64 --input ${FASTA_OG_PATH} -o OGs_64
