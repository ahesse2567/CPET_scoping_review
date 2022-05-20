import pandas as pd
import os
os.getcwd()

scopus_output = pd.read_csv('/Users/antonhesse/Desktop/Anton/Education/UMN/Lab and Research/HSPL/CPET_scoping_review/data/cpet_articles/scopus/scopus_records_combined.csv')
scopus_output.columns
scopus_output = scopus_output[['authors', 'title', 'source_title', 'doi', 'eid']]
scopus_output = scopus_output.drop_duplicates()
scopus_output = scopus_output.reset_index(drop=True)

scopus_output.to_csv('/Users/antonhesse/Desktop/Anton/Education/UMN/Lab and Research/HSPL/CPET_scoping_review/data/cpet_articles/scopus/scopus_records_tidy.csv',\
    index=False)
