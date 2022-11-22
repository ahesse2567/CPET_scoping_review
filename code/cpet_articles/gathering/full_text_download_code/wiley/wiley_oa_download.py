import requests
import pandas as pd
from tqdm import tqdm
import json
from code.cpet_articles.gathering.full_text_download_code.helper_funcs.articles import get_current_full_texts
from code.cpet_articles.gathering.full_text_download_code.helper_funcs.crossref_pdf_download import crossref_pdf_download
from code.cpet_articles.utils.article_names import get_doi_suffix

current_full_texts = get_current_full_texts()

all_articles = pd.read_csv('/Users/antonhesse/Desktop/Anton/Education/UMN/Lab and Research/HSPL/CPET_scoping_review/data/cpet_articles/unpaywall/unpaywall_info.csv')
all_articles['doi_suffix'] = all_articles['doi'].apply(lambda x: get_doi_suffix(x))

remaining_articles = all_articles[~all_articles['doi_suffix'].isin(current_full_texts)]
articles = remaining_articles[remaining_articles['publisher'] == 'Wiley'].reset_index(drop=True)
articles.shape

with open('code/cpet_articles/gathering/full_text_download_code/wiley/wiley_config.json') as config_file:
    wiley_token = json.load(config_file)['api_key']

user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:107.0) Gecko/20100101 Firefox/107.0'
accept = 'application/vnd.citationstyles.csl+json, application/vnd.crossref.unixref+xml'
dest_folder = 'data/cpet_articles/full_texts/pdfs/'


# uncomment below to redownload wiley oa articles
res = []
for i, row in tqdm(articles.iterrows(), total=articles.shape[0]):
    temp = crossref_pdf_download(
        doi=row['doi'],
        accept=accept,
        dest=dest_folder,
        user_agent=user_agent,
        TDM_header='Wiley-TDM-Client-Token',
        TDM_token=wiley_token,
        verify=True)
    res.append(temp)

res_df = pd.DataFrame(res)

res_df['publisher_status_code'].value_counts()

# res_df = pd.DataFrame(res)
# merge = pd.merge(wiley_articles, res_df, how = 'outer', on='doi')
# merge.columns
# merge['publisher_status_code'].value_counts() # most are NOT status code 200
# # merge.to_csv('data/cpet_articles/unpaywall/wiley_oa_status_codes.csv', index=False)


###### Rerun code using URLs from Unpaywall rather than crossref

df_status_codes = pd.read_csv('data/cpet_articles/unpaywall/wiley_oa_status_codes.csv')
non200 = df_status_codes[df_status_codes['publisher_status_code'] != 200]
non200.shape
# res2 = []
# for i, row in tqdm(non200.iterrows(), total=non200.shape[0]):
#     temp = crossref_pdf_download(
#         doi=row['doi'],
#         accept=accept,
#         dest=dest_folder,
#         user_agent=user_agent,
#         application='pdf',
#         TDM_header='Wiley-TDM-Client-Token',
#         TDM_token=wiley_token,
#         verify=True)
    # res2.append(temp)

non200
test_url = non200['best_oa_location.url_for_pdf'].iloc[1]
test_url

publisher_headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:101.0) Gecko/20100101 Firefox/101.0',
    'Wiley-TDM-Client-Token': wiley_token
}
folder = 'data/cpet_articles/full_texts/pdfs/wiley_oa_pdfs'
res = []
for idx, row in tqdm(non200.iterrows(), total=len(non200)):
    out = {}
    doi = row['doi']
    out.update({'doi': doi})
    pdf_url_best = row['best_oa_location.url_for_pdf']

    try:
        r = requests.get(url = pdf_url_best, headers=publisher_headers, allow_redirects=True, verify=True)
        out.update({'best_oa_location_status_code': r.status_code})

        if (r.status_code != 200) & (row['best_oa_location.url_for_pdf'] != row['first_oa_location.url_for_pdf']):
            # try another possible pdf url
            print('Trying another PDF url')
            pdf_url_first = row['first_oa_location.url_for_pdf']
            r = requests.get(url = pdf_url_first, headers=publisher_headers, allow_redirects=True, verify=True)
            out.update({'first_oa_location_status_code': r.status_code})

        if r.status_code == 200:
            doi_suffix = str(doi.split('/')[1:]).strip("[']")
            filename = f'{folder}/{doi_suffix}.pdf'

            with open(filename, 'wb') as f:
                f.write(r.content)
        else:
            print(f'Status code {r.status_code} for DOI {doi}')

    except Exception as e:
        out.update({'error': e})
        print(f'Exception at DOI {doi}')
        print(e)

    res.append(out)

res
res_df = pd.DataFrame(res)
merge = pd.merge(non200, res_df, how = 'outer', on='doi')
merge.shape
merge['publisher_status_code'].value_counts() # most are NOT status code 200
merge['best_oa_location_status_code'].value_counts() # ok so we got a few more
merge['first_oa_location_status_code'].value_counts() # and just a couple more

import numpy as np

merge['remaining_non200'] = np.where((merge['best_oa_location_status_code'] != 200) & (merge['first_oa_location_status_code'] != 200), merge['publisher_status_code'], 200)
merge['remaining_non200'].value_counts() # we still have several left

merge.to_csv('data/cpet_articles/unpaywall/wiley_oa_status_codes.csv', index=False)


##### Resolve http errors

## spoiler, not many were fixed

https_errors = df_status_codes[(df_status_codes['error_y'].notna()) & \
    (df_status_codes['error_y'] != "Invalid URL 'nan': No scheme supplied. Perhaps you meant http://nan?")]
https_errors['error_y'].value_counts()

publisher_headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:101.0) Gecko/20100101 Firefox/101.0',
    'Wiley-TDM-Client-Token': wiley_token
}
dest_folder = 'data/cpet_articles/full_texts/pdfs/wiley_oa_pdfs'
res = []
for i, row in tqdm(https_errors.iterrows(), total=https_errors.shape[0]):
    temp = crossref_pdf_download(
        doi=row['doi'],
        accept=accept,
        dest=dest_folder,
        user_agent=user_agent,
        TDM_header='Wiley-TDM-Client-Token',
        TDM_token=wiley_token,
        verify=False)
    res.append(temp)

res_df = pd.DataFrame(res)
res_df
res_df.columns
res_df['error'][0]