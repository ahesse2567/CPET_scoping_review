# selenium 4
from distutils.log import error
from scipy import rand
from selenium import webdriver
from selenium.webdriver.firefox.service import Service as FirefoxService
from webdriver_manager.firefox import GeckoDriverManager
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import pandas as pd
import requests
import random
import shutil
import re
import time
from tqdm import tqdm
from pathlib import Path

def get_driver_status(driver=None):
    # check if driver is active or supplied to function. If not, initialize a driver
    try:
        return driver.service.is_connectable()            
    except AttributeError:
        return False

def download_ovid_full_text(doi, headers, dest_folder, driver=None, quit_driver=False):
    if get_driver_status(driver) == False:
        driver = webdriver.Firefox(service=FirefoxService(GeckoDriverManager().install()))
        driver.implicitly_wait(10) # hopefully let's JS load correctly
    out = {'doi': doi}
    doi_url = 'https://doi.org/' + doi
    try:
        doi_resp = requests.get(doi_url, headers=headers)
        out.update({'doi_redirect_SC': doi_resp.status_code})
        if doi_resp.status_code == 200:
            driver.get(doi_resp.url)
            # time.sleep(1)
        outer_download_button, inner_download_button = find_buttons(driver)
        driver.execute_script("window.scrollTo(0, 550)")
        outer_download_button.click()
        inner_download_button.click()

        time.sleep(15)
        parent_tab = driver.current_window_handle
        chwd = driver.window_handles
        time.sleep(1)
        driver.switch_to.window(chwd[1])
        full_text_resp = requests.get(url = driver.current_url, headers = headers)
        if full_text_resp.status_code == 200:
            download_pdf(doi=doi, dest_folder=dest_folder, content=full_text_resp.content)
        driver.close()
        driver.switch_to.window(parent_tab)
    except Exception as e:
        print(e)
        out.update({'error': e})
    if quit_driver == True:
        driver.quit()

    return out

def download_pdf(doi, dest_folder, content):
    doi_suffix = str(doi.split('/', 1)[1:]).strip("[']")
    filename = dest_folder + str(doi_suffix)+'.pdf'
    with open(filename, mode = 'wb') as f:
        f.write(content)

def find_buttons(driver):
    PDF_re = re.compile('PDF')
    outer_download_button = driver.find_element(By.CLASS_NAME, 'icon-pdf').find_element(By.XPATH, '../../..')
    inner_buttons = outer_download_button.find_elements(By.TAG_NAME, 'i')
    button_html = [i.find_element(By.XPATH, '..').get_attribute('innerHTML') for i in inner_buttons]
    pdf_button_list = [PDF_re.search(html) for html in button_html]
    PDF_idx = [i for i, val in enumerate(pdf_button_list) if val != None]
    if len(PDF_idx) == 1:
        pdf_download_icon = inner_buttons[PDF_idx[0]].find_element(By.XPATH,"//*[text()='PDF']")
        inner_download_button = pdf_download_icon.find_element(By.XPATH,'..')
    else:
        EPUB_re = re.compile('EPUB')
        epub_button_list = [EPUB_re.search(html) for html in button_html]
        EPUB_idx = [i for i, val in enumerate(epub_button_list) if val != None]
        epub_download_icon = inner_buttons[PDF_idx[0]].find_element(By.XPATH,"//*[text()='EPUB']")
        inner_download_button = epub_download_icon.find_element(By.XPATH,'..')
    
    return outer_download_button, inner_download_button


ovid_ca_articles = pd.read_csv('/Users/antonhesse/Desktop/Anton/Education/UMN/Lab and Research/HSPL/CPET_scoping_review/data/cpet_articles/unpaywall/ovid_non_oa_status_codes.csv')
error_df = ovid_ca_articles[~ovid_ca_articles['error'].isnull()].reset_index(drop=True)

ovid_ca_pdf_paths = list(Path('data/cpet_articles/full_texts/pdfs/ovid_non_oa').glob('*.pdf'))
ovid_ca_pdfs = [path.stem for path in ovid_ca_pdf_paths]
re_doi_prefix = re.compile(r'(?<=\d/).*')
error_df['doi_suffix'] = error_df['doi'].apply(lambda x: re_doi_prefix.search(x).group())

pdfs_to_download = [x for x in error_df['doi_suffix'].tolist() if x not in ovid_ca_pdfs]
merge = pd.merge(pd.DataFrame({'doi_suffix': pdfs_to_download}), error_df, how='inner', on='doi_suffix')
merge['error']

headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:102.0) Gecko/20100101 Firefox/102.0'}
dest_folder = 'data/cpet_articles/full_texts/pdfs/ovid_non_oa/'

driver = webdriver.Firefox(service=FirefoxService(GeckoDriverManager().install()))
driver.implicitly_wait(10) # hopefully let's JS load correctly


