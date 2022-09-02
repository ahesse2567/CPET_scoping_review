from distutils import text_file
from pathlib import Path
import pandas as pd
import shutil
from tqdm import tqdm
import sys
sys.path.append('/Users/antonhesse/Desktop/Anton/Education/UMN/Lab and Research/HSPL/CPET_scoping_review/code/cpet_articles/gathering/full-text_download_code/')
from helper_funcs.articles import get_doi_suffix
# import send2trash

status_codes_df = pd.read_csv('/Users/antonhesse/Desktop/Anton/Education/UMN/Lab and Research/HSPL/CPET_scoping_review/data/cpet_articles/unpaywall/springer_status_codes.csv')
status_codes_df['doi_suffix'] = status_codes_df['doi'].apply(lambda x: get_doi_suffix(x))
errors_df = status_codes_df[~status_codes_df['error'].isna()].reset_index(drop=True)

full_text_file_paths = list(Path('/Users/antonhesse/Desktop/Anton/Education/UMN/Lab and Research/HSPL/CPET_scoping_review/data/cpet_articles/full_texts').rglob('*'))

dest_folder = Path('/Users/antonhesse/Desktop/files_to_delete')

for path in tqdm(full_text_file_paths):
    try:
        if path.stem in errors_df['doi_suffix'].to_list():
            shutil.move(str(path), dest_folder)
    except FileNotFoundError as e:
        print(e)

