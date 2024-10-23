import pandas as pd

ovid_records = pd.read_csv('/Users/antonhesse/Desktop/Anton/Education/UMN/PhD/Dissertation/CPET_scoping_review/data/cpet_articles/database_search/ovid/ovid_records_tidy.csv')
# id_intersect = pd.crosstab(id_df['pmcid'], ovid_records['pmc_clean']) > 0
# id_intersect.to_csv("/Users/antonhesse/Desktop/Anton/Education/UMN/Lab and Research/HSPL/CPET_data_analysis/data/raw/id_intersect.csv",\
#     index = True)
id_df = pd.read_csv('/Users/antonhesse/Desktop/Anton/Education/UMN/PhD/Dissertation/CPET_scoping_review/data/cpet_articles/database_search/ovid/ovid_pmc_conv.csv')

#change the name of the pmc id coquitlumn so that it's the same in both dfs.
ovid_records = ovid_records.rename(columns={'pmc_clean': 'pmcid'})

#merge matching on pmcid; indicator=True creates a new column that shows you if pmcid is found in "both" columns, "left_only", or "right_only"
merged_df = ovid_records.merge(id_df, on='pmcid', how='outer', indicator=True)

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

merged_df = merged_df.drop('doi', axis=1)
merged_df = merged_df.rename(columns={'doi_clean': 'doi'})

merged_df.to_csv('/Users/antonhesse/Desktop/Anton/Education/UMN/PhD/Dissertation/CPET_scoping_review/data/cpet_articles/database_search/ovid/doi_merged_ovid.csv',\
    index=False)