re_locate_window = re.compile(r'Unable to locate window')
error_df['locate_window'] = error_df['error'].apply(lambda x: re_locate_window.search(str(x)) != None)
unable_locate_window_df = error_df[error_df['locate_window']].reset_index(drop=True)
unable_locate_window_df.shape

for idx, row in unable_locate_window_df.iterrows():
    doi = row['doi']
    download_ovid_full_text(
        doi=doi,
        headers=headers,
        dest_folder=dest_folder,
        driver=driver,
        quit_driver=False
    )


re_locate_element = re.compile(r'Unable to locate element')
error_df['locate_icon-pdf'] = error_df['error'].apply(lambda x: re_locate_element.search(str(x)) != None)
unable_locate_df = error_df[error_df['locate_icon-pdf']].reset_index(drop=True)
unable_locate_df.shape

n = random.randint(0, unable_locate_df.shape[0])
doi = unable_locate_df.loc[n, 'doi']
doi_url = 'https://doi.org/' + doi
out = {'doi': doi}

try:
    doi_resp = requests.get(doi_url, headers=headers)
    out.update({'doi_redirect_SC': doi_resp.status_code})
    if doi_resp.status_code == 200:
        driver.get(doi_resp.url)
        # time.sleep(1)
    outer_download_button, inner_download_button = find_buttons(driver)
    driver.execute_script("window.scrollTo(0, 550)")
    outer_download_button.click()
    inner_download_button.click()

    time.sleep(15)
    parent_tab = driver.current_window_handle
    chwd = driver.window_handles
    time.sleep(1)
    driver.switch_to.window(chwd[1])
    full_text_resp = requests.get(url = driver.current_url, headers = headers)
    if full_text_resp.status_code == 200:
        download_pdf(doi=doi, dest_folder=dest_folder, content=full_text_resp.content)
    driver.close()
    driver.switch_to.window(parent_tab)
except Exception as e:
    print(e)
    out.update({'error': e})
if quit_driver == True:
    driver.quit()



# download_ovid_full_text(
#     doi=unable_locate_df.loc[1,'doi'],
#     headers=headers,
#     dest_folder='data/cpet_articles/full_texts/pdfs',
#     driver=driver,
#     quit_driver=False)

# driver.quit()

# connection_adapters_re = re.compile(r'connection adapters')
# error_df['connection_adapters'] = error_df['error'].apply(lambda x: connection_adapters_re.search(str(x)) != None)
# connection_adapters_df = error_df[error_df['connection_adapters']].reset_index(drop=True)
# connection_adapters_df.shape

# download_ovid_full_text(
#     doi=connection_adapters_df.loc[0,'doi'],
#     headers=headers,
#     dest_folder='data/cpet_articles/full_texts/pdfs',
#     driver=driver,
#     quit_driver=False)

# part of original loop
# if r.status_code == 200:
#     driver.get(r.url)
#     time.sleep(1)
#     outer_download_button = driver.find_element(By.CLASS_NAME, 'icon-pdf').find_element(By.XPATH, '../../..')
#     inner_buttons = outer_download_button.find_elements(By.TAG_NAME, 'i')
#     button_html = [i.find_element(By.XPATH, '..').get_attribute('innerHTML') for i in inner_buttons]
#     pdf_button_list = [PDF_re.search(html) for html in button_html]
#     PDF_idx = [i for i, val in enumerate(pdf_button_list) if val != None]
#     # scroll down b/c I think you need to do that for some reason
#     driver.execute_script("window.scrollTo(0, 600)")
#     if len(PDF_idx) == 1:
#         pdf_download_icon = inner_buttons[PDF_idx[0]].find_element(By.XPATH,"//*[text()='PDF']")
#         inner_download_button = pdf_download_icon.find_element(By.XPATH,'..')
#     else:
#         epub_button_list = [EPUB_re.search(html) for html in button_html]
#         EPUB_idx = [i for i, val in enumerate(epub_button_list) if val != None]
#         epub_download_icon = inner_buttons[PDF_idx[0]].find_element(By.XPATH,"//*[text()='EPUB']")
#         inner_download_button = epub_download_icon.find_element(By.XPATH,'..')
#         outer_download_button.click()
#         inner_download_button.click()
    
#     outer_download_button.click()
#     inner_download_button.click()
#     time.sleep(15)
#     parent_tab = driver.current_window_handle
#     chwd = driver.window_handles
#     time.sleep(1)
#     driver.switch_to.window(chwd[1])
#     full_text_resp = requests.get(url = driver.current_url, headers = headers)
#     if full_text_resp.status_code == 200:
#         download_pdf(doi=doi, dest_folder=pdf_folder, content=full_text_resp.content)
#     driver.close()
#     driver.switch_to.window(parent_tab)

