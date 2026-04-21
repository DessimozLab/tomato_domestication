OG_PATH=OGs_64
MSA_OUT=OGs_64_aln
mkdir -p ${MSA_OUT}
for f in ${OG_PATH}/*
do
  sbatch ./scripts/mafft.sh ${f} ${MSA_OUT}/`basename ${f%.fa}`.aln
done
