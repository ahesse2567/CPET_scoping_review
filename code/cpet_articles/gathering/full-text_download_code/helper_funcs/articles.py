from pathlib import Path
import pandas as pd
import re

def get_current_full_texts(
    folder='/Users/antonhesse/Desktop/Anton/Education/UMN/Lab and Research/HSPL/CPET_scoping_review/data/cpet_articles/full_texts',
    file_types=['pdf', 'txt', 'epub']
    ):
    
    folder = re.sub(r'/$', '', folder) # remove trailing '/' if present
    full_text_stems = []
    
    for type in file_types:
        paths = list(Path(f'{folder}/{type}s').glob(f'*.{type}'))
        stems = [path.stem for path in paths]
        full_text_stems.append(stems)

    full_texts = sum(full_text_stems, [])
    full_texts = list(set(full_texts)) # remove duplicates

    return full_texts

def get_doi_suffix(doi):
    doi_suffix = str(doi.split('/', 1)[1:]).strip("[']")
    fixed_doi_suffix = re.sub(r"""([()\\*,"': ?;<>])""", '_._', doi_suffix)
    return fixed_doi_suffix