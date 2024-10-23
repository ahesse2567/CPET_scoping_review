import pandas as pd

ovid_records = pd.read_csv('/Users/antonhesse/Desktop/Anton/Education/UMN/PhD/Dissertation/CPET_scoping_review/data/cpet_articles/database_search/ovid/doi_merged_ovid.csv')
scopus_records = pd.read_csv('/Users/antonhesse/Desktop/Anton/Education/UMN/PhD/Dissertation/CPET_scoping_review/data/cpet_articles/database_search/scopus/scopus_records_tidy.csv')
wos_records = pd.read_csv('/Users/antonhesse/Desktop/Anton/Education/UMN/PhD/Dissertation/CPET_scoping_review/data/cpet_articles/database_search/web_of_science/web_of_science_records_tidy.csv')

doi_df = pd.concat([ovid_records['doi'], scopus_records['doi'], wos_records['doi']])
doi_df = doi_df.drop_duplicates().dropna().reset_index(drop=True)

doi_df.to_csv('/Users/antonhesse/Desktop/Anton/Education/UMN/PhD/Dissertation/CPET_scoping_review/data/cpet_articles/dois_combined.csv',\
    index=False)