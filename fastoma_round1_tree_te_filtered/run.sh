mamba activate FastOMA-release
nextflow run ../FastOMA/FastOMA.nf \
	--input input \
	--output_folder result \
	--omamer_db /work/FAC/FBM/DBC/cdessim2/oma/oma-browser/All.Jul2024/downloads/LUCA.h5 \
	--hogmap_in input/hogmap \
	--nr_repr_per_hog 100 \
	-profile slurm -qs 550 -w /scratch/awarwick/nextflow -resume
