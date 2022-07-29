import requests
import json

doi = '10.1016/j.vph.2022.106978'
doi_url = 'https://api.elsevier.com/content/article/doi/' + doi

with open("code/cpet_articles/gathering/pdf_download_code/elsevier_config.json") as config_file:
    api_key = json.load(config_file)['apikey']

elsevier_params = {
    'apiKey': api_key,
    'httpAccept': 'text/xml',
    'view': 'FULL'
}
elsevier_headers ={
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:101.0) Gecko/20100101 Firefox/101.0'}

r = requests.get(url=doi_url, params=elsevier_params, headers=elsevier_headers,
    allow_redirects=True, verify=True)
r.status_code