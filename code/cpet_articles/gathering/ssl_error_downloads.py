# %%
import requests
import pandas as pd
from unpywall.utils import UnpywallCredentials
from unpywall import Unpywall
from tqdm import tqdm

UnpywallCredentials('hesse151@umn.edu')
# %%
oa_articles = pd.read_csv('/Users/antonhesse/Desktop/Anton/Education/UMN/Lab and Research/HSPL/CPET_scoping_review/data/cpet_articles/unpaywall/oa_articles_status_codes.csv')
ssl_oa_articles = oa_articles[oa_articles['status_code'].str.contains('SSL')]

# %%
ssl_status_code = []

for idx, row in tqdm(ssl_oa_articles.iterrows()):
    url = Unpywall.get_pdf_link(doi = row.doi_url)
    
    if url:
        # this just checks to make sure there's a URL before sending the request
        try:
            response = requests.get(url, verify=False)
            # verify=False required to fix ssl errors
            if response.status_code == 200: # save the PDF if the server responds
                ssl_status_code.append(response.status_code)

                # drop the doi prefix so you can use the DOI as a filename
                drop_prefix = row.doi.split('/')[1]
                folder_name = '/Users/antonhesse/Desktop/Anton/Education/UMN/Lab and Research/HSPL/CPET_scoping_review/data/cpet_articles/pdfs/unpaywall_oa_ssl/'
                filename = folder_name + str(drop_prefix)+'.pdf'

                # write the PDF
                with open(filename, 'wb') as f:
                    f.write(response.content)

            else:
                print('Bad URL response:', response.status_code, 'for', url, 'at idx', idx)
                ssl_status_code.append(response.status_code)
        except Exception as e:
            print(f'{e} at index {idx} for url {url}')
            ssl_status_code.append(e)

    else: # if Unpywall can't get a url
        print('No URL available from unpaywall')
        ssl_status_code.append('No URL available from unpaywall')

# %%
ssl_oa_articles.to_csv('/Users/antonhesse/Desktop/Anton/Education/UMN/Lab and Research/HSPL/CPET_scoping_review/data/cpet_articles/unpaywall/ssl_oa_articles')