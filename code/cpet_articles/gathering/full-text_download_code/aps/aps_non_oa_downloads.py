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

def click_links_landing_page(driver):
    pdf_icon = driver.find_element(By.CLASS_NAME, "icon-PDF").find_element(By.XPATH, '../../..')
    pdf_dropdown = pdf_icon.find_element(By.TAG_NAME, 'a')

    pdf_download_text = pdf_dropdown.find_element(By.XPATH, "//*[text()='Download PDF']")
    pdf_download_link = pdf_download_text.find_element(By.XPATH, "../..")

    pdf_dropdown.click()
    pdf_download_link.click()

def click_links_download_page(driver):
    if len(driver.find_elements(By.XPATH, "//button[@aria-label='Download document' and @type='button']")) > 0:
        download_button_arrow = driver.find_element(By.XPATH, "//button[@aria-label='Download document' and @type='button']")
        download_link = driver.find_element(By.XPATH, "//a[@class='download list-button btn' and @data-download-files-key='pdf']")
        download_button_arrow.click()
        download_link.click()
    else:
        download_link = driver.find_element(By.XPATH, "//div[@class='grouped right']").find_element(By.XPATH, 'a')
        download_link.click()

def download_pdf(doi, dest_folder, content):
    doi_suffix = str(doi.split('/', 1)[1:]).strip("[']")
    filename = dest_folder + str(doi_suffix)+'.pdf'
    with open(filename, mode = 'wb') as f:
        f.write(content)

articles = pd.read_csv('data/cpet_articles/unpaywall/unpaywall_info.csv')
aps_ca_articles = articles[(articles['publisher'] == 'American Physiological Society') & \
    (articles['is_oa'] == False)].drop_duplicates().reset_index(drop=True)

aps_ca_pdf_paths = list(Path('data/cpet_articles/full_texts/pdfs/aps_non_oa').glob('*.pdf'))
aps_ca_pdfs = [path.stem for path in aps_ca_pdf_paths]

# find which articles are already downloaded
re_doi_prefix = re.compile(r'(?<=\d/).*')
aps_ca_articles['doi_suffix'] = aps_ca_articles['doi'].apply(lambda x: re_doi_prefix.search(x).group())

full_texts_to_download = [x for x in aps_ca_articles['doi_suffix'].tolist() if x not in aps_ca_pdfs]
len(full_texts_to_download)
merge = pd.merge(pd.DataFrame({'doi_suffix': full_texts_to_download}), aps_ca_articles, how='inner', on='doi_suffix')

headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:102.0) Gecko/20100101 Firefox/102.0'}
dest_folder = 'data/cpet_articles/full_texts/pdfs/aps_non_oa/'

driver = webdriver.Firefox(service=FirefoxService(GeckoDriverManager().install()))
driver.implicitly_wait(1) # hopefully let's JS load correctly

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
            driver.execute_script("window.scrollTo(0, 200)")
            click_links_landing_page(driver)
            time.sleep(5)
            click_links_download_page(driver)
            time.sleep(3)
            parent_tab = driver.current_window_handle
            chwd = driver.window_handles
            time.sleep(1) # might help with switching windows
            driver.switch_to.window(chwd[1])
            # download byte content
            full_text_resp = requests.get(url = driver.current_url, headers = headers)
            out.update({'full_text_SC': full_text_resp.status_code})
            if full_text_resp.status_code == 200:
                download_pdf(doi = doi, dest_folder=dest_folder, content=full_text_resp.content)
            driver.close()
            driver.switch_to.window(parent_tab)
    except Exception as e:
        print(e)
        out.update({'error': e})
    log.append(out)
    time.sleep(60) # wait so our IP address isn't blocked

# log_df = pd.DataFrame(log)
# log_df['doi_redirect_SC'].value_counts()
# log_df.to_csv('data/cpet_articles/unpaywall/aps_non_oa_errors.csv', index=False)

# error_df = log_df[~log_df['error'].isna()].reset_index(drop=True)

"""
Error testing

driver = webdriver.Firefox(service=FirefoxService(GeckoDriverManager().install()))
driver.implicitly_wait(1) # hopefully let's JS load correctly

n = random.randint(0, error_df.shape[0])
row = error_df.loc[n,:]

log = []
for idx, row in tqdm(error_df.iterrows(), total=error_df.shape[0]):
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
            driver.execute_script("window.scrollTo(0, 200)")
            click_links_landing_page(driver)
            time.sleep(5)
            click_links_download_page(driver)
            time.sleep(3)
            parent_tab = driver.current_window_handle
            chwd = driver.window_handles
            time.sleep(1) # might help with switching windows
            driver.switch_to.window(chwd[1])
            # download byte content
            full_text_resp = requests.get(url = driver.current_url, headers = headers)
            out.update({'full_text_SC': full_text_resp.status_code})
            if full_text_resp.status_code == 200:
                download_pdf(doi = doi, dest_folder=dest_folder, content=full_text_resp.content)
            driver.close()
            driver.switch_to.window(parent_tab)
    except Exception as e:
        print(e)
        out.update({'error': e})
    log.append(out)


"""