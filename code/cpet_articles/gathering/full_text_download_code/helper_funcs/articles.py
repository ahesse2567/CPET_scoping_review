from pathlib import Path
import re
from tqdm import tqdm
from code.cpet_articles.utils.article_names import get_doi_suffix

def get_current_full_texts(
    folder='/Users/antonhesse/Desktop/Anton/Education/UMN/Lab and Research/HSPL/CPET_scoping_review/data/cpet_articles/full_texts',
    file_types=['pdf', 'txt', 'epub']
    ):
    
    folder = re.sub(r'/$', '', folder) # remove trailing '/' if present
    full_text_stems = []
    
    for type in tqdm(file_types):
        paths = list(Path(f'{folder}/{type}s').glob(f'*.{type}'))
        stems = [path.stem for path in paths]
        full_text_stems.append(stems)

    full_texts = sum(full_text_stems, [])
    full_texts = list(set(full_texts)) # remove duplicates

    return full_texts

def download_pdf(doi, dest_folder, content):
    doi_suffix = get_doi_suffix(doi)
    file_path = Path(dest_folder).joinpath(f'{doi_suffix}.pdf')
    with open(file_path, mode = 'wb') as f:
        f.write(content)

def close_extra_tabs(driver):
    driver.switch_to.window(driver.window_handles[0])
    parent_tab = driver.current_window_handle
    for handle in driver.window_handles:
        if handle != parent_tab:
            driver.switch_to.window(handle)
            driver.close()
    driver.switch_to.window(driver.window_handles[0])