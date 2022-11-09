from selenium import webdriver
from selenium.webdriver.firefox.service import Service as FirefoxService
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.common.by import By
import pandas as pd
import requests
import random
import time
from tqdm import tqdm, trange
from pathlib import Path
import re

def download_pdf(doi, dest_folder, content):
    doi_suffix = str(doi.split('/', 1)[1:]).strip("[']")
    filename = dest_folder + str(doi_suffix)+'.pdf'
    with open(filename, mode = 'wb') as f:
        f.write(content)

def wait(duration=60):
    for i in trange(duration):
        time.sleep(1)

articles = pd.read_csv('/Users/antonhesse/Desktop/Anton/Education/UMN/Lab and Research/HSPL/CPET_scoping_review/data/cpet_articles/unpaywall/unpaywall_info.csv')
hk_ca_articles = articles[(articles['publisher'] == 'Human Kinetics') & \
    (articles['is_oa'] == False)].drop_duplicates().reset_index(drop=True)

hk_ca_pdf_paths = list(Path('/Users/antonhesse/Desktop/Anton/Education/UMN/Lab and Research/HSPL/CPET_scoping_review/data/cpet_articles/full_texts/pdfs/human_kinetics').glob('*.pdf'))
hk_ca_pdfs = [path.stem for path in hk_ca_pdf_paths]

# find which articles are already downloaded
re_doi_suffix = re.compile(r'(?<=\d/).*')
hk_ca_articles['doi_suffix'] = hk_ca_articles['doi'].apply(lambda x: re_doi_suffix.search(x).group())

full_texts_to_download = [x for x in hk_ca_articles['doi_suffix'].tolist() if x not in hk_ca_pdfs]
merge = pd.merge(pd.DataFrame({'doi_suffix': full_texts_to_download}), hk_ca_articles, how='inner', on='doi_suffix')

headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:102.0) Gecko/20100101 Firefox/102.0'}
dest_folder = '/Users/antonhesse/Desktop/Anton/Education/UMN/Lab and Research/HSPL/CPET_scoping_review/data/cpet_articles/full_texts/pdfs/human_kinetics/'

driver = webdriver.Firefox(service=FirefoxService(GeckoDriverManager().install()))
driver.implicitly_wait(1) # hopefully let's JS load correctly

n = random.randint(0, merge.shape[0])
row = merge.loc[n,:]

log = []
for idx, row in tqdm(merge.iterrows(), total=merge.shape[0]):
    doi = row['doi']
    doi_url = 'https://doi.org/' + doi
    out = {'doi': doi}
    try:
        # use DOI to get to publisher landing page
        doi_resp = requests.get(doi_url, headers=headers)
        out.update({'doi_redirect_SC': doi_resp.status_code})
        if doi_resp.status_code == 200:
            driver.get(doi_resp.url) # load publisher landing page
            time.sleep(1) # wait in case there's ads or something
            # driver.execute_script("window.scrollTo(0, 200)")
            pdf_download_link = driver.find_element(By.XPATH, "//a[@id='pdf-download']")
            pdf_download_url = pdf_download_link.get_attribute('href')
            full_text_resp = requests.get(url=pdf_download_url, headers=headers, allow_redirects=True)
            out.update({'full_text_SC': full_text_resp.status_code})
            if full_text_resp.status_code == 200:
                download_pdf(doi = doi, dest_folder=dest_folder, content=full_text_resp.content)
            
            """
            # code below USED to work, but now clicking the link automatically sends the pdf
            # to the downloads folder
            pdf_download_link.click()
            time.sleep(5) # allow page to load

            parent_tab = driver.current_window_handle
            chwd = driver.window_handles # time.sleep(1) # might help with switching windows and avoiding errors
            driver.switch_to.window(chwd[1])
            
            full_text_resp = requests.get(url = driver.current_url, headers = headers)
            out.update({'full_text_SC': full_text_resp.status_code})
            if full_text_resp.status_code == 200:
                download_pdf(doi = doi, dest_folder=dest_folder, content=full_text_resp.content)
            driver.close()
            driver.switch_to.window(parent_tab)
            """

    except Exception as e:
        print(e)
        out.update({'error': e})
    wait(47) # Site suggests waiting 60 seconds between requests
    log.append(out)

driver.quit()

log_df = pd.DataFrame(log)
error_df = log_df[~log_df['error'].isna()]
error_df = pd.merge(error_df, merge, how='inner', on='doi')
error_df.to_csv('/Users/antonhesse/Desktop/Anton/Education/UMN/Lab and Research/HSPL/CPET_scoping_review/data/cpet_articles/unpaywall/human_kinetics_errors.csv')