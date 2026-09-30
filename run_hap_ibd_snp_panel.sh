#!/bin/env bash
#$ -cwd
#$ -l h_rt=24:00:00
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

input_dir=/wynton/scratch/guardado075/king_hap_ibd/large_fam_1000sims
vcf_file_gz="${input_dir}/largefam_${super_pop}_seed${SGE_TASK_ID}_snp_panel.vcf.gz"
vcf_file="${input_dir}/largefam_${super_pop}_seed${SGE_TASK_ID}_snp_panel.vcf"

# Now we will run hap ibd for each indiv part of the genome
map_file=/wynton/group/hernandez/guardado075/hapibd/map_files/plink.GRCh38.full.FixCHR.map
out_file=~/rohlfs_lab/igg_prelim/king_hap_ibd/large_fam_1000sims/results/hap_ibd_v3_snp_panel/large_fam_${super_pop}_seed${SGE_TASK_ID}_snp_panel

bcftools view $vcf_file_gz -Ov -o $vcf_file


hap-ibd \
  gt="$vcf_file" \
  map="$map_file" \
  out="$out_file"