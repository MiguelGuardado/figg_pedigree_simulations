import pandas as pd
import numpy as np

## add comments please?
## This script combines the results from multiple simulations (1000 seeds) for different populations (afr, amr, eas, eur, sas) using various methods (king, hap_ibd, ibis).
## It reads the input data, processes each seed, merges the results with the large family relationships, and saves the combined results to CSV files.

large_fam_rels = pd.read_csv('../input_data/large_family_012326_rel.csv')

king_coef_results = []
king_seg_results = []
hap_ibd_results = [] 
ibis_seg_results = []
ibis_coef_results = []


for pop in ['afr', 'amr', 'eas', 'eur', 'sas']:
    for i in range(1, 1001):
        king_coef = pd.read_csv(f'king_v3_snp_panel/large_fam_{pop}_seed{i}_snp_panel.kin0', sep='\t')
        king_seg = pd.read_csv(f'king_v3_snp_panel/large_fam_{pop}_seed{i}_snp_panel.seg', sep='\t')

        hap_ibd = pd.read_csv(f'hap_ibd_v3_snp_panel/large_fam_{pop}_seed{i}_snp_panel.ibd.gz', sep='\t')
        hap_ibd.columns = ['ID1','ID1_H', 'ID2', 'ID2_H', 'Chr', 'Start', 'Stop', 'CM_Length']
        
        ibis_seg = pd.read_csv(f'ibis_v3_snp_panel/large_fam_{pop}_seed{i}_snp_panel.seg', sep='\t', header=None)
        ibis_seg.columns = ['Individual1', 'Individual2', 'Chrom', 'Phys_Start', 'Phys_End', 'IBD_Type', 'Genetic_Start', 'Genetic_End', 'Genetic_Seg_Length', 'Marker_Count', 'Error_Count', 'Error_Density']

        ibis_seg['Individual1'] = ibis_seg['Individual1'].astype(str).str.split(':').str[0].astype(int)
        ibis_seg['Individual2'] = ibis_seg['Individual2'].astype(str).str.split(':').str[0].astype(int)

        ibis_coef = pd.read_csv(f'ibis_v3_snp_panel/large_fam_{pop}_seed{i}_snp_panel.coef', sep='\t')

        ibis_coef['Individual1'] = ibis_coef['Individual1'].astype(str).str.split(':').str[0].astype(int)
        ibis_coef['Individual2'] = ibis_coef['Individual2'].astype(str).str.split(':').str[0].astype(int)


        # Merge with large_fam_rels 

        king_coef_merged = pd.merge(
            large_fam_rels,
            king_coef,
            on=['ID1', 'ID2'],
            how='inner'
         )

        king_seg_merged = pd.merge(
                    large_fam_rels,
                    king_seg,
                    on=['ID1', 'ID2'],
                    how='inner'
                )

        hap_ibd_merged = pd.merge(
                    large_fam_rels,
                    hap_ibd,
                    on=['ID1', 'ID2'],
                     how='inner')

        ibis_seg_merged = pd.merge(
                large_fam_rels,
                ibis_seg,
                left_on=['ID1', 'ID2'],
                right_on=['Individual1', 'Individual2'],
                how='inner'
            )

        ibis_coef_merged = pd.merge(
                large_fam_rels,
                ibis_coef,
                left_on=['ID1', 'ID2'],
                right_on=['Individual1', 'Individual2'],
                how='inner'
            )

        king_coef_merged['pop'] = pop
        king_seg_merged['pop'] = pop
        hap_ibd_merged['pop'] = pop
        ibis_seg_merged['pop'] = pop
        ibis_coef_merged['pop'] = pop

        king_coef_merged['seed'] = i
        king_seg_merged['seed'] = i
        hap_ibd_merged['seed'] = i
        ibis_seg_merged['seed'] = i
        ibis_coef_merged['seed'] = i

        king_coef_results.append(king_coef_merged)
        king_seg_results.append(king_seg_merged)
        hap_ibd_results.append(hap_ibd_merged)
        ibis_seg_results.append(ibis_seg_merged)
        ibis_coef_results.append(ibis_coef_merged)


# Combine all seeds into one dataframe
king_coef_results = pd.concat(king_coef_results, ignore_index=True)
king_seg_results = pd.concat(king_seg_results, ignore_index=True)
hap_ibd_results = pd.concat(hap_ibd_results, ignore_index=True)
ibis_seg_results = pd.concat(ibis_seg_results, ignore_index=True)
ibis_coef_results = pd.concat(ibis_coef_results, ignore_index=True)

king_coef_results.to_csv('king_snp_panel_kinship_results.csv', index=False)
king_seg_results.to_csv('king_snp_panel_segment_results.csv', index=False)
hap_ibd_results.to_csv('hap_ibd_snp_panel_results.csv', index=False)
ibis_seg_results.to_csv('ibis_snp_panel_segment_results.csv', index=False)
ibis_coef_results.to_csv('ibis_snp_panel_kinship_results.csv', index=False)