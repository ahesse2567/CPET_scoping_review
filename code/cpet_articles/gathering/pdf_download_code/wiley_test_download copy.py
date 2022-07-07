from pytest import param
import requests
import pandas as pd
import json

with open('code/cpet_articles/gathering/pdf_download_code/wiley_config.json') as config_file:
    wiley_token = json.load(config_file)['api_key']

articles = pd.read_csv('/Users/antonhesse/Desktop/Anton/Education/UMN/Lab and Research/HSPL/CPET_scoping_review/data/cpet_articles/unpaywall/unpaywall_info.csv')
wiley_articles = articles[(articles['is_oa'] == False) & \
    (articles['publisher'] == 'Wiley')].reset_index(drop=True) # & \ # 

test_doi = wiley_articles.loc[0,'doi']
doi_url = 'http://dx.doi.org/' + test_doi
doi_url

crossref_metadata_headers = {
    'Accept': 'application/vnd.citationstyles.csl+json, application/vnd.crossref.unixref+xml',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:101.0) Gecko/20100101 Firefox/101.0'
}

crossref_response = requests.get(
    url = doi_url,
    headers=crossref_metadata_headers,
    allow_redirects=True,
    verify=True)
crossref_response.status_code
crossref_response.url

full_text_link = crossref_response.json()['link'][1]['URL']
full_text_link

wiley_params = {'Wiley-TDM-Client-Token': wiley_token}
wiley_headers = {
    # 'Wiley-TDM-Client-Token': wiley_token,
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:101.0) Gecko/20100101 Firefox/101.0',
}

wiley_response = requests.get(
    url = full_text_link,
    params=wiley_params,
    headers=wiley_headers,
    allow_redirects=True,
    verify=True)
wiley_response.status_code
# wiley_response.headers # use this for logging
folder = '/Users/antonhesse/Desktop/Anton/Education/UMN/Lab and Research/HSPL/CPET_scoping_review/data/cpet_articles/pdfs/wiley_oa_pdfs'
doi_suffix = str(test_doi.split('/')[1:]).strip("[']")

filename = f'{folder}/{doi_suffix}.pdf'

with open(filename, mode='wb') as f:
    f.write(wiley_response.content)