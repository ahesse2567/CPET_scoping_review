# selenium 4
from selenium import webdriver
from selenium.webdriver.firefox.service import Service as FirefoxService
from webdriver_manager.firefox import GeckoDriverManager
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options as FirefoxOptions
firefox_options = FirefoxOptions()
firefox_options.add_argument("--headless")
import pandas as pd
import requests
import random
import shutil
import re
import time
from tqdm import tqdm

def download_pdf(doi, dest_folder, content):
    doi_suffix = str(doi.split('/', 1)[1:]).strip("[']")
    filename = dest_folder + str(doi_suffix)+'.pdf'
    with open(filename, mode = 'wb') as f:
        f.write(content)

driver = webdriver.Firefox(service=FirefoxService(GeckoDriverManager().install()))
driver.implicitly_wait(10) # hopefully let's JS load correctly

articles = pd.read_csv('/Users/antonhesse/Desktop/Anton/Education/UMN/Lab and Research/HSPL/CPET_scoping_review/data/cpet_articles/unpaywall/unpaywall_info.csv')
ovid_ca_articles = articles[(articles['is_oa'] == False) & (articles['publisher'] == 'Ovid Technologies (Wolters Kluwer Health)')].reset_index(drop=True)

headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:102.0) Gecko/20100101 Firefox/102.0'}

# n = random.randint(0, ovid_ca_articles.shape[0])
# doi_url = ovid_ca_articles.loc[n, 'doi_url']
# r = requests.get(doi_url, headers=headers)

pdf_folder = 'data/cpet_articles/full_texts/pdfs/ovid_non_oa/'
epub_folder = 'data/cpet_articles/full_texts/epubs/ovid_non_oa/'
# row = ovid_ca_articles.loc[0,:]
PDF_re = re.compile('PDF')
EPUB_re = re.compile('EPUB')

log = []
for idx, row in tqdm(ovid_ca_articles.iterrows(), total=ovid_ca_articles.shape[0]):
    doi = row['doi']
    out = {'doi': doi}
    doi_url = row['doi_url']
    r = requests.get(doi_url, headers=headers)
    out.update({'doi_redirect_SC': r.status_code})
    if r.status_code == 200:
        driver.get(r.url)
        time.sleep(5)
        try:
            outer_download_button = driver.find_element(By.CLASS_NAME, 'icon-pdf').find_element(By.XPATH, '../../..')
            inner_buttons = outer_download_button.find_elements(By.TAG_NAME, 'i')
            button_html = [i.find_element(By.XPATH, '..').get_attribute('innerHTML') for i in inner_buttons]
            pdf_button_list = [PDF_re.search(html) for html in button_html]
            PDF_idx = [i for i, val in enumerate(pdf_button_list) if val != None]
            # scroll down b/c I think you need to do that for some reason
            driver.execute_script("window.scrollTo(0, 600)")
            if len(PDF_idx) == 1:
                pdf_download_icon = inner_buttons[PDF_idx[0]].find_element(By.XPATH,"//*[text()='PDF']")
                inner_download_button = pdf_download_icon.find_element(By.XPATH,'..')
            else:
                epub_button_list = [EPUB_re.search(html) for html in button_html]
                EPUB_idx = [i for i, val in enumerate(epub_button_list) if val != None]
                epub_download_icon = inner_buttons[PDF_idx[0]].find_element(By.XPATH,"//*[text()='EPUB']")
                inner_download_button = epub_download_icon.find_element(By.XPATH,'..')
                outer_download_button.click()
                inner_download_button.click()
            
            outer_download_button.click()
            inner_download_button.click()
            time.sleep(15)
            parent_tab = driver.current_window_handle
            chwd = driver.window_handles
            time.sleep(1)
            driver.switch_to.window(chwd[1])
            full_text_resp = requests.get(url = driver.current_url, headers = headers)
            if full_text_resp.status_code == 200:
                download_pdf(doi=doi, dest_folder=pdf_folder, content=full_text_resp.content)
            driver.close()
            driver.switch_to.window(parent_tab)
        except Exception as e:
            out.update({'error': e})
    log.append(out)

driver.quit()

# move epub files from downloads folder later
# epub_re = re.compile('\.epub')
# epub_file = list(filter())
# shutil.move()


