from cgitb import text
from pathlib import Path
import pandas as pd
import re
from tqdm import tqdm
import sys
helper_funcs_path = Path('/Users/antonhesse/Desktop/Anton/Education/UMN/Lab and Research/HSPL/CPET_scoping_review/code/cpet_articles/analysis/')
sys.path.append(str(helper_funcs_path))
from helper_funcs.text_analysis import tokenize_file, read_raw_text
tqdm.pandas()

def get_doi_suffix(doi):
    doi_suffix = str(doi.split('/', 1)[1:]).strip("[']")
    doi_suffix = re.sub(r"""([()\\*,"': /?;<>])""", '_._', doi_suffix) # remove bad chars
    doi_suffix = re.sub(r'(_._){2,}', '_._', doi_suffix) # remove multiple sequences of _._
    return doi_suffix

txt_file_paths = list(Path('/Users/antonhesse/Desktop/Anton/Education/UMN/Lab and Research/HSPL/CPET_scoping_review/data/cpet_articles/full_texts/txts').rglob('*.txt'))

raw_text = []
for path in tqdm(txt_file_paths):
    try:
        rt = read_raw_text(path)
        raw_text.append(rt)
    except FileNotFoundError as e:
        print(e)

txt_files = [path.stem for path in txt_file_paths]
text_df = pd.DataFrame({
    'doi_suffix': txt_files,
    'path': txt_file_paths,
    'text': raw_text})

bbb_re = re.compile(r'(breath.{0,5}breath)|(b[btx]b)', re.DOTALL)

text_df['bbb'] = text_df['text'].progress_apply(lambda x: True if bbb_re.search(x) is not None else False)
text_df['bbb'].value_counts()

oxycon_re = re.compile(r'oxycon')
text_df['oxycon'] = text_df['text'].progress_apply(lambda x: True if oxycon_re.search(x) is not None else False)
text_df['oxycon'].value_counts()

carefusion_re = re.compile(r'carefusion')
text_df['carefusion'] = text_df['text'].progress_apply(lambda x: True if carefusion_re.search(x) is not None else False)
text_df['carefusion'].value_counts()

parvomedics_re = re.compile(r'parvomedics')
text_df['parvomedics'] = text_df['text'].progress_apply(lambda x: True if parvomedics_re.search(x) is not None else False)
text_df['parvomedics'].value_counts()

def medgraphics_bbb(text):
    medgraphics_brand_re = re.compile(r'medgraphics|medical.{0,2}graphics', re.DOTALL)
    medgraphics_model_re = re.compile(r'ultima|cpx|pfx|ccm|cardio2')

    mo_list = [medgraphics_brand_re.search(text), medgraphics_model_re.search(text)]
    out = all(mo is not None for mo in mo_list)

    return out

text_df['medgraphics'] = text_df['text'].progress_apply(lambda x: medgraphics_bbb(x))
text_df['medgraphics'].value_counts()

def sensormedics_bbb(text):
    brand_re = re.compile(r'sensormedics')
    model_re = re.compile(r'encore|2900')

    mo_list = [brand_re.search(text), model_re.search(text)]
    out = all(mo is not None for mo in mo_list)
    
    return out

text_df['sensormedics'] = text_df['text'].progress_apply(lambda x: sensormedics_bbb(x))
text_df['sensormedics'].value_counts()

def cosmed_bbb(text):
    cosmed_brand_re = re.compile(r'cosmed')
    cosmed_model_re = re.compile(r'quark|k[4,5]')

    mo_list = [cosmed_brand_re.search(text), cosmed_model_re.search(text)]
    out = all(mo is not None for mo in mo_list)
    
    return out

text_df['cosmed'] = text_df['text'].progress_apply(lambda x: cosmed_bbb(x))
text_df['cosmed'].value_counts()



unpaywall_info_path = Path('/Users/antonhesse/Desktop/Anton/Education/UMN/Lab and Research/HSPL/CPET_scoping_review/data/cpet_articles/unpaywall/unpaywall_info.csv')
all_articles = pd.read_csv(unpaywall_info_path)
all_articles['doi_suffix'] = all_articles['doi'].apply(lambda x: get_doi_suffix(x))

merge_df = pd.merge(text_df, all_articles, how='inner', on='doi_suffix').drop_duplicates()
bbb_df = merge_df[merge_df['bbb'] == True].drop('text', axis=1).reset_index(drop=True)
bbb_df.to_csv('/Users/antonhesse/Desktop/Anton/Education/UMN/Lab and Research/HSPL/CPET_scoping_review/data/cpet_articles/text_analysis/bbb_articles.csv', index=False)