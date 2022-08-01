from selenium import webdriver
from selenium.webdriver.firefox.service import Service as FirefoxService
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.common.by import By
import pandas as pd
import requests
import random
import time
from tqdm import tqdm
from pathlib import Path
import re
import sys
sys.path.append('code/cpet_articles/gathering/full-text_download_code/')
from helper_funcs.articles import get_current_full_texts, download_pdf

current_full_texts = get_current_full_texts()

all_articles = pd.read_csv('/Users/antonhesse/Desktop/Anton/Education/UMN/Lab and Research/HSPL/CPET_scoping_review/data/cpet_articles/unpaywall/unpaywall_info.csv')

re_doi_suffix = re.compile(r'(?<=\d/).*')
all_articles['doi_suffix'] = all_articles['doi'].apply(lambda x: re_doi_suffix.search(x).group())
full_texts_to_download = [x for x in all_articles['doi_suffix'].tolist() if x not in current_full_texts]

remaining_articles = pd.merge(pd.DataFrame({'doi_suffix': full_texts_to_download}), all_articles, how='inner', on='doi_suffix')
articles = remaining_articles[remaining_articles['publisher'] == 'Oxford University Press (OUP)'].drop_duplicates().reset_index(drop=True)
articles.shape


headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:102.0) Gecko/20100101 Firefox/102.0'}
dest_folder = '/Users/antonhesse/Desktop/Anton/Education/UMN/Lab and Research/HSPL/CPET_scoping_review/data/cpet_articles/full_texts/pdfs'

driver = webdriver.Firefox(service=FirefoxService(GeckoDriverManager().install()))
driver.implicitly_wait(1) # hopefully let's JS load correctly

# n = random.randint(0, articles.shape[0])
# row = articles.loc[n,:]


log = []
for idx, row in tqdm(articles.iterrows(), total=articles.shape[0]):
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
            pdf_link = driver.find_element(By.XPATH, "//a[@class='al-link pdf article-pdfLink']").get_attribute('href')
            full_text_resp = requests.get(url = pdf_link, headers = headers)
            # time.sleep(2) # wait in case there's ads or something
            out.update({'full_text_SC': full_text_resp.status_code})
            if full_text_resp.status_code == 200:
                download_pdf(doi=doi, dest_folder=dest_folder, content=full_text_resp.content)
                time.sleep(3)
    except Exception as e:
        print(e)
        out.update({'error': e})
    log.append(out)
    # time.sleep(20)

driver.quit()
# log_df = pd.DataFrame(log)
# log_df