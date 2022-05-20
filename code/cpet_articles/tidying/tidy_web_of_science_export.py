import pandas as pd
import os
os.getcwd()

wos_output = pd.read_csv('/Users/antonhesse/Desktop/Anton/Education/UMN/Lab and Research/HSPL/CPET_scoping_review/data/cpet_articles/web_of_science/web_of_science_records_combined.csv')
wos_output.columns
wos_output = wos_output[['authors', 'article_title', 'source_title', 'issn', 'publication_year',\
    'doi', 'pubmed_id', 'ut_unique_wos_id']]
wos_output = wos_output.drop_duplicates()
wos_output = wos_output.reset_index(drop=True)

wos_output.to_csv('/Users/antonhesse/Desktop/Anton/Education/UMN/Lab and Research/HSPL/CPET_scoping_review/data/cpet_articles/web_of_science/web_of_science_records_tidy.csv',\
    index=False)
