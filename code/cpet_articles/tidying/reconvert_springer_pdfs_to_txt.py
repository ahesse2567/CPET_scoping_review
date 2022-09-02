import subprocess
from pathlib import Path
from tqdm import tqdm
import re
import pandas as pd
import itertools
import random
import sys
sys.path.append('/Users/antonhesse/Desktop/Anton/Education/UMN/Lab and Research/HSPL/CPET_scoping_review/code/cpet_articles/gathering/full-text_download_code/')
from helper_funcs.articles import get_current_full_texts, get_doi_suffix


all_articles = pd.read_csv('/Users/antonhesse/Desktop/Anton/Education/UMN/Lab and Research/HSPL/CPET_scoping_review/data/cpet_articles/unpaywall/unpaywall_info.csv')
articles = all_articles[all_articles['publisher'].str.contains('springer', case=False, regex=True, na=False)].reset_index(drop=True)
articles['doi_suffix'] = articles['doi'].apply(lambda x: get_doi_suffix(x))

# determine which pdfs need to be redownloaded
# find all PDF paths
existing_pdf_file_paths = list(Path('/Users/antonhesse/Desktop/Anton/Education/UMN/Lab and Research/HSPL/CPET_scoping_review/data/cpet_articles/full_texts/pdfs').glob('*.pdf'))
existing_pdf_file_paths = list(set(existing_pdf_file_paths)) # remove potential duplicates
existing_pdf_stems = [path.stem for path in existing_pdf_file_paths]

existing_file_paths_df = pd.DataFrame({
    'doi_suffix': existing_pdf_stems,
    'file_path': existing_pdf_file_paths
})

articles = pd.merge(existing_file_paths_df, articles, how='inner', on='doi_suffix')

"""
n = random.randint(0, articles.shape[0])
file_path = articles.loc[n, 'file_path']
file_path
"""

def pdf_to_txt(file_path):
    pdf_stem = Path(file_path).stem
    log = {'doi_suffix': str(pdf_stem)}
    txt_folder_path = re.sub(r'/pdfs/', '/txts/', str(file_path))
    txt_file_path = re.sub(r'.pdf', '.txt', txt_folder_path)
    cmd = f"'/Users/antonhesse/opt/anaconda3/bin/pdf2txt.py' -o '{txt_file_path}' '{file_path}'"
    run = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    try:
        out, err = run.communicate(timeout=90)
        if err:
            log.update({'error': err})
            print(err)
    except Exception as e:
        run.kill()
        out, err = run.communicate()
        if err:
            log.update({'error': err})
            print(err) # display errors if they occur

    return log

log_list = [pdf_to_txt(path) for path in tqdm(articles['file_path'].to_list())]

log_df = pd.DataFrame(log_list)
conv_errors_path = '/Users/antonhesse/Desktop/Anton/Education/UMN/Lab and Research/HSPL/CPET_scoping_review/data/cpet_articles/unpaywall/pdf2txt_conv_errors.csv'
log_df.to_csv(conv_errors_path, mode='a', index=False, header=False)

"""
# after running this loop, move all txt files from pdf folders into txt folders
n = random.randint(0, len(pdf_file_paths_to_convert))
f = pdf_file_paths_to_convert[n]
f

errors = {}
for f in tqdm(pdf_file_paths_to_convert):
    txt_filename = f.split('.pdf')[0]
    cmd = '/Users/antonhesse/opt/anaconda3/bin/pdf2txt.py -o %s.txt %s' % (txt_filename, f)
    run = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    try:
        out, err = run.communicate(timeout=90)
        if err:
            errors.update({f: err})
            print(err) # display errors if they occur
    except Exception as e:
        run.kill()
        out, err = run.communicate()
        if err:
            errors.update({f: err})
            print(err) # display errors if they occur
"""

"""
Old code from copied file below


# find txt files and stems
existing_txt_file_paths = list(Path('/Users/antonhesse/Desktop/Anton/Education/UMN/Lab and Research/HSPL/CPET_scoping_review/data/cpet_articles/full_texts/txts').glob('*.txt'))
existing_txt_files = [path.stem for path in existing_txt_file_paths]

full_text_folders = [folder for folder in list(Path('/Users/antonhesse/Desktop/Anton/Education/UMN/Lab and Research/HSPL/CPET_scoping_review/data/cpet_articles/full_texts').iterdir()) if folder.is_dir()]
txt_error_folders = ['non-english', 'empty_txt_conv', 'pdf_to_txt_parsing_error']
txt_error_folders_paths = [folder for folder in full_text_folders if folder.name in txt_error_folders]
#  find txt error files
txt_error_file_path_list = [path.glob('*.txt') for path in txt_error_folders_paths]
txt_error_file_paths = list(itertools.chain.from_iterable(txt_error_file_path_list))
# find PDF files
existing_pdf_file_paths = list(Path('/Users/antonhesse/Desktop/Anton/Education/UMN/Lab and Research/HSPL/CPET_scoping_review/data/cpet_articles/full_texts/pdfs').glob('*.pdf'))
existing_pdf_file_paths = list(set(existing_pdf_file_paths)) # remove potential duplicates
len(existing_pdf_file_paths)
existing_pdf_files = [path.stem for path in existing_pdf_file_paths]
# determine PDFs that have yet to be converted
txt_error_files = [path.stem for path in txt_error_file_paths]
pdfs_to_convert = [pdf for pdf in existing_pdf_files if pdf not in existing_txt_files and pdf not in txt_error_files]
len(pdfs_to_convert)

"""