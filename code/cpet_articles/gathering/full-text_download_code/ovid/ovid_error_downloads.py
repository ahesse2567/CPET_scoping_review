# selenium 4
from selenium import webdriver
from selenium.webdriver.firefox.service import Service as FirefoxService
from sympy import rem
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
import sys
sys.path.append('code/cpet_articles/gathering/full-text_download_code/')
from helper_funcs.articles import get_current_full_texts
#### WARNING #### DELETE ALL EPUBS AND PDFS FROM DOWNLOADS FOLDER PRIOR TO RUNNING THIS CODE
# IF YOU DON'T, YOU'LL MISNAME THE FILES

# For some reason when I used to click on the inner pdf download button, I would get to the
# page where the pdf was and need to use requests.get() to get the content in bytes
# now for some reason when I click the download button it downloads straight to the
# download folder. See previous commits for older code

def download_ovid_full_text(doi, headers, dest_folder, driver, quit_driver=False):
    out = {'doi': doi}
    doi_url = 'https://doi.org/' + doi
    try:
        doi_resp = requests.get(doi_url, headers=headers)
        out.update({'doi_redirect_SC': doi_resp.status_code})
        if doi_resp.status_code == 200:
            driver.get(doi_resp.url)
            time.sleep(3) # seems to let advertisement close
            driver.execute_script("window.scrollTo(0, 100)")
            outer_download_button, inner_download_button, button_type = find_buttons(driver)
            outer_download_button.click()
            inner_download_button.click()
            if button_type == 'pdf':
                time.sleep(15) # allow for download time
                parent_tab = driver.current_window_handle
                chwd = driver.window_handles
                time.sleep(1) # might help with switching windows
                driver.switch_to.window(chwd[1])
                # full_text_resp = requests.get(url = driver.current_url, headers = headers)
                # out.update({'full_text_SC': full_text_resp.status_code})
                # if full_text_resp.status_code == 200:
                #     download_pdf(doi=doi, dest_folder=dest_folder, content=full_text_resp.content)
                driver.close()
                driver.switch_to.window(parent_tab)
                pdfs_in_downloads_paths = list(Path('/Users/antonhesse/Downloads').glob('*.pdf'))
                if len(pdfs_in_downloads_paths) > 1:
                    for path in pdfs_in_downloads_paths:
                        Path.unlink(path)
                else:
                    doi_suffix = str(doi.split('/', 1)[1:]).strip("[']")
                    new_path = 'data/cpet_articles/full_texts/pdfs/' + doi_suffix + '.pdf'
                    shutil.move(src=epubs_in_downloads_paths[0], dst=new_path)
            elif button_type == 'epub':
                time.sleep(5) # allow for download time
                # epubs are automatically downloaded so I need to change the file name
                epubs_in_downloads_paths = list(Path('/Users/antonhesse/Downloads').glob('*.epub'))
                if len(epubs_in_downloads_paths) > 1:
                    for path in epubs_in_downloads_paths:
                        Path.unlink(path)
                else:
                    doi_suffix = str(doi.split('/', 1)[1:]).strip("[']")
                    new_path = 'data/cpet_articles/full_texts/epubs/ovid_non_oa/' + doi_suffix + '.epub'
                    shutil.move(src=epubs_in_downloads_paths[0], dst=new_path)
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
        button_type = 'pdf'
    else:
        EPUB_re = re.compile('EPUB')
        epub_button_list = [EPUB_re.search(html) for html in button_html]
        EPUB_idx = [i for i, val in enumerate(epub_button_list) if val != None]
        epub_download_icon = inner_buttons[EPUB_idx[0]].find_element(By.XPATH,"//*[text()='EPUB']")
        inner_download_button = epub_download_icon.find_element(By.XPATH,'..')
        button_type = 'epub'
    
    return outer_download_button, inner_download_button, button_type


all_articles = pd.read_csv('/Users/antonhesse/Desktop/Anton/Education/UMN/Lab and Research/HSPL/CPET_scoping_review/data/cpet_articles/unpaywall/unpaywall_info.csv')
re_doi_suffix = re.compile(r'(?<=\d/).*')
all_articles['doi_suffix'] = all_articles['doi'].apply(lambda x: re_doi_suffix.search(x).group())

current_full_texts = get_current_full_texts()

full_texts_to_download = [x for x in all_articles['doi_suffix'].tolist() if x not in current_full_texts]

remaining_articles = pd.merge(pd.DataFrame({'doi_suffix': full_texts_to_download}), all_articles, how='inner', on='doi_suffix')
articles = remaining_articles[remaining_articles['publisher'] == 'Ovid Technologies (Wolters Kluwer Health)'].drop_duplicates().reset_index(drop=True)


headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:102.0) Gecko/20100101 Firefox/102.0'}
dest_folder = 'data/cpet_articles/full_texts/pdfs/'

driver = webdriver.Firefox(service=FirefoxService(GeckoDriverManager().install()))
driver.implicitly_wait(5) # hopefully let's JS load correctly

log = []
for idx, row in tqdm(articles.iterrows(), total=articles.shape[0]):
    doi = row['doi']
    out = download_ovid_full_text(
        doi=doi,
        headers=headers,
        dest_folder=dest_folder,
        driver=driver,
        quit_driver=False
    )
    log.append(out)

driver.quit()
# idx
# sometimes it might be scrolling too far down
log_df = pd.DataFrame(log)
error_df = log_df[(~log_df['error'].isnull()) | (log_df['doi_redirect_SC'] != 200) | (log_df['full_text_SC'] != 200)]
error_df.to_csv('')
# update errors



"""
# single download for troubleshooting

driver = webdriver.Firefox(service=FirefoxService(GeckoDriverManager().install()))
driver.implicitly_wait(5) # hopefully let's JS load correctly

n = random.randint(0, articles.shape[0])
doi = articles.loc[n, 'doi']
doi_url = 'https://doi.org/' + doi
out = {'doi': doi}

doi_resp = requests.get(doi_url, headers=headers)
out.update({'doi_redirect_SC': doi_resp.status_code})
if doi_resp.status_code == 200:
    driver.get(doi_resp.url)
    time.sleep(1)
driver.execute_script("window.scrollTo(0, 550)")
outer_download_button, inner_download_button, button_type = find_buttons(driver)

outer_download_button.click()
inner_download_button.click()

if button_type == 'pdf':
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
elif button_type == 'epub':
    # epubs are automatically downloaded so I need to change the file name
    epubs_in_downloads_paths = list(Path('/Users/antonhesse/Downloads').glob('*.epub'))
    assert len(epubs_in_downloads_paths) == 1, 'More than one EPUB in Downloads folder'
    doi_suffix = str(doi.split('/', 1)[1:]).strip("[']")
    new_epub_path = 'data/cpet_articles/full_texts/epubs/ovid_non_oa/' + doi_suffix + '.epub'
    shutil.move(src=epubs_in_downloads_paths[0], dst=new_epub_path)
"""

# The following code snippets subsetted the articles by error type

# re_not_clickable = re.compile(r'not clickable')
# merge['not_clickable'] = merge['error'].apply(lambda x: re_not_clickable.search(str(x)) != None)
# not_clickable_df = merge[merge['not_clickable']]
# not_clickable_df.shape

# re_list_index = re.compile(r'list index out of range')
# merge['list_index'] = merge['error'].apply(lambda x: re_list_index.search(str(x)) != None)
# list_index_df = merge[merge['list_index']].reset_index(drop=True)
# list_index_df.shape

# re_locate_window = re.compile(r'Unable to locate window')
# error_df['locate_window'] = error_df['error'].apply(lambda x: re_locate_window.search(str(x)) != None)
# unable_locate_window_df = error_df[error_df['locate_window']].reset_index(drop=True)
# unable_locate_window_df.shape

# re_locate_element = re.compile(r'Unable to locate element')
# error_df['locate_icon-pdf'] = error_df['error'].apply(lambda x: re_locate_element.search(str(x)) != None)
# unable_locate_df = error_df[error_df['locate_icon-pdf']].reset_index(drop=True)
# unable_locate_df.shape

# n = random.randint(0, unable_locate_df.shape[0])
# doi = unable_locate_df.loc[n, 'doi']
# doi_url = 'https://doi.org/' + doi
# out = {'doi': doi}

# try:
#     doi_resp = requests.get(doi_url, headers=headers)
#     out.update({'doi_redirect_SC': doi_resp.status_code})
#     if doi_resp.status_code == 200:
#         driver.get(doi_resp.url)
#         # time.sleep(1)
#     outer_download_button, inner_download_button = find_buttons(driver)
#     driver.execute_script("window.scrollTo(0, 550)")
#     outer_download_button.click()
#     inner_download_button.click()

#     time.sleep(15)
#     parent_tab = driver.current_window_handle
#     chwd = driver.window_handles
#     time.sleep(1)
#     driver.switch_to.window(chwd[1])
#     full_text_resp = requests.get(url = driver.current_url, headers = headers)
#     if full_text_resp.status_code == 200:
#         download_pdf(doi=doi, dest_folder=dest_folder, content=full_text_resp.content)
#     driver.close()
#     driver.switch_to.window(parent_tab)
# except Exception as e:
#     print(e)
#     out.update({'error': e})
# if quit_driver == True:
#     driver.quit()

