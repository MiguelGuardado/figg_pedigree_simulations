import pandas as pd
import numpy as np

large_fam_rels = pd.read_csv('../input_data/large_family_012326_rel.csv')

ibis_coef_results = []
ibis_seg_results = []
print(large_fam_rels.head())

for pop in ['afr', 'eur', 'amr', 'eas', 'sas']:

    for seed in range(1, 1001):
        print(f"Processing pop: {pop}, seed: {seed}...")

        ibis_path = f'ibis_full/large_fam_{pop}_seed{seed}.coef'
        ibis_seg_path = f'ibis_full/large_fam_{pop}_seed{seed}.seg'


        ibis = pd.read_csv(ibis_path, sep='\t')
        ibis_seg = pd.read_csv(ibis_seg_path, sep='\t', header=None)
        ibis_seg.columns = ['Individual1', 'Individual2', 'chrom', 'phys_start_pos', 'phys_end_pos', 'IBD_type', 
                            'genetic_start_pos', 'genetic_end_pos', 'genetic_seg_length', 'marker_count', 'error_count', 'error_density']
       

        # Convert ibis IDs from "N:N" to integer N
        ibis['Individual1'] = ibis['Individual1'].astype(str).str.split(':').str[0].astype(int)
        ibis['Individual2'] = ibis['Individual2'].astype(str).str.split(':').str[0].astype(int)

        ibis_seg['Individual1'] = ibis_seg['Individual1'].astype(str).str.split(':').str[0].astype(int)
        ibis_seg['Individual2'] = ibis_seg['Individual2'].astype(str).str.split(':').str[0].astype(int)


        # Merge with KING and IBIS
        ibis_merged = pd.merge(
            large_fam_rels,
            ibis,
            left_on=['ID1', 'ID2'],
            right_on=['Individual1', 'Individual2'],
            how='inner'
        )

        ibis_seg_merged = pd.merge(
                    large_fam_rels,
                    ibis_seg,
                    left_on=['ID1', 'ID2'],
                    right_on=['Individual1', 'Individual2'],
                    how='inner'
                )

        #ibis_merged = pd.merge(
        #    large_fam_rels,
        #    ibis,
        #    left_on=['ID1', 'ID2'],
        #     right_on=['Individual1', 'Individual2'],
        #    how='inner'
        #)


        # Build hierfstat kinship lookup table once per seed
        #hierfstat_kinship = []
        #for _, row in kinship_merged.iterrows():
        #    id1 = row['ID1']
        #    id2 = row['ID2']
        #    hierfstat_kinship.append(float(hierfstat.loc[id1][id2 - 1]))

        ibis_merged['pop'] = pop
        ibis_merged['seed'] = seed

        ibis_seg_merged['pop'] = pop
        ibis_seg_merged['seed'] = seed

        ibis_coef_results.append(ibis_merged)
        ibis_seg_results.append(ibis_seg_merged)

# Combine all seeds into one dataframe
ibis_coef_results = pd.concat(ibis_coef_results, ignore_index=True)
ibis_seg_results = pd.concat(ibis_seg_results, ignore_index=True)

ibis_coef_results.to_csv('ibis_full_summary/ibis_full_kinship_results.csv', index=False)
ibis_seg_results.to_csv('ibis_full_summary/ibis_full_segment_results.csv', index=False)