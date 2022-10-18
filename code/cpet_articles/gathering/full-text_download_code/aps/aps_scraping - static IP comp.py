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
import shutil
import re
# import sys
# helper_funcs_path = Path(r'\code\cpet_articles\gathering\full-text_download_code\helper_funcs')
# sys.path.append(helper_funcs_path)

def get_doi_suffix(doi):
    doi_suffix = str(doi.split('/', 1)[1:]).strip("[']")
    doi_suffix = re.sub(r"""([()\\*,"': /?;<>])""", '_._', doi_suffix) # remove bad chars
    doi_suffix = re.sub(r'(_._){2,}', '_._', doi_suffix) # remove multiple sequences of _._
    return doi_suffix

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

def close_extra_tabs(driver):
    driver.switch_to.window(driver.window_handles[0])
    parent_tab = driver.current_window_handle
    for handle in driver.window_handles:
        if handle != parent_tab:
            driver.switch_to.window(handle)
            driver.close()
    driver.switch_to.window(driver.window_handles[0])

downloaded_articles = pd.read_csv(str(Path('data/cpet_articles/unpaywall/downloaded_articles.csv')))
# downloaded_articles['doi_suffix'] = downloaded_articles['doi'].apply(lambda x: get_doi_suffix(x))
all_articles = pd.read_csv(str(Path('data/cpet_articles/unpaywall/unpaywall_info.csv')))
all_articles['doi_suffix'] = all_articles['doi'].apply(lambda x: get_doi_suffix(x))

remaining_articles = all_articles[~all_articles['doi_suffix'].isin(downloaded_articles['doi_suffix'].to_list())]
articles = remaining_articles[remaining_articles['publisher'] == 'American Physiological Society'].drop_duplicates().reset_index(drop=True)

headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:102.0) Gecko/20100101 Firefox/102.0'}
dest_folder = Path('data/cpet_articles/full_texts/pdfs')

driver = webdriver.Firefox(service=FirefoxService(GeckoDriverManager().install()))
driver.implicitly_wait(1) # hopefully let's JS load correctly

# uncomment if you want to test a random article
# n = random.randint(0, articles.shape[0])
# row = articles.loc[n, :]

# As with Oxford(?), clicking the download button now sends the PDF directly to the down

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

            downloads_folder_path = Path(re.escape(r'C:\Users\hesse151\Downloads'))
            pdfs_in_downloads_paths = list(downloads_folder_path.glob('*.pdf'))
            if len(pdfs_in_downloads_paths) > 1:
                for path in pdfs_in_downloads_paths:
                    Path.unlink(path)
            else:
                doi_suffix = get_doi_suffix(doi)
                new_folder = Path(re.escape(r'C:\Users\hesse151\Documents\CPET_scoping_review\data\cpet_articles\full_texts\pdfs'))
                new_path = new_folder / (doi_suffix + '.pdf')
                shutil.move(src=pdfs_in_downloads_paths[0], dst=new_path)
                time.sleep(2)
            wait(1) # The IP address will get blocked, but waiting is probably a good idea, anyway
    except Exception as e:
        print(e)
        out.update({'error': e})
        close_extra_tabs(driver)
    log.append(out)
    
log_df = pd.DataFrame(log)
log_df.to_csv('/Users/antonhesse/Desktop/Anton/Education/UMN/Lab and Research/HSPL/CPET_scoping_review/data/cpet_articles/unpaywall/aps_errors.csv', index=False)
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
#             if len(pdfs_in_downloads_paths) > 1:
#                 for path in pdfs_in_downloads_paths:
#                     Path.unlink(path)
#             else:
#                 doi_suffix = get_doi_suffix(doi)
#                 new_path = '/Users/antonhesse/Desktop/Anton/Education/UMN/Lab and Research/HSPL/CPET_scoping_review/data/cpet_articles/full_texts/pdfs/' + doi_suffix + '.pdf'
#                 shutil.move(src=pdfs_in_downloads_paths[0], dst=new_path)
#     except Exception as e:
#         print(e)
#         out.update({'error': e})
#     log.append(out)
