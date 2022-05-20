import requests
import pandas as pd
import requests
# from unpywall.utils import UnpywallCredentials
# from unpywall import Unpywall
import json
import re

# UnpywallCredentials('hesse151@umn.edu')

articles = pd.read_csv('/Users/antonhesse/Desktop/Anton/Education/UMN/Lab and Research/HSPL/CPET_scoping_review/data/cpet_articles/ovid/unpaywall_info.csv')
springer_non_oa_articles = articles[(articles['is_oa'] == False) & \
    (articles['publisher'] == 'Springer Science and Business Media LLC')].reset_index()

with open('/Users/antonhesse/Desktop/Anton/Education/UMN/Lab and Research/HSPL/CPET_scoping_review/code/cpet_articles/gathering/springer_config.json') as config_file:
    api_key = json.load(config_file)['api_key']
api_key
# api_key = '94ac47d7af9676b7403b4694dcf058b0'

query = springer_non_oa_articles.loc[0,'doi']
query
params = {
    'api_key': api_key,
    'q': query
    }
params

springer_api_url = 'https://api.springernature.com/meta/v2/json?'
headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:100.0) Gecko/20100101 Firefox/100.0'}

response = requests.get(url = springer_api_url, params = params, headers=headers, allow_redirects=True)
response
response.json()
response.json()['records'][0]['url']
pdf_url = response.json()['records'][0]['url'][1]['value']
pdf_url

pdf_response = requests.get(pdf_url)
pdf_response
pdf_response.content

with open(filename, mode = 'wb') as f:
    f.write(pdf_response.content)

id_param = re.compile(r'openurl/pdf\?id=doi\:')
new_pdf_url = id_param.sub('content/pdf/', pdf_url) + '.pdf'
fix_https = re.compile(r'http')
new_pdf_url = fix_https.sub('https', new_pdf_url)
new_pdf_url

# https://link.springer.com/content/pdf/10.1007/s00421-021-04808-z.pdf
# https://link.springer.com/content/pdf/10.1007/s00421-021-04808-z.pdf

pdf_response = requests.get(new_pdf_url)
pdf_response
pdf_response.content

drop_prefix = str(springer_non_oa_articles.loc[0,'doi'].split('/')[1:]).strip('[').strip("']")
folder = '/Users/antonhesse/Desktop/Anton/Education/UMN/Lab and Research/HSPL/CPET_scoping_review/data/cpet_articles/ovid/springer_non_oa_pdfs/'
filename = folder + str(drop_prefix)+'.pdf'
filename

with open(filename, mode = 'wb') as f:
    f.write(pdf_response.content)



################

test_url = 'https://link.springer.com/content/pdf/10.1007/s00421-021-04808-z.pdf'


pdf_response = requests.get(test_url, headers=headers, allow_redirects=True)
pdf_response
pdf_response.content

drop_prefix = str(springer_non_oa_articles.loc[0,'doi'].split('/')[1:]).strip('[').strip("']")
folder = '/Users/antonhesse/Desktop/Anton/Education/UMN/Lab and Research/HSPL/CPET_scoping_review/data/cpet_articles/ovid/springer_non_oa_pdfs/'
filename = folder + str(drop_prefix)+'.pdf'
filename

with open(filename, mode = 'wb') as f:
    f.write(pdf_response.content)



# id_param = re.compile(r'pdf\?id=doi\:')
# new_pdf_url = id_param.sub('pdf/', pdf_url)
# new_pdf_url

# new_pdf_response = requests.get(new_pdf_url)

drop_prefix = str(springer_non_oa_articles.loc[0,'doi'].split('/')[1:]).strip('[').strip("']")
folder = '/Users/antonhesse/Desktop/Anton/Education/UMN/Lab and Research/HSPL/CPET_scoping_review/data/cpet_articles/ovid/springer_non_oa_pdfs/'
filename = folder + str(drop_prefix)+'.pdf'
filename

with open(filename, mode = 'wb') as f:
    f.write(pdf_response.content)

# https://api.springernature.com/meta/v2/?api_key=94ac47d7af9676b7403b4694dcf058b0&q=10.1007%2Fs00421-021-04808-z
# https://api.springernature.com/meta/v2/json?api_key=94ac47d7af9676b7403b4694dcf058b0&q=10.1007%2Fs00421-021-04808-z&s=1&p=10