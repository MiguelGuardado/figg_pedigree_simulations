#!/bin/env bash
#$ -cwd  # use current working directory
#$ -l h_rt=300:00:00  # The scheduler knows that the job to run no longer than 20 minutes allowing it to be scheduled much sooner than if no run-time was specified
#$ -l mem_free=10G  #  the job will be allotted 10 GiB of RAM per slot
#$ -t 1-100  # Requesting the 1000 jobs to be preformed for this script

module load CBI r/4.0

# Inputs: Superpopulation Label  
while getopts s: flag
do
    case "${flag}" in
        s) super_pop=${OPTARG};;
    esac
done

input_dir=/wynton/scratch/guardado075/king_hap_ibd/large_fam_hap_map_re6_scale/ 
vcf_file="${input_dir}/largefam_${super_pop}_seed${SGE_TASK_ID}_merged_genomes.vcf.gz"
vcf_file_unc="${input_dir}/largefam_${super_pop}_seed${SGE_TASK_ID}_merged_genomes.vcf"
output_filename=~/rohlfs_lab/igg_prelim/king_hap_ibd/large_family_simulations/results/hapmap_v6/hierfstat/largefam_${super_pop}_seed${SGE_TASK_ID}_merged_genomes

bcftools view $vcf_file -Ov -o $vcf_file_unc

Rscript python_scripts/estimate_kinship.R $vcf_file_unc ${SGE_TASK_ID}