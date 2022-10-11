from pathlib import Path
import pandas as pd
import re
from tqdm import tqdm
import sys
helper_funcs_path = Path('/Users/antonhesse/Desktop/Anton/Education/UMN/Lab and Research/HSPL/CPET_scoping_review/code/cpet_articles/analysis/')
sys.path.append(str(helper_funcs_path))
from helper_funcs.text_analysis import read_raw_text
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

parvomedics_re = re.compile(r'parvo\s?medics')
text_df['parvomedics'] = text_df['text'].progress_apply(lambda x: True if parvomedics_re.search(x) is not None else False)
text_df['parvomedics'].value_counts()

def medgraphics_bbb(text):
    brand_re = re.compile(r'medgraphics|medical.{0,2}graphics|\smgc\s', re.DOTALL)
    model_re = re.compile(r'ultima|cpx|pfx|ccm|cardio2')

    mo_list = [brand_re.search(text), model_re.search(text)]
    out = all(mo is not None for mo in mo_list)

    return out

text_df['medgraphics'] = text_df['text'].progress_apply(lambda x: medgraphics_bbb(x))
text_df['medgraphics'].value_counts()

def sensormedics_bbb(text):
    brand_re = re.compile(r'sensor\s?medics')
    model_re = re.compile(r'encore|2900')

    mo_list = [brand_re.search(text), model_re.search(text)]
    out = all(mo is not None for mo in mo_list)
    
    return out

text_df['sensormedics'] = text_df['text'].progress_apply(lambda x: sensormedics_bbb(x))
text_df['sensormedics'].value_counts()

def cosmed_bbb(text):
    brand_re = re.compile(r'cosmed')
    model_re = re.compile(r'quark|k[4,5]')

    mo_list = [brand_re.search(text), model_re.search(text)]
    out = all(mo is not None for mo in mo_list)
    
    return out

text_df['cosmed'] = text_df['text'].progress_apply(lambda x: cosmed_bbb(x))
text_df['cosmed'].value_counts()

def minato_bbb(text):
    brand_re = re.compile(r'minato')
    model_re = re.compile(r'ae-{0,1}[2,3][0,1]0|rm-{0,1}[2,3]00')

    mo_list = [brand_re.search(text), model_re.search(text)]
    out = all(mo is not None for mo in mo_list)
    
    return out

text_df['minato'] = text_df['text'].progress_apply(lambda x: minato_bbb(x))
text_df['minato'].value_counts()

text_df['pred_bbb'] = text_df[['bbb', 'oxycon', 'cosmed', 'carefusion', 'parvomedics', 'medgraphics', 'sensormedics', 'minato']].any(axis=1)
text_df['pred_bbb'].value_counts()

unpaywall_info_path = Path('/Users/antonhesse/Desktop/Anton/Education/UMN/Lab and Research/HSPL/CPET_scoping_review/data/cpet_articles/unpaywall/unpaywall_info.csv')
all_articles = pd.read_csv(unpaywall_info_path, dtype='str')
all_articles['doi_suffix'] = all_articles['doi'].apply(lambda x: get_doi_suffix(x))

merge_df = pd.merge(text_df, all_articles, how='inner', on='doi_suffix').drop_duplicates()

# load known ineligible articles
eligibility_path = Path('/Users/antonhesse/Desktop/Anton/Education/UMN/Lab and Research/HSPL/CPET_scoping_review/data/cpet_articles/text_analysis/Manual text analysis - eligibility.csv')
elgibility_df = pd.read_csv(eligibility_path)
ineligible_articles = elgibility_df[elgibility_df['eligible']==False]['doi_suffix'].to_list()

# [str(path) for path in txt_file_paths if path.stem == 'mss.0000000000001353'][0]

merge_df = merge_df[~merge_df['doi_suffix'].isin(ineligible_articles)] # remove inelgible articles
bbb_df = merge_df[merge_df['pred_bbb'] == True].drop('text', axis=1).reset_index(drop=True)
bbb_df = bbb_df.sample(frac=1, random_state=22).reset_index(drop=True)
bbb_df['doi_suffix'] = bbb_df['doi_suffix'].astype('str')
bbb_df.to_csv('/Users/antonhesse/Desktop/Anton/Education/UMN/Lab and Research/HSPL/CPET_scoping_review/data/cpet_articles/text_analysis/bbb_articles.csv', index=False)

# 'mss.0000000000001353' in bbb_df['doi_suffix'].to_list()