import sys
sys.path.append('code/cpet_articles/gathering/pdf_download_code')
from crossref_pdf_download import crossref_pdf_download
import pandas as pd
from tqdm import tqdm
import json

with open('code/cpet_articles/gathering/pdf_download_code/wiley_config.json') as config_file:
    wiley_token = json.load(config_file)['api_key']

articles = pd.read_csv('/Users/antonhesse/Desktop/Anton/Education/UMN/Lab and Research/HSPL/CPET_scoping_review/data/cpet_articles/unpaywall/unpaywall_info.csv')
wiley_articles = articles[(articles['is_oa'] == True) & \
    (articles['publisher'] == 'Wiley')].reset_index(drop=True)
wiley_articles.shape

user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:101.0) Gecko/20100101 Firefox/101.0'
accept = 'application/vnd.citationstyles.csl+json, application/vnd.crossref.unixref+xml'
dest_folder = 'data/cpet_articles/pdfs/wiley_oa_pdfs'

# uncomment below to redownload wiley oa articles
# res = []
# for i, row in tqdm(wiley_articles.iterrows(), total=wiley_articles.shape[0]):
#     temp = crossref_pdf_download(
#         doi=row['doi'],
#         accept=accept,
#         dest=dest_folder,
#         user_agent=user_agent,
#         TDM_header='Wiley-TDM-Client-Token',
#         TDM_token=wiley_token,
#         verify=True)
#     res.append(temp)

# res_df = pd.DataFrame(res)
# merge = pd.merge(wiley_articles, res_df, how = 'outer', on='doi')
# merge.columns
# merge['publisher_status_code'].value_counts() # most are NOT status code 200
# # merge.to_csv('data/cpet_articles/unpaywall/wiley_oa_status_codes.csv', index=False)

df_status_codes = pd.read_csv('data/cpet_articles/unpaywall/wiley_oa_status_codes.csv')
non200 = df_status_codes[df_status_codes['publisher_status_code'] != 200]
res2 = []
for i, row in tqdm(non200.iterrows(), total=non200.shape[0]):
    temp = crossref_pdf_download(
        doi=row['doi'],
        accept=accept,
        dest=dest_folder,
        user_agent=user_agent,
        application='pdf',
        TDM_header='Wiley-TDM-Client-Token',
        TDM_token=wiley_token,
        verify=True)
    res2.append(temp)