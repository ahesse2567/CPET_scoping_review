import pandas as pd
from tqdm import tqdm
import requests
import json
from pathlib import Path
import re
import sys
sys.path.append('code/cpet_articles/gathering/full-text_download_code/helper_funcs')
# from elsevier_full_text_download import elsevier_full_text_download
from crossref_pdf_download import crossref_pdf_download
# import random
import numpy as np

# try downloading these remaining artilces by publisher
existing_pdf_paths = list(Path('data/cpet_articles/full_texts/pdfs').rglob('*/*.pdf'))
existing_pdf_files = [path.stem for path in existing_pdf_paths]
# existing_pdf_files[0:10]

cr_articles = pd.read_csv('data/cpet_articles/unpaywall/unpaywall_oa_for_cr.csv').drop_duplicates(subset=['doi']).reset_index(drop=True)
cr_articles['doi'].value_counts()
cr_articles['doi_suffix'] = cr_articles['doi'].apply(lambda x: str(x.split('/')[1:]).strip("[']")).tolist()
# cr_articles['doi_suffix'].value_counts()

remaining_oa_articles = [x for x in cr_articles['doi_suffix'] if x not in existing_pdf_files]
remaining_oa_articles_df = pd.DataFrame({'doi_suffix': remaining_oa_articles})
# remaining_oa_articles_df

merge = pd.merge(remaining_oa_articles_df, cr_articles, how='inner', on='doi_suffix')
merge['publisher'].value_counts()

"""
elsevier_oa_articles = merge[merge['publisher'] == 'Elsevier BV'].reset_index(drop=True)
with open("code/cpet_articles/gathering/full-text_download_code/elsevier_config.json") as config_file:
    api_key = json.load(config_file)['apikey']
with open("code/cpet_articles/gathering/full-text_download_code/elsevier_config.json") as config_file:
    insttoken = json.load(config_file)['insttoken']
    
dest_folder = 'data/cpet_articles/full_texts/txts/elsevier_oa_txts'
elsevier_params = {
    'apiKey': api_key,
    'insttoken': insttoken,
    'httpAccept': 'text/plain',
    'view': 'FULL'
}
elsevier_headers ={'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:101.0) Gecko/20100101 Firefox/101.0'}

res = []
for i, row in tqdm(elsevier_oa_articles.iterrows(), total=len(elsevier_oa_articles)):
    doi = row['doi']
    out = {'doi': doi}
    doi_url = 'https://api.elsevier.com/content/article/doi/' + doi

    try:
        r = requests.get(
            url=doi_url, params=elsevier_params, headers=elsevier_headers,
            allow_redirects=True, verify=True)
        out.update({'publisher_status_code': r.status_code})
        if r.status_code == 200:
            doi_suffix = str(doi.split('/')[1:]).strip("[']")
            filename = f'{dest_folder}/{doi_suffix}.txt'

            with open(filename, mode='wb') as f:
                f.write(r.content)
    except Exception as e:
        out.update({'error': e})
    res.append(out)

res_df = pd.DataFrame(res)
res_df
"""

wiley_oa_articles = merge[merge['publisher'] == 'Wiley'].reset_index(drop=True)
with open("code/cpet_articles/gathering/full-text_download_code/wiley_config.json") as config_file:
    wiley_api_key = json.load(config_file)['api_key']

wiley_folder = 'data/cpet_articles/full_texts/pdfs/wiley_oa_pdfs'
crossref_headers ={
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:101.0) Gecko/20100101 Firefox/101.0',
    'Accept': 'application/vnd.citationstyles.csl+json, application/vnd.crossref.unixref+xml'
}
wiley_headers ={
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:101.0) Gecko/20100101 Firefox/101.0',
    'Wiley-TDM-Client-Token': wiley_api_key
}

# uncomment below to redownload wiley oa articles
res = []
for i, row in tqdm(wiley_oa_articles.iterrows(), total=wiley_oa_articles.shape[0]):
    temp = crossref_pdf_download(
        doi=row['doi'],
        accept='application/vnd.citationstyles.csl+json, application/vnd.crossref.unixref+xml',
        dest=wiley_folder,
        user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:101.0) Gecko/20100101 Firefox/101.0',
        TDM_header='Wiley-TDM-Client-Token',
        TDM_token=wiley_api_key,
        verify=True)
    res.append(temp)

pdf_re = re.compile(r'http.*pdf.*')
wiley_res = []
for i, row in tqdm(wiley_oa_articles.iterrows(), total=len(wiley_oa_articles)):
    doi = row['doi']
    out = {'doi': doi}
    doi_url = 'https://doi.org/' + doi

    try:
        crossref_response = requests.get(
            url = doi_url, headers=crossref_headers,
            allow_redirects=True,verify=True)
        out.update({'CR_status_code': crossref_response.status_code})

        if crossref_response.status_code != 200:
            print(f'Status code {crossref_response.status_code} for DOI {doi}')
            wiley_res.append(out)
            continue
        
        pdf_links = [list(filter(pdf_re.search, item.values())) for item in crossref_response.json()['link']]
        list_len = [len(l) for l in pdf_links] # if a list len > 0, it refers to a PDF
        pdf_link_idx = list(np.where(np.array(list_len) > 0)[0])

        for i in pdf_link_idx:
            full_text_url = pdf_links[i][0]
            r = requests.get(
                url=full_text_url, headers=wiley_headers,
                allow_redirects=True, verify=True)
            out.update({'publisher_status_code': r.status_code})
            if r.status_code == 200:
                doi_suffix = str(doi.split('/')[1:]).strip("[']")
                filename = f'{wiley_folder}/{doi_suffix}.txt'

                with open(filename, mode='wb') as f:
                    f.write(r.content)

    except Exception as e:
        out.update({'error': e})

    wiley_res.append(out)

wiley_res_df = pd.DataFrame(wiley_res)
wiley_res_df['publisher_status_code'].value_counts()
# and eevvverryything is still a status code 503