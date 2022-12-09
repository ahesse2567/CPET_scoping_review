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
# import shutil
from code.cpet_articles.utils.article_names import get_doi_suffix
from code.cpet_articles.gathering.full_text_download_code.helper_funcs.articles import download_pdf, close_extra_tabs

downloaded_articles = pd.read_csv(str(Path('data/cpet_articles/unpaywall/downloaded_articles.csv')))
# downloaded_articles['doi_suffix'] = downloaded_articles['doi'].apply(lambda x: get_doi_suffix(x))

all_articles = pd.read_csv(str(Path('data/cpet_articles/unpaywall/unpaywall_info.csv')))
all_articles['doi_suffix'] = all_articles['doi'].apply(lambda x: get_doi_suffix(x))

remaining_articles = all_articles[~all_articles['doi_suffix'].isin(downloaded_articles['doi_suffix'].to_list())]
articles = remaining_articles[remaining_articles['publisher'] == 'Informa UK Limited'].drop_duplicates().reset_index(drop=True)

headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:102.0) Gecko/20100101 Firefox/102.0'}
dest_folder = Path('data/cpet_articles/full_texts/pdfs')

driver = webdriver.Firefox(service=FirefoxService(GeckoDriverManager().install()))
driver.implicitly_wait(1) # hopefully let's JS load correctly


# import random
# n = random.randint(0, articles.shape[0])
# row = articles.loc[n,:]

# n = 3
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

            pdf_link = driver.find_element(By.XPATH, "//a[@class='show-pdf' and @role='button']")
            pdf_link.click()
            # pdf_link = pdf_link.get_attribute('href')
            # pdf_link
            # r = requests.get(pdf_link, headers=headers, allow_redirects=True)
            
            time.sleep(2) # might help with switching windows

            # driver.current_window_handle

            parent_tab = driver.current_window_handle
            for handle in driver.window_handles:
                if handle != parent_tab:
                    driver.switch_to.window(handle)

            # driver.switch_to.window(parent_tab)
            
            # download_button = driver.find_element(By.XPATH, "//button[@id='download']")
            # download_button.click()

            r = requests.get(driver.current_url, headers=headers, allow_redirects=True, verify=True)
            out.update({'download_SC': r.status_code})
            pdf_folder_path = Path.cwd() / 'data' / 'cpet_articles' / 'full_texts' / 'pdfs'
            doi_suffix = get_doi_suffix(doi)
            download_pdf(doi=doi, dest_folder=pdf_folder_path, content=r.content)

            close_extra_tabs(driver=driver)
            # close_extra_tabs(driver)
            # # move PDF from downloads to pdf folder
            # pdfs_in_downloads_paths = list(Path('/Users/antonhesse/Downloads').glob('*.pdf'))
            # if len(pdfs_in_downloads_paths) > 1:
            #     for path in pdfs_in_downloads_paths:
            #         Path.unlink(path)
            # else:
            #     doi_suffix = get_doi_suffix(doi)
            #     new_path = '/Users/antonhesse/Desktop/Anton/Education/UMN/Lab and Research/HSPL/CPET_scoping_review/data/cpet_articles/full_texts/pdfs/' + doi_suffix + '.pdf'
            #     shutil.move(src=pdfs_in_downloads_paths[0], dst=new_path)
            #     time.sleep(2)
            # wait(5) # wait so our IP address isn't blocked
    except Exception as e:
        print(e)
        out.update({'error': e})
        close_extra_tabs(driver)
    log.append(out)

log_df = pd.DataFrame(log)
log_df[~log_df['download_SC'].isnull()]