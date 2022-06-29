import pandas as pd
from pathlib import Path
import re
import shutil
from tqdm import tqdm

project_folder = '/Users/antonhesse/Desktop/Anton/Education/UMN/Lab and Research/HSPL/CPET_scoping_review'

p = Path(project_folder)
pdf_folder = p / 'data' / 'cpet_articles' / 'pdfs'
txt_folder = p / 'data' / 'cpet_articles' / 'txts'

##### Moving PDF files

pdf_paths = [path for path in pdf_folder.glob('**/*.pdf')]
len(pdf_paths)
pdf_doi_suffixes = [re.sub(r'.pdf', '', path.name) for path in pdf_paths]
len(pdf_doi_suffixes)
# find which doi_suffixes are NOT in the current unpaywall_info.csv file

unpaywall_info = pd.read_csv(p / 'data' / 'cpet_articles' / 'unpaywall' / 'unpaywall_info.csv')
unpaywall_doi_suffixes = unpaywall_info['doi'].apply(lambda x: str(x.split('/')[1:]).strip("[']"))

no_exer_pdf_files = list(set(pdf_doi_suffixes).difference(unpaywall_doi_suffixes))
len(no_exer_pdf_files)
# no_exer_files[0]

no_exer_pdf_folder = p / 'data' / 'cpet_articles' / 'no_exer' / 'pdfs'

for f in tqdm(no_exer_pdf_files, total=len(no_exer_pdf_files)):
    old_f_path = next(pdf_folder.glob(f'**/*{f}.pdf'))
    new_f_path = no_exer_pdf_folder / f'{f}.pdf'
    try:
        shutil.move(old_f_path, new_f_path)
    except Exception as e:
        print(e)


##### Moving txt files

txt_paths = [path for path in txt_folder.glob('*.txt')]
len(txt_paths)
txt_doi_suffixes = [re.sub(r'.txt', '', path.name) for path in txt_paths]
len(txt_doi_suffixes)
# find which doi_suffixes are NOT in the current unpaywall_info.csv file

unpaywall_info = pd.read_csv(p / 'data' / 'cpet_articles' / 'unpaywall' / 'unpaywall_info.csv')
unpaywall_doi_suffixes = unpaywall_info['doi'].apply(lambda x: str(x.split('/')[1:]).strip("[']"))

no_exer_txt_files = list(set(txt_doi_suffixes).difference(unpaywall_doi_suffixes))
len(no_exer_txt_files)
# no_exer_files[0]

no_exer_txt_folder = p / 'data' / 'cpet_articles' / 'no_exer' / 'txts'

for f in tqdm(no_exer_txt_files, total=len(no_exer_txt_files)):
    old_f_path = next(txt_folder.glob(f'**/*{f}.txt'))
    new_f_path = no_exer_txt_folder / f'{f}.txt'
    try:
        shutil.move(old_f_path, new_f_path)
    except Exception as e:
        print(e)