import pandas as pd

wos_records = pd.read_csv('/Users/antonhesse/Desktop/Anton/Education/UMN/Lab and Research/HSPL/CPET_scoping_review/data/cpet_articles/web_of_science/web_of_science_records_tidy.csv')
id_df = pd.read_csv('/Users/antonhesse/Desktop/Anton/Education/UMN/Lab and Research/HSPL/CPET_scoping_review/data/cpet_articles/web_of_science/wos_pmc_conv.csv')

wos_records = wos_records.rename(columns={'pubmed_id': 'pmid'})

merged_df = wos_records.merge(id_df, on='pmid', how='outer', indicator=True)
merged_df['_merge'].value_counts()

print(len(merged_df[merged_df['_merge'] == 'both']), 'rows with DOI added from id_df')
merged_df[merged_df['_merge'] == 'both'] #merged_df will include all rows from both df

# From Cody H: This loop copies the value of the doi column over to doi_clean in
# any rows where doi_clean is null and doi is not:
def my_function():
    for i, row in merged_df.iterrows():
        if pd.notnull(row['doi_y']) and pd.isnull(row['doi_x']):
            merged_df.loc[i, 'doi_x'] = row['doi_y']
            
my_function()

merged_df = merged_df.drop('doi_y', axis=1)
merged_df = merged_df.rename(columns={'doi_x': 'doi'})

merged_df.to_csv('/Users/antonhesse/Desktop/Anton/Education/UMN/Lab and Research/HSPL/CPET_scoping_review/data/cpet_articles/web_of_science/wos_doi_merged.csv',\
    index=False)
