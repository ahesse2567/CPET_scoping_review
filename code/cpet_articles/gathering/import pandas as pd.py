import pandas as pd
from unpywall.utils import UnpywallCredentials
from unpywall import Unpywall

articles = pd.read_csv('/Users/antonhesse/Desktop/Anton/Education/UMN/Lab and Research/HSPL/CPET_data_analysis/data/cpet_articles/ovid/unpaywall_info.csv')
oa_articles = articles[articles['is_oa'] == True].reset_index(drop=True)

UnpywallCredentials('hesse151@umn.edu')

Unpywall.download_pdf_file(doi = oa_articles.doi_url[0], filename=oa_articles.title[0]+'.pdf')