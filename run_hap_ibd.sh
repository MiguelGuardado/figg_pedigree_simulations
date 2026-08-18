#!/bin/env bash
#$ -cwd
#$ -l h_rt=300:00:00
#$ -l mem_free=15G
#$ -t 1-100

module load CBI r plink bcftools miniforge3
conda activate hapibd


# Inputs: Superpopulation Label
while getopts s: flag
do
    case "${flag}" in
        s) super_pop=${OPTARG};;
    esac
done

# Based on the SGE_TASK_ID (or first arg), read the corresponding line from the input file and export variables
# N=${1:-${SGE_TASK_ID:-1}}
# FILE=${2:-input_data/job_id_1000sims.txt}

# line=$(sed -n "${N}p" "$FILE")
# if [[ -z "$line" ]]; then
#   echo "No line $N in $FILE" >&2
#   exit 1
# fi

# read -r JOB POP SEED CHR <<< "$line"

# export JOB POP SEED CHR

# echo "JOB=$JOB POP=$POP SEED=$SEED CHR=$CHR"

input_dir=/wynton/scratch/guardado075/king_hap_ibd/large_fam_1000sims
vcf_filepath="${input_dir}/largefam_${super_pop}_seed${SGE_TASK_ID}_merged_genomes.vcf.gz"

# Now we will run hap ibd for each indiv part of the genome
map_file=/wynton/group/hernandez/guardado075/hapibd/map_files/plink.GRCh38.full.FixCHR.map
out_file=~/rohlfs_lab/igg_prelim/king_hap_ibd/large_fam_1000sims/results/hap_ibd_full/large_fam_${super_pop}_seed${SGE_TASK_ID}

hap-ibd \
  gt="$vcf_filepath" \
  map="$map_file" \
  out="$out_file"