import requests
import pandas as pd
import requests
import json
from tqdm import tqdm

articles = pd.read_csv('/Users/antonhesse/Desktop/Anton/Education/UMN/Lab and Research/HSPL/CPET_scoping_review/data/cpet_articles/unpaywall/unpaywall_info.csv')
springer_non_oa_articles = articles[(articles['is_oa'] == False) & \
    (articles['publisher'] == 'Springer Science and Business Media LLC')].reset_index(drop=True)

with open('/Users/antonhesse/Desktop/Anton/Education/UMN/Lab and Research/HSPL/CPET_scoping_review/code/cpet_articles/gathering/full-text_download_code/springer_config.json') as config_file:
    api_key = json.load(config_file)['api_key']
# api_key

springer_api_url = 'https://api.springernature.com/meta/v2/json?'
headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:100.0) Gecko/20100101 Firefox/100.0'}
folder = '/Users/antonhesse/Desktop/Anton/Education/UMN/Lab and Research/HSPL/CPET_scoping_review/data/cpet_articles/full_texts/pdfs/springer_non_oa_pdfs/'

query_status_code = []
pdf_status_code = []

for i, row in tqdm(springer_non_oa_articles.iterrows(), total=springer_non_oa_articles.shape[0]):
    query = row['doi']
    params = {
    'api_key': api_key,
    'q': query
    }

    try:
        response = requests.get(url = springer_api_url, params = params, headers=headers, allow_redirects=True)
        if response.status_code == 200:
            query_status_code.append(response.status_code)

            pdf_url = response.json()['records'][0]['url'][1]['value']
            pdf_response = requests.get(pdf_url, stream=True, allow_redirects=True)
            if pdf_response.status_code == 200:
                pdf_status_code.append(pdf_response.status_code)

                # drop_prefix = str(row['doi'].split('/')[1:]).strip("[']")
                # filename = folder + str(drop_prefix)+'.pdf'

                # with open(filename, mode = 'wb') as f:
                #     f.write(pdf_response.content)
            
            else:
                print('Bad pdf URL response:', response.status_code, 'for', pdf_response.url)
                pdf_status_code.append(pdf_response.status_code)
        
        else:
            print('Bad query URL response:', response.status_code, 'for', response.url)
            query_status_code.append(response.status_code)

    except Exception as e:
        print(f'{e} at index {i} for url {query}')
        query_status_code.append(e)
        # pdf_status_code.append(e)


# I need to fix an error where some of the status code lists get double counted
# or I need to make the status codes part of a data frame with the doi