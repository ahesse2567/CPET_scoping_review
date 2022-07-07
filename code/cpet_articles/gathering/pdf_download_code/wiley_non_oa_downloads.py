import requests
import pandas as pd
import json
from tqdm import tqdm
import sys
sys.path.append('code/cpet_articles/gathering/pdf_download_code')
from crossref_pdf_download import crossref_pdf_download

with open('code/cpet_articles/gathering/pdf_download_code/wiley_config.json') as config_file:
    wiley_token = json.load(config_file)['api_key']

articles = pd.read_csv('/Users/antonhesse/Desktop/Anton/Education/UMN/Lab and Research/HSPL/CPET_scoping_review/data/cpet_articles/unpaywall/unpaywall_info.csv')
wiley_articles = articles[(articles['is_oa'] == False) & \
    (articles['publisher'] == 'Wiley')].reset_index(drop=True) # & \ # 
    #     (articles['status_code'] == '503')].reset_index(drop=True)
wiley_articles.shape

accept = 'application/vnd.citationstyles.csl+json, application/vnd.crossref.unixref+xml'
user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:101.0) Gecko/20100101 Firefox/101.0'
crossref_headers = {
    'Accept': 'application/vnd.citationstyles.csl+json, application/vnd.crossref.unixref+xml',
    'User-Agent': user_agent
}

folder = '/Users/antonhesse/Desktop/Anton/Education/UMN/Lab and Research/HSPL/CPET_scoping_review/data/cpet_articles/pdfs/wiley_non_oa_pdfs'

res = []
for i, row in tqdm(wiley_articles.iterrows(), total=wiley_articles.shape[0]):
    temp = crossref_pdf_download(
        doi=row['doi'],
        accept=accept,
        dest=folder,
        user_agent=user_agent,
        TDM_header='Wiley-TDM-Client-Token',
        TDM_token=wiley_token,
        verify=True)
    res.append(temp)

res_df = pd.DataFrame(res)
merge = pd.merge(wiley_articles, res_df, how = 'outer', on='doi')
merge['publisher_status_code'].value_counts() # most are NOT status code 200
# merge.to_csv('data/cpet_articles/unpaywall/wiley_non_oa_status_codes.csv', index=False)

"""
I'm able to manually download articles with status code 500, 503, 404, 403, and 400
Therefore, I think there might be problem on Wiley's end?
"""