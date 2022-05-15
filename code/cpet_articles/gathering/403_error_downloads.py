# %%
import requests
import pandas as pd
import requests

#!pip install unpywall
from unpywall.utils import UnpywallCredentials
from unpywall import Unpywall

UnpywallCredentials('hesse151@umn.edu')
# %%
articles = pd.read_csv('/Users/antonhesse/Desktop/Anton/Education/UMN/Lab and Research/HSPL/CPET_data_analysis/data/cpet_articles/ovid/oa_articles_status_codes.csv')
oa_403_articles = articles[(articles['is_oa'] == True) & (articles['status_code'] == '403')].reset_index(drop=True)
new_status_code = []
# %%

for idx, row in oa_403_articles.iterrows():

    url = Unpywall.get_pdf_link(doi = row.doi_url)
    
    if url:
        # this just checks to make sure there's a URL before sending the request
        try:
            headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:100.0) Gecko/20100101 Firefox/100.0'}
            response = requests.get(url, headers = headers)

            if response.status_code == 200:
                new_status_code.append(response.status_code)
                # save the PDF if the server responds

                # drop the doi prefix so you can use the DOI as a filename
                drop_prefix = row.doi.split('/')[1]
                folder_name = '/Users/antonhesse/Desktop/Anton/Education/UMN/Lab and Research/HSPL/CPET_data_analysis/data/cpet_articles/ovid/ovid_pdfs/'
                filename = folder_name + str(drop_prefix)+'.pdf'

                # write the PDF
                with open(filename, 'wb') as f:
                    f.write(response.content)

            else:
                # if the server response is bad, add code here to add a column to oa_articles that saves the response.status_code
                print('Bad URL response:', response.status_code, 'for', url)
                new_status_code.append(response.status_code)
        except Exception as e:
            print(f'{e} at index {idx} for url {url}')
            new_status_code.append(e)

    else:
        # add code here to add a column with note that there no PDF URL available
        print('No URL available from unpaywall')
        new_status_code.append('No URL available from unpaywall')
# %%
new_status_code = []
for idx, row in oa_403_articles.iterrows():

    url = Unpywall.get_pdf_link(doi = row.doi_url)
    
    if url:
        # this just checks to make sure there's a URL before sending the request
        try:
            headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:100.0) Gecko/20100101 Firefox/100.0'}
            response = requests.get(url, headers = headers)
            print(f'URL response at index {idx}: {response.status_code} for {url}')
            new_status_code.append(response.status_code)

        except Exception as e:
            print(f'{e} at index {idx} for url {url}')
            new_status_code.append(e)

    else:
        # add code here to add a column with note that there no PDF URL available
        print('No URL available from unpaywall')
        new_status_code.append('No URL available from unpaywall')
# %%

oa_403_articles['post_403_status_code'] = new_status_code
oa_403_articles[oa_403_articles['post_403_status_code'] == 503]['publisher']
# those are all Elsevier
