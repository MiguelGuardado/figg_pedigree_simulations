#!/bin/env bash
#$ -cwd
#$ -l h_rt=24:00:00
#$ -l mem_free=15G
#$ -t 1-1000

module load CBI r plink bcftools miniforge3
conda activate py_ped_sim_clean

# Inputs: Superpopulation Label
while getopts s: flag
do
    case "${flag}" in
        s) super_pop=${OPTARG};;
    esac
done

input_dir=/wynton/scratch/guardado075/king_hap_ibd/large_fam_1000sims
vcf_input="${input_dir}/largefam_${super_pop}_seed${SGE_TASK_ID}_merged_genomes.vcf.gz"
vcf_output="${input_dir}/largefam_${super_pop}_seed${SGE_TASK_ID}_snp_panel.vcf"
bed_output="${input_dir}/largefam_${super_pop}_seed${SGE_TASK_ID}_snp_panel"
snp_panel="input_data/compass_hg38_subsetfile.txt" 

bcftools index ${vcf_input}

# Output regular VCF file
bcftools view -R $snp_panel ${vcf_input} -Ov -o ${vcf_output}

# Output compressed VCF file
bcftools view -R $snp_panel ${vcf_input} -Oz -o ${vcf_output}.gz
bcftools index ${vcf_output}.gz

# Output BED file
plink --vcf ${vcf_output} --make-bed --out ${bed_output}
