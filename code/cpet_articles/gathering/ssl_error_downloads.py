# %%
import requests
import pandas as pd
from unpywall.utils import UnpywallCredentials
from unpywall import Unpywall

UnpywallCredentials('hesse151@umn.edu')
# %%
ssl_error_articles = pd.read_csv('/Users/antonhesse/Desktop/Anton/Education/UMN/Lab and Research/HSPL/CPET_data_analysis/data/cpet_articles/ovid/ssl_error.csv')
# %%

for idx, row in ssl_error_articles.iterrows():

    url = Unpywall.get_pdf_link(doi = row.doi_url)
    
    if url:
        # this just checks to make sure there's a URL before sending the request
        try:
            response = requests.get(url, verify=False)

            if response.status_code == 200:
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
        except Exception as e:
            print(f'{e} at index {idx} for url {url}')

    else:
        # add code here to add a column with note that there no PDF URL available
        print('No URL available from unpaywall')

# %%
ssl_error_articles.to_csv('/Users/antonhesse/Desktop/Anton/Education/UMN/Lab and Research/HSPL/CPET_data_analysis/data/cpet_articles/ovid/oa_articles_status_codes.csv')