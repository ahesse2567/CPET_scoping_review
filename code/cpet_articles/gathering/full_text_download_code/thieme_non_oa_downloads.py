from selenium import webdriver
from selenium.webdriver.firefox.service import Service as FirefoxService
from send2trash import send2trash
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.common.by import By
import pandas as pd
import requests
import random
import time
from tqdm import tqdm
from pathlib import Path
import re

def accept_cookies(driver):
    if len(driver.find_elements(By.XPATH, "//*[text()='I Accept']")) > 0:
        accept_button = driver.find_element(By.XPATH, "//*[text()='I Accept']")
        accept_button.click()

def download_pdf(doi, dest_folder, content):
    doi_suffix = str(doi.split('/', 1)[1:]).strip("[']")
    filename = dest_folder + str(doi_suffix)+'.pdf'
    with open(filename, mode = 'wb') as f:
        f.write(content)

articles = pd.read_csv('data/cpet_articles/unpaywall/unpaywall_info.csv')
thieme_ca_articles = articles[(articles['publisher'] == 'Georg Thieme Verlag KG') & \
    (articles['is_oa'] == False)].drop_duplicates().reset_index(drop=True)

thieme_ca_pdf_paths = list(Path('data/cpet_articles/full_texts/pdfs/thieme_non_oa').glob('*.pdf'))
thieme_ca_pdfs = [path.stem for path in thieme_ca_pdf_paths]

# find which articles are already downloaded
re_doi_prefix = re.compile(r'(?<=\d/).*')
thieme_ca_articles['doi_suffix'] = thieme_ca_articles['doi'].apply(lambda x: re_doi_prefix.search(x).group())

full_texts_to_download = [x for x in thieme_ca_articles['doi_suffix'].tolist() if x not in thieme_ca_pdfs]
len(full_texts_to_download)
merge = pd.merge(pd.DataFrame({'doi_suffix': full_texts_to_download}), thieme_ca_articles, how='inner', on='doi_suffix')

headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:102.0) Gecko/20100101 Firefox/102.0'}
dest_folder = 'data/cpet_articles/full_texts/pdfs/thieme_non_oa/'

driver = webdriver.Firefox(service=FirefoxService(GeckoDriverManager().install()))
driver.implicitly_wait(1) # hopefully let's JS load correctly

# n = random.randint(0, merge.shape[0])
# row = merge.loc[n,:]

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
            # find PDF download button on landing page
            time.sleep(1) # wait in case there's ads or something
            accept_cookies(driver)
            time.sleep(2) # wait in case there's ads or something
            pdf_download_link = driver.find_element(By.XPATH, "//a[@class='linkNotUnderlined']")
            pdf_download_link.click()
            time.sleep(2)
            # driver.execute_script("window.scrollTo(0, 200)")
            full_text_resp = requests.get(url = driver.current_url, headers = headers)
            out.update({'full_text_SC': full_text_resp.status_code})
            if full_text_resp.status_code == 200:
                download_pdf(doi = doi, dest_folder=dest_folder, content=full_text_resp.content)
    except Exception as e:
        print(e)
        out.update({'error': e})
    log.append(out)
    # time.sleep(20)

driver.quit()
log_df = pd.DataFrame(log)
log_df