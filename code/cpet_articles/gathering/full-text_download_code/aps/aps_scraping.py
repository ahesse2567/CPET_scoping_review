from multiprocessing import parent_process
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
import sys
sys.path.append('/Users/antonhesse/Desktop/Anton/Education/UMN/Lab and Research/HSPL/CPET_scoping_review/code/cpet_articles/gathering/full-text_download_code/')
from helper_funcs.articles import *
import shutil

# As with Oxford(?), clicking the download button now sends the PDF directly to the down

def click_links_landing_page(driver, sleep_time=1):
    pdf_dropdown_link = driver.find_element(By.XPATH, "//a[@data-db-target-for='pdfLinks']")
    pdf_dropdown_link.click()
    time.sleep(sleep_time)

    pdf_download_link = pdf_dropdown_link.find_element(By.XPATH, "//a[text()='Download PDF']")
    pdf_download_link.click()
    time.sleep(sleep_time)

def click_links_download_page(driver, sleep_time=1):
    if len(driver.find_elements(By.XPATH, "//button[@aria-label='Download document' and @type='button']")) > 0:
        download_button_arrow = driver.find_element(By.XPATH, "//button[@aria-label='Download document' and @type='button']")
        download_link = driver.find_element(By.XPATH, "//a[@class='download list-button btn' and @data-download-files-key='pdf']")
        download_button_arrow.click()
        time.sleep(sleep_time)
        download_link.click()
        time.sleep(sleep_time)
    else:
        download_link = driver.find_element(By.XPATH, "//div[@class='grouped right']").find_element(By.XPATH, 'a')
        download_link.click()
        time.sleep(sleep_time)

def wait(duration=60):
    for i in trange(duration):
        time.sleep(1)

current_full_texts = get_current_full_texts()

all_articles = pd.read_csv('/Users/antonhesse/Desktop/Anton/Education/UMN/Lab and Research/HSPL/CPET_scoping_review/data/cpet_articles/unpaywall/unpaywall_info.csv')
all_articles['doi_suffix'] = all_articles['doi'].apply(lambda x: get_doi_suffix(x))
full_texts_to_download = [x for x in tqdm(all_articles['doi_suffix'].tolist()) if x not in current_full_texts]

remaining_articles = pd.merge(pd.DataFrame({'doi_suffix': full_texts_to_download}), all_articles, how='inner', on='doi_suffix')

articles = remaining_articles[remaining_articles['publisher'] == 'American Physiological Society'].drop_duplicates().reset_index(drop=True)
articles.shape

headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:102.0) Gecko/20100101 Firefox/102.0'}
dest_folder = '/Users/antonhesse/Desktop/Anton/Education/UMN/Lab and Research/HSPL/CPET_scoping_review/data/cpet_articles/full_texts/pdfs'

driver = webdriver.Firefox(service=FirefoxService(GeckoDriverManager().install()))
driver.implicitly_wait(1) # hopefully let's JS load correctly

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
            driver.execute_script("window.scrollTo(0, 200)")
            click_links_landing_page(driver)
            time.sleep(5)
            click_links_download_page(driver)
            time.sleep(3) # might help with switching windows
            close_extra_tabs(driver)
            # move PDF from downloads to pdf folder
            pdfs_in_downloads_paths = list(Path('/Users/antonhesse/Downloads').glob('*.pdf'))
            if len(pdfs_in_downloads_paths) > 1:
                for path in pdfs_in_downloads_paths:
                    Path.unlink(path)
            else:
                doi_suffix = get_doi_suffix(doi)
                new_path = '/Users/antonhesse/Desktop/Anton/Education/UMN/Lab and Research/HSPL/CPET_scoping_review/data/cpet_articles/full_texts/pdfs/' + doi_suffix + '.pdf'
                shutil.move(src=pdfs_in_downloads_paths[0], dst=new_path)
                time.sleep(2)
            wait(40) # wait so our IP address isn't blocked
    except Exception as e:
        print(e)
        out.update({'error': e})
        close_extra_tabs(driver)
    log.append(out)
    
log_df = pd.DataFrame(log)
log_df.to_csv('/Users/antonhesse/Desktop/Anton/Education/UMN/Lab and Research/HSPL/CPET_scoping_review/data/cpet_articles/unpaywall/aps_errors.csv',
    index=False)
# log_df['doi_redirect_SC'].value_counts()
# log_df.to_csv('data/cpet_articles/unpaywall/aps_non_oa_errors.csv', index=False)

# error_df = log_df[~log_df['error'].isna()].reset_index(drop=True)


# Error testing

# driver = webdriver.Firefox(service=FirefoxService(GeckoDriverManager().install()))
# driver.implicitly_wait(1) # hopefully let's JS load correctly

# n = random.randint(0, articles.shape[0])
# row = articles.loc[n,:]

# log = []
# for idx, row in tqdm(articles.iterrows(), total=articles.shape[0]):
#     doi = row['doi']
#     doi_url = 'https://doi.org/' + doi
#     out = {'doi': doi}
#     try:
#         # use DOI to get to publisher landing page
#         doi_resp = requests.get(doi_url, headers=headers)
#         out.update({'doi_redirect_SC': doi_resp.status_code})
#         if doi_resp.status_code == 200:
#             driver.get(doi_resp.url) # load publisher landing page
#             time.sleep(1) # wait in case there's ads or something
#             # find PDF download button on landing page
#             driver.execute_script("window.scrollTo(0, 200)")
#             click_links_landing_page(driver)
#             time.sleep(5) # let download page load
#             click_links_download_page(driver)
#             parent_tab = driver.current_window_handle
#             chwd = driver.window_handles
#             time.sleep(1) # might help with switching windows
#             driver.switch_to.window(chwd[1])
#             # this code used to work for some reason
#             # download byte content
#             # full_text_resp = requests.get(url = driver.current_url, headers = headers)
#             # out.update({'full_text_SC': full_text_resp.status_code})
#             # if full_text_resp.status_code == 200:
#             #     download_pdf(doi = doi, dest_folder=dest_folder, content=full_text_resp.content)
#             driver.close()
#             driver.switch_to.window(parent_tab)
#             # move PDF from downloads to pdf folder
#             pdfs_in_downloads_paths = list(Path('/Users/antonhesse/Downloads').glob('*.pdf'))
#                 if len(pdfs_in_downloads_paths) > 1:
#                     for path in pdfs_in_downloads_paths:
#                         Path.unlink(path)
#                 else:
#                     doi_suffix = get_doi_suffix(doi)
#                     new_path = '/Users/antonhesse/Desktop/Anton/Education/UMN/Lab and Research/HSPL/CPET_scoping_review/data/cpet_articles/full_texts/pdfs/' + doi_suffix + '.pdf'
#                     shutil.move(src=pdfs_in_downloads_paths[0], dst=new_path)
#     except Exception as e:
#         print(e)
#         out.update({'error': e})
#     log.append(out)
