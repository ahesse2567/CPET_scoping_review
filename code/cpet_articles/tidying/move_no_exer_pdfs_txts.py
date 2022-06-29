import pandas as pd
from pathlib import Path
import re
import shutil
from tqdm import tqdm

project_folder = '/Users/antonhesse/Desktop/Anton/Education/UMN/Lab and Research/HSPL/CPET_scoping_review'

p = Path(project_folder)
pdf_folder = p / 'data' / 'cpet_articles' / 'pdfs'
txt_folder = p / 'data' / 'cpet_articles' / 'txts'

pdf_paths = [path for path in pdf_folder.glob('**/*.pdf')]
len(pdf_paths)
doi_suffixes = [re.sub(r'.pdf', '', path.name) for path in pdf_paths]
len(doi_suffixes)
# find which doi_suffixes are NOT in the current unpaywall_info.csv file

unpaywall_info = pd.read_csv(p / 'data' / 'cpet_articles' / 'unpaywall' / 'unpaywall_info.csv')
unpaywall_doi_suffixes = unpaywall_info['doi'].apply(lambda x: str(x.split('/')[1:]).strip("[']"))

no_exer_files = list(set(doi_suffixes).difference(unpaywall_doi_suffixes))
len(no_exer_files)
# no_exer_files[0]

no_exer_folder = p / 'data' / 'cpet_articles' / 'no_exer' / 'pdfs'

for f in tqdm(no_exer_files, total=len(no_exer_files)):
    old_f_path = next(pdf_folder.glob(f'**/*{f}.pdf'))
    new_f_path = no_exer_folder / f'{f}.pdf'
    try:
        shutil.move(old_f_path, new_f_path)
    except Exception as e:
        print(e)