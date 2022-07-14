import requests
import pandas as pd
from tqdm import tqdm
import json
import re
import numpy as np

articles = pd.read_csv('data/cpet_articles/unpaywall/unpaywall_info.csv')
cdn = articles[(articles['is_oa'] == False) & \
    (articles['publisher'] == 'Canadian Science Publishing')].reset_index(drop=True)
cdn.shape

with open('code/cpet_articles/gathering/pdf_download_code/crossref_config.json') as config_file:
    crossref_token = json.load(config_file)['api_key']

dest_folder = 'data/cpet_articles/full_texts/pdfs/cdn_non_oa_pdfs'

crossref_headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:101.0) Gecko/20100101 Firefox/101.0',
    'Accept': 'application/vnd.citationstyles.csl+json, application/vnd.crossref.unixref+xml'
}
pdf_re = re.compile(r'.*pdf.*') # find 'pdf' within link or application content type

res = []
for idx, row in tqdm(cdn.iterrows(), total=len(cdn)):
    doi = row['doi']
    out = {'doi': doi}
    doi_url = doi_url = 'https://doi.org/' + str(doi)

    try:
        crossref_response = requests.get(
            url = doi_url,
            headers=crossref_headers,
            allow_redirects=True,
            verify=True)
        
        out.update({'CR_status_code': crossref_response.status_code})

        if crossref_response.status_code != 200:
            print(f'Status code {crossref_response.status_code} for DOI {doi}')
            res.append(out)
            continue

        link_info = crossref_response.json()['link']
        pdf_links = [list(filter(pdf_re.findall, item.values())) for item in link_info]
        list_len = [len(l) for l in pdf_links] # if a list len > 0, it refers to a PDF
        pdf_link_idx = int(np.where(np.array(list_len) > 0)[0])
        full_text_url = link_info[pdf_link_idx]['URL']

        publisher_headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:101.0) Gecko/20100101 Firefox/101.0',
            'CR-TDM-Rate-Limit': '1500',
            'CR-TDM-Rate-Limit-Remaining': '76',
            'CR-TDM-Rate-Limit-Reset': '1378072800'
        }
        publisher_response = requests.get(
            url = full_text_url,
            headers=publisher_headers,
            allow_redirects=True,
            verify=True)
        out.update({'publisher_status_code': publisher_response.status_code})

        if publisher_response.status_code != 200:
            print(f'Status code {publisher_response.status_code} for DOI {doi}')
            res.append(out)
            continue

        doi_suffix = str(doi.split('/')[1:]).strip("[']")
        file_name = f'{dest_folder}/{doi_suffix}.pdf'

        with open(file_name, 'wb') as f:
            f.write(publisher_response.content)
    except Exception as e:
        print(f'Exception at DOI {doi}')
        print(e)
        out.update({'error': e})

    res.append(out)

res
res_df = pd.DataFrame(res)
merge = pd.merge(cdn, res_df, how = 'outer', on='doi')
merge.columns
merge['publisher_status_code'].value_counts() # most are NOT status code 200
merge.to_csv('data/cpet_articles/unpaywall/cdn_status_codes.csv', index=False)
