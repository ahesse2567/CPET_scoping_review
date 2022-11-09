import pandas as pd
from tqdm import tqdm
import requests
import numpy as np

oa_articles = pd.read_csv('data/cpet_articles/unpaywall/oa_articles_status_codes.csv')
no_unpaywall_url_articles = oa_articles[oa_articles['status_code'] == 'No URL available from unpaywall']
# no_unpaywall_url_articles

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:101.0) Gecko/20100101 Firefox/101.0'
}

folder = 'data/cpet_articles/full_texts/pdfs/unpaywall_oa'
res = []
for idx, row in tqdm(no_unpaywall_url_articles.iterrows(), total=len(no_unpaywall_url_articles)):
    out = {}
    doi = row['doi']
    out.update({'doi': doi})

    urls = [row['best_oa_location.url_for_pdf'], row['first_oa_location.url_for_pdf']]

    for idx, url in enumerate(urls):
        try:
            r = requests.get(url = url, headers=headers, allow_redirects=True, verify=True)
            out.update({f'status_code_{idx}': r.status_code})

            if r.status_code == 200:
                doi_suffix = str(doi.split('/', 1)[1:]).strip("[']")
                filename = f'{folder}/{doi_suffix}.pdf'

                with open(filename, 'wb') as f:
                    f.write(r.content)
            else:
                print(f'Status code {r.status_code} for DOI {doi}')

        except Exception as e:
            out.update({f'error_{idx}': e})
            print(f'Exception at DOI {doi}')

    res.append(out)

res_df = pd.DataFrame(res)

merge = pd.merge(no_unpaywall_url_articles, res_df, how = 'outer', on='doi')
merge.columns
merge['status_code_0'].value_counts() # most are NOT status code 200

merge[merge['status_code_1'] == 200]
folder = 'data/cpet_articles/full_texts/pdfs'
res2 = []
for idx, row in tqdm(merge[merge['status_code_1'] == 200].iterrows(),total=len(merge[merge['status_code_1'] == 200])):
    out = {}
    doi = row['doi']
    out.update({'doi': doi})

    urls = [row['best_oa_location.url_for_pdf'], row['first_oa_location.url_for_pdf']]

    for idx, url in enumerate(urls):
        try:
            r = requests.get(url = url, headers=headers, allow_redirects=True, verify=True)
            out.update({f'status_code_{idx}': r.status_code})

            if r.status_code == 200:
                doi_suffix = str(doi.split('/')[1:]).strip("[']")
                filename = f'{folder}/{doi_suffix}.pdf'

                with open(filename, 'wb') as f:
                    f.write(r.content)
            else:
                print(f'Status code {r.status_code} for DOI {doi}')

        except Exception as e:
            out.update({f'error_{idx}': e})
            print(f'Exception at DOI {doi}')
            print(e)

    res2.append(out)

res2_df = pd.DataFrame(res2)

res2_df

non200_idx = np.where((merge['status_code_0'] != 200) & (merge['status_code_1'] != 200))[0].tolist()
unpaywall_oa_for_cr = merge.iloc[non200_idx,:]
unpaywall_oa_for_cr['status_code_0'].value_counts()

unpaywall_oa_for_cr.to_csv('data/cpet_articles/unpaywall/unpaywall_oa_for_cr.csv',index=False)