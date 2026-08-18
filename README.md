# large_fam_1000sims

Simulation and relatedness-inference pipeline for the large-family arm of the
forensic genetic-ancestry (IGG) project. The workflow simulates whole-genome
data for a fixed large-family pedigree across 1000 Genomes reference
populations, then estimates pairwise relatedness on the simulated genomes with
four independent methods (KING, IBIS, hap-ibd, and hierfstat) so their accuracy
can be compared across genetic ancestries.

All of the `run_*.sh` scripts are **SGE array jobs** written for the Wynton HPC
cluster (`#$ -t` sets the task range, `#$ -l` requests runtime/memory, and
`module load` / `conda activate` set up the environment). The genome simulation
itself is driven by [`py_ped_sim`](https://github.com/MiguelGuardado/py_ped_sim)
(`run_ped_sim.py` in `~/bin`), and the relatedness tools (`king`, `ibis`,
`hap-ibd`, `plink2`) are installed under `~/bin`.

Most paths in these scripts are specific to the author's Wynton scratch/group
space and will need to be edited to run elsewhere.

## Pipeline overview

```
run_simulations_largefam_1000sims.sh    # 1. simulate genomes per (population, seed, chromosome)
            │
            ▼
run_king.sh        # 2a. merge the 22 per-chromosome VCFs, then run KING
run_ibis.sh        # 2b. run IBIS on the merged genotypes
run_hap_ibd.sh     # 2c. run hap-ibd on the merged VCF
run_hierfstat.sh   # 2d. run hierfstat (R) on the merged VCF
```

Stage 1 produces one VCF per population/seed/chromosome. `run_king.sh` is what
concatenates those per-chromosome files into the merged VCF and PLINK `.bed`
that the other three inference scripts consume, so it generally needs to run
first. Stages 2a–2d are otherwise independent of one another. The
seed-numbered array tasks (`SGE_TASK_ID`, 1–100) correspond to independent
simulation replicates, and `-s` selects the 1000 Genomes superpopulation.

## Scripts

### `run_simulations_largefam_1000sims.sh`

The simulation entry point, and the largest job (an array of up to 110,000
tasks). For each task it reads one line from `input_data/job_id_1000sims.txt`,
parsing the columns into `JOB`, `POP` (population), `SEED`, and `CHR`
(chromosome). It then calls `py_ped_sim`'s `run_ped_sim.py` in
`sim_genomes_exact` mode to drop the large-family pedigree
(`input_data/large_family_012326.nx`) onto a 1000 Genomes reference VCF for that
population and chromosome, using the matching recombination map and a mutation
rate of `1e-7`, to produce simulated genomes. Simulation is wrapped in a retry
loop (up to `MAX_RETRIES=100`) that re-attempts until the expected
`*_genomes.vcf` is written, cleaning up and pausing between tries, so transient
failures on the cluster don't lose a task.

### `run_king.sh`

Merge step plus KING relatedness. Takes a superpopulation with `-s` and uses
`SGE_TASK_ID` as the replicate seed. It first uses `bcftools concat` to combine
the 22 per-chromosome simulated VCFs into a single merged VCF, then `plink
--make-bed` to convert that into PLINK binary format. It then runs **KING**
(`king -b … --kinship --ibdseg`) to estimate kinship coefficients and infer IBD
segments for every pair of individuals. Results are written under
`results/king_full/`. Because this script creates the merged VCF/`.bed`, it is
effectively a prerequisite for the IBIS and hap-ibd scripts.

### `run_ibis.sh`

Runs **IBIS** to detect IBD segments and estimate relatedness on the merged
genotypes. It sets variant IDs to `chr:pos` with `plink2 --set-all-var-ids`,
appends genetic-map (cM) positions to the `.bim` using IBIS's
`add-map-plink.pl` and `input_data/genetic_map_hg38_withX.txt`, drops SNPs that
have no map position, and then runs `ibis` with segment-detection parameters
(`-min_l 7 -mt 500 -er .004 -printCoef`). Output goes to `results/ibis_full/`.
Note: this script deliberately uses a non-AVX2 `plink2` build from `~/bin` so it
runs on Wynton's older SSE4.2-only nodes rather than crashing.

### `run_hap_ibd.sh`

Runs **hap-ibd** (in the `hapibd` conda environment) to detect
identity-by-descent segments from the merged, phased VCF
(`…_merged_genomes.vcf.gz`), using the GRCh38 PLINK genetic map. Selected by `-s`
(superpopulation) and `SGE_TASK_ID` (seed). Output is written to
`results/hap_ibd_full/`.

### `run_hierfstat.sh`

Estimates kinship / F-statistics with **hierfstat** in R. It converts the merged
VCF to uncompressed form with `bcftools view`, then calls an R script
(`estimate_kinship.R`) on the resulting VCF. Selected by `-s` and
`SGE_TASK_ID`. Note that this script currently points at a different input
directory (`large_fam_hap_map_re6_scale`) and output path than the other three,
so its paths may need reconciling before a coordinated run.

## Inputs

Key files under `input_data/` used by these scripts:

- `job_id_1000sims.txt` — task table (`JOB POP SEED CHR` per line) driving the simulation array.
- `large_family_012326.nx` — the large-family pedigree structure simulated by `py_ped_sim`.
- `genetic_map_hg38_withX.txt` — genetic map used by IBIS to add cM positions.

## A note on data files

Large reference and result files (the genetic map, the merged/per-run VCFs, and
the KING/IBIS/hap-ibd/hierfstat result CSVs) are **not tracked in this
repository** because they exceed GitHub's file-size limits. They are regenerated
by running the pipeline above, or can be available upon request. 
