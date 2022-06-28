import pandas as pd

ovid_records = pd.read_csv('/Users/antonhesse/Desktop/Anton/Education/UMN/Lab and Research/HSPL/CPET_scoping_review/data/cpet_articles/ovid/doi_merged_ovid.csv')
scopus_records = pd.read_csv('/Users/antonhesse/Desktop/Anton/Education/UMN/Lab and Research/HSPL/CPET_scoping_review/data/cpet_articles/scopus/scopus_records_tidy.csv')
wos_recoreds = pd.read_csv('/Users/antonhesse/Desktop/Anton/Education/UMN/Lab and Research/HSPL/CPET_scoping_review/data/cpet_articles/web_of_science/web_of_science_records_tidy.csv')

doi_df = pd.concat([ovid_records['doi'], scopus_records['doi'], wos_recoreds['doi']])
doi_df = doi_df.drop_duplicates().dropna().reset_index(drop=True)

doi_df.to_csv('/Users/antonhesse/Desktop/Anton/Education/UMN/Lab and Research/HSPL/CPET_scoping_review/data/cpet_articles/dois_combined.csv',\
    index=False)