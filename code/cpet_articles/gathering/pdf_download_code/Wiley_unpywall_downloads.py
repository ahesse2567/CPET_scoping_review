import requests
import pandas as pd
import requests
from unpywall.utils import UnpywallCredentials
from unpywall import Unpywall

UnpywallCredentials('hesse151@umn.edu')

articles = pd.read_csv('/Users/antonhesse/Desktop/Anton/Education/UMN/Lab and Research/HSPL/CPET_scoping_review/data/cpet_articles/unpaywall/unpaywall_info.csv')
wiley_articles = articles[(articles['is_oa'] == False) & \
    (articles['publisher'] == 'Wiley')].reset_index(drop=True) # & \ # 
    #     (articles['status_code'] == '503')].reset_index(drop=True)
wiley_articles.shape
# find download urls
crossref_headers = {'Accept': 'application/vnd.citationstyles.csl+json, application/vnd.crossref.unixref+xml'}
doi_url = wiley_articles.loc[0,'doi_url']
crossref_response = requests.get(url = doi_url, headers=crossref_headers, allow_redirects=True, verify=False)
crossref_response.status_code

# crossref_response.json().keys()
# for k, v in crossref_response.json().items():
#     print(k, ': ', v)

# crossref_response.content # is the wiley api somewhere in here?
crossref_response.json()['link']
pdf_url = crossref_response.json()['link'][0]['URL']
pdf_url

# trying with Crossref_response.url
token = '08932ce3-df43-4685-b8ac-fa5f692bc235'
# url = Unpywall.get_pdf_link(doi = wiley_articles.loc[0,'first_oa_location.url_for_pdf'])
headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:100.0) Gecko/20100101 Firefox/100.0',
    'Wiley-TDM-Client-Token': token,
    'CR-TDM-Rate-Limit': '5' ,
    'CR-TDM-Rate-Limit-Remaining': '4',
    'CR-TDM-Rate-Limit-Reset': '1375427514'
    }
response = requests.get(crossref_response.url, headers = headers, allow_redirects=True, verify=False)
response # response 406

# trying with dx.doi from Crossref
url = crossref_response.json()['URL']
response = requests.get(url, headers=headers, allow_redirects=True)
response # 503....

# trying with 'best_oa_location.url_for_pdf'
url = wiley_articles.loc[0, 'first_oa_location.url_for_pdf']
response = requests.get(url, headers=headers)
response # still getting 503

# trying with doi_url
url = wiley_articles.loc[0,'doi_url']
response = requests.get(url, headers=headers, allow_redirects=True)
response # 503

url = wiley_articles.loc[0, 'first_oa_location.url_for_pdf']
url = Unpywall.get_pdf_link(url)
response = requests.get(url, headers=headers, allow_redirects=True)
response # 503...