import sys
sys.path.append('code/cpet_articles/gathering/pdf_download_code')
from crossref_pdf_download import crossref_pdf_download
import pandas as pd
from tqdm import tqdm
import json

articles = pd.read_csv('data/cpet_articles/unpaywall/unpaywall_info.csv')
cdn = articles[(articles['is_oa'] == False) & \
    (articles['publisher'] == 'Canadian Science Publishing')].reset_index(drop=True)
cdn.shape

user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:101.0) Gecko/20100101 Firefox/101.0'
accept = 'application/vnd.citationstyles.csl+json, application/vnd.crossref.unixref+xml'
dest_folder = 'data/cpet_articles/pdfs/cdn_non_oa_pdfs'

with open('code/cpet_articles/gathering/pdf_download_code/crossref_config.json') as config_file:
    crossref_token = json.load(config_file)['api_key']

test_doi = cdn.loc[0,'doi']
test_doi

crossref_pdf_download(doi=test_doi, accept=accept, dest=dest_folder, user_agent=user_agent,verify=True)

# res = []
# for i, row in tqdm(cdn.iterrows(), total=cdn.shape[0]):
#     temp = crossref_pdf_download(
#         doi=row['doi'],
#         accept=accept,
#         dest=dest_folder,
#         user_agent=user_agent,
#         verify=True)
#     res.append(temp)