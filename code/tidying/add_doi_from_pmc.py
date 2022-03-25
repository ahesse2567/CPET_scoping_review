import pandas as pd
import numpy as np

ovid_output = pd.read_csv('/Users/antonhesse/Desktop/Anton/Education/UMN/Lab and Research/HSPL/CPET_data_analysis/data/processed/ovid_export_tidy.csv')
# id_intersect = pd.crosstab(id_df['pmcid'], ovid_output['pmc_clean']) > 0
# id_intersect.to_csv("/Users/antonhesse/Desktop/Anton/Education/UMN/Lab and Research/HSPL/CPET_data_analysis/data/raw/id_intersect.csv",\
#     index = True)
id_df = pd.read_csv('/Users/antonhesse/Desktop/Anton/Education/UMN/Lab and Research/HSPL/CPET_data_analysis/data/raw/pmc_conv.csv')

for i in range(len(id_df)):
    idx = np.where(ovid_output['pmc_clean'] == id_df.loc[i,'pmcid'])
    ovid_doi = ovid_output.loc[idx,'doi_clean'].values[0]
    id_df_doi = id_df.loc[i,'doi']
    if ovid_output.loc[idx,'doi_clean'].isnull().values[0] & (ovid_doi != id_df_doi):
        if ovid_output.loc[idx,'doi_clean'].isna().bool():
            ovid_output.loc[idx,'doi_clean'].fillna(id_df_doi, inplace=True) # not saving for some reason
        else:
            ovid_output.loc[idx,'doi_clean'] = id_df_doi
        print(f'i = {i}\nindex = {idx}')
        
ovid_output.to_csv('/Users/antonhesse/Desktop/Anton/Education/UMN/Lab and Research/HSPL/CPET_data_analysis/data/processed/ovid_output_pmc_doi.csv')