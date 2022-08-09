from pathlib import Path
import shutil
import pandas as pd
import re
import sys
from tqdm import tqdm
sys.path.append('/Users/antonhesse/Desktop/Anton/Education/UMN/Lab and Research/HSPL/CPET_scoping_review/code/cpet_articles/gathering/full-text_download_code/')
from helper_funcs.articles import *

# this code was used to delete files from my original electronic search that were in Google Drive for manual analysis

# I've already deleted files locally not in the master list, but I also need to do the same thing to the files in Google Drive

all_articles = pd.read_csv('/Users/antonhesse/Desktop/Anton/Education/UMN/Lab and Research/HSPL/CPET_scoping_review/data/cpet_articles/unpaywall/unpaywall_info.csv')
all_articles['doi_suffix'] = all_articles['doi'].apply(lambda x: get_doi_suffix(x))

p = Path('/Users/antonhesse/Downloads/Manual PDF Analysis').glob('**/*')
files = [x for x in p if x.is_file()]

suffix_dict = {}
for f in files:
    suffix = f.suffix
    if suffix not in suffix_dict.keys():
        suffix_dict[suffix] = 1
    else:
        suffix_dict[suffix] += 1
suffix_dict # showing .pdf, .docx, and one file without an extension

no_ext_re = re.compile(r'[^.pdf]$')
list(filter(no_ext_re.search, list(map(str, files)))) # .DS_Store is getting picked up for some reason

# fix bad characters in file names
bad_chars_re = re.compile(r"""([()\\*,"': /?;<>]+)""")
for f in files:
    if (f.suffix == '.pdf') | (f.suffix == '.docx'):
        stem = f.stem
        stem = re.sub(r"""([()\\*,"': /?;<>])""", '_._', stem)
        stem = re.sub(r'(_._){2,}', '_._', stem)
        if f.stem != stem:
            new_path = str(f.parent / stem) + f.suffix
            shutil.move(f, stem)

stems = [f.stem for f in files]
list(filter(bad_chars_re.search, list(map(str, stems))))

p = Path('/Users/antonhesse/Downloads/Manual PDF Analysis').glob('**/*')
files = [x for x in p if x.is_file()]
len(files)

articles_not_in_master = []
for f in files:
    if (f.suffix == '.pdf') | (f.suffix == '.docx'):
        if f.stem not in all_articles['doi_suffix'].to_list():
            articles_not_in_master.append(f.stem)
len(articles_not_in_master)

for f in files:
    if f.stem in articles_not_in_master:
        dest = '/Users/antonhesse/Downloads/to_delete' + f.name
        try:
            shutil.move(f, dest)
        except FileNotFoundError as e:
            print(e)

        
len(articles_not_in_master)
articles_not_in_master

articles_not_in_master = [article for article in current_full_texts if article not in all_articles['doi_suffix']]

