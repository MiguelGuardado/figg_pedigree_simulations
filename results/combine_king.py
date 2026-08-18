import pandas as pd
import numpy as np

large_fam_rels = pd.read_csv('../input_data/large_family_012326_rel.csv')

king_coef_results = []
king_seg_results = []

for pop in ['afr', 'eur', 'amr', 'eas', 'sas']:

    for seed in range(1, 1001):
        print(f"Processing pop: {pop}, seed: {seed}...")

        king_path = f'king_full/large_fam_{pop}_seed{seed}.kin0'
        king_seg_path = f'king_full/large_fam_{pop}_seed{seed}.seg'
        #ibis_path = f'ibis_full/largefam_{pop}_seed{seed}.coef'


        king = pd.read_csv(king_path, sep='\t')
        king_seg = pd.read_csv(king_seg_path, sep='\t')
       

        # Convert ibis IDs from "N:N" to integer N
        #ibis['Individual1'] = ibis['Individual1'].astype(str).str.split(':').str[0].astype(int)
        #ibis['Individual2'] = ibis['Individual2'].astype(str).str.split(':').str[0].astype(int)

        # Merge with KING and IBIS
        king_merged = pd.merge(
            large_fam_rels,
            king,
            on=['ID1', 'ID2'],
            how='inner'
        )

        king_seg_merged = pd.merge(
                    large_fam_rels,
                    king_seg,
                    on=['ID1', 'ID2'],
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

        king_merged['pop'] = pop
        king_merged['seed'] = seed

        king_seg_merged['pop'] = pop
        king_seg_merged['seed'] = seed

        king_coef_results.append(king_merged)
        king_seg_results.append(king_seg_merged)

# Combine all seeds into one dataframe
king_coef_results = pd.concat(king_coef_results, ignore_index=True)
king_seg_results = pd.concat(king_seg_results, ignore_index=True)

king_coef_results.to_csv('king_full_summary/king_full_kinship_results.csv', index=False)
king_seg_results.to_csv('king_full_summary/king_full_segment_results.csv', index=False)