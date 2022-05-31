import requests
import pandas as pd
import requests
# from unpywall.utils import UnpywallCredentials
# from unpywall import Unpywall
import json
from tqdm import tqdm

articles = pd.read_csv('/Users/antonhesse/Desktop/Anton/Education/UMN/Lab and Research/HSPL/CPET_scoping_review/data/cpet_articles/unpaywall/unpaywall_info.csv')
bmj_non_oa_articles = articles[(articles['is_oa'] == False) & \
    (articles['publisher'] == 'BMJ')].reset_index()

bmj_non_oa_articles.shape

crossref_headers = {
    'Accept': 'application/vnd.citationstyles.csl+json, application/vnd.crossref.unixref+xml',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:100.0) Gecko/20100101 Firefox/100.0'
    }

doi_url = 'http://dx.doi.org/10.5555/515151' # test url from crossref
# doi_url = bmj_non_oa_articles.loc[0, 'doi_url']
doi_url

crossref_response = requests.get(url = doi_url, headers=crossref_headers, allow_redirects=True)
# crossref_response.json().keys()
# for k, v in crossref_response.json().items():
#     print(k, ': ', v)

crossref_response.json()['link']
pdf_url = crossref_response.json()['link'][0]['URL']
pdf_url

# for k in crossref_response.json().keys():
#     print(k)

license = crossref_response.json()['license']
license_url = crossref_response.json()['license'][1]['URL']
license_url

pdf_headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:100.0) Gecko/20100101 Firefox/100.0',
    'Content-Type': 'application/pdf'
    }
pdf_response = requests.get(url = pdf_url, headers=pdf_headers, verify=False, allow_redirects=True)
pdf_response # currently getting 404 error

# -k: verify=False
# -L: allow_redirections=True
# -O: write file based on what's returned from the request. -o lets you choose the output file name
# -D, --dump-header <filename> puts headers into file name(?)
'''
headers to include. See https://curl.se/docs/manpage.html#-D for details
CR-TDM-Client-Token
CR-TDM-Rate-Limit
CR-TDM-Rate-Limit-Reset
X-Content-Type-Options
Last-Modified
GMT Status
Content-Length
Content-Type: application/pdf
'''