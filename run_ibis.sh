#!/bin/env bash
#$ -cwd  # use current working directory
#$ -l h_rt=300:00:00  # The scheduler knows that the job to run no longer than 20 minutes allowing it to be scheduled much sooner than if no run-time was specified
#$ -l mem_free=10G  #  the job will be allotted 10 GiB of RAM per slot
#$ -t 1-100  # Requesting the 1000 jobs to be preformed for this script

## This code is to be used on wynton, where each job run in parralel for each individual family.
## NOTE: We no longer load the CBI plink2 module. That module ships an AVX2 build that
## crashes on Wynton's older (SSE4.2-only) nodes. Instead we use the plain non-AVX2
## plink2 binary in ~/bin, which runs on every node. Node/scheduler settings are unchanged.
module load CBI scl-gcc-toolset/12

# Path to the non-AVX2 plink2 build (downloaded once from plink2-assets).
PLINK2=~/bin/plink2

# Inputs: Superpopulation Label
while getopts s: flag
do
    case "${flag}" in
        s) super_pop=${OPTARG};;
    esac
done

input_dir=/wynton/scratch/guardado075/king_hap_ibd/large_fam_1000sims
bed_file="${input_dir}/largefam_${super_pop}_seed${SGE_TASK_ID}_merged_genomes"
output_prefix=~/rohlfs_lab/igg_prelim/king_hap_ibd/large_fam_1000sims/results/ibis_full/large_fam_${super_pop}_seed${SGE_TASK_ID}


# Run plink2 command to add id to bim file based on chr and pos
$PLINK2 --bfile $bed_file --set-all-var-ids @:# --make-bed --out ${bed_file}_newid

# Add genetic map to bim file
~/bin/ibis/add-map-plink.pl ${bed_file}_newid.bim input_data/genetic_map_hg38_withX.txt > ${bed_file}_with_map.bim

# Now remove snps with missing map positions (i.e. those that were not in the genetic map)
awk '$3==0 {print $2}' ${bed_file}_with_map.bim > snps_to_remove_${super_pop}_seed${SGE_TASK_ID}.txt

# Use plink to remove these snps from original bed file and create new bed file with map positions
$PLINK2 --bfile ${bed_file}_newid --exclude snps_to_remove_${super_pop}_seed${SGE_TASK_ID}.txt --make-bed --out ${bed_file}_cleaned

# Finally remove map positions from bim file with genetic positions and replace the bim file in the subsetted version
 awk '$3!=0' ${bed_file}_with_map.bim > ${bed_file}_cleaned.bim

# Run IBIS
~/bin/ibis/ibis -bfile ${bed_file}_cleaned -min_l 7 -mt 500 -er .004 -printCoef -f $output_prefix

## End-of-job summary, if running as a job
[[ -n "$JOB_ID" ]] && qstat -j "$JOB_ID"  # This is useful for debugging and usage purposes,
                                          # e.g. "did my job exceed its memory request?"