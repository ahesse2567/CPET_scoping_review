import pandas as pd
import os
os.getcwd()

ovid_output = pd.read_csv('/Users/antonhesse/Desktop/Anton/Education/UMN/Lab and Research/HSPL/CPET_scoping_review/data/cpet_articles/ovid/ovid_records_combined.csv')
ovid_output = ovid_output.drop(['ORN', 'VN', 'DB', 'XL'], axis = 1)
ovid_output = ovid_output.drop_duplicates()
ovid_output = ovid_output.reset_index(drop=True)
ovid_output['pmc_clean'] = ovid_output.PM.str.replace('https://www.ncbi.nlm.nih.gov/pmc/articles/','')
ovid_output['doi_clean'] = ovid_output.DO.str.replace('https://dx.doi.org/', '')

ovid_output.to_csv('/Users/antonhesse/Desktop/Anton/Education/UMN/Lab and Research/HSPL/CPET_scoping_review/data/cpet_articles/ovid/ovid_export_tidy.csv',\
    index=False)
