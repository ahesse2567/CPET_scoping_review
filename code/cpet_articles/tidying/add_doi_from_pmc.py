import pandas as pd
import numpy as np

ovid_output = pd.read_csv('/Users/antonhesse/Desktop/Anton/Education/UMN/Lab and Research/HSPL/CPET_data_analysis/data/cpet_articles/ovid_export_tidy.csv')
# id_intersect = pd.crosstab(id_df['pmcid'], ovid_output['pmc_clean']) > 0
# id_intersect.to_csv("/Users/antonhesse/Desktop/Anton/Education/UMN/Lab and Research/HSPL/CPET_data_analysis/data/raw/id_intersect.csv",\
#     index = True)
id_df = pd.read_csv('/Users/antonhesse/Desktop/Anton/Education/UMN/Lab and Research/HSPL/CPET_data_analysis/data/cpet_articles/pmc_conv.csv')

#change the name of the pmc id column so that it's the same in both dfs.
ovid_output = ovid_output.rename(columns={'pmc_clean': 'pmcid'})

#merge matching on pmcid; indicator=True creates a new column that shows you if pmcid is found in "both" columns, "left_only", or "right_only"
merged_df = ovid_output.merge(id_df, on='pmcid', how='outer', indicator=True)

#show the rows where a DOI from id_df was added
print(len(merged_df[merged_df['_merge'] == 'both']), 'rows with DOI added from id_df')
merged_df[merged_df['_merge'] == 'both'] #merged_df will include all rows from both dfs

# From Cody H: This loop copies the value of the doi column over to doi_clean in
# any rows where doi_clean is null and doi is not:
def my_function():
    for i, row in merged_df.iterrows():
        if pd.notnull(row['doi']) and pd.isnull(row['doi_clean']):
            merged_df.loc[i, 'doi_clean'] = row['doi']
            

my_function()

merged_df.to_csv('/Users/antonhesse/Desktop/Anton/Education/UMN/Lab and Research/HSPL/CPET_data_analysis/data/cpet_articles/doi_merged.csv',\
    index=False)
