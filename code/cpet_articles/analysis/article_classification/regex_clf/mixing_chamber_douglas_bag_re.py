from pathlib import Path
import pandas as pd
import re
from tqdm import tqdm
from code.cpet_articles.analysis.helper_funcs.text_analysis import read_raw_text, get_surrounding_text, capitalize_substring
from code.cpet_articles.analysis.helper_funcs.comb_overlapping_str import string_list_overlap
from code.cpet_articles.utils.article_names import get_doi_suffix
from code.cpet_articles.utils.flatten_list import flatten_list
tqdm.pandas()

txt_file_paths = list(Path('/Users/antonhesse/Desktop/Anton/Education/UMN/Lab and Research/HSPL/CPET_scoping_review/data/cpet_articles/full_texts/txts').rglob('*.txt'))

bbb_df_path = Path('/Users/antonhesse/Desktop/Anton/Education/UMN/Lab and Research/HSPL/CPET_scoping_review/data/cpet_articles/text_analysis/bbb_articles.csv')
bbb_df = pd.read_csv(bbb_df_path, dtype='str')
# bbb_df['doi_suffix'] = bbb_df['doi'].apply(lambda x: get_doi_suffix(x))

bbb_article_paths = [path for path in txt_file_paths if path.stem in bbb_df['doi_suffix'].to_list()]

raw_text = []
for path in tqdm(bbb_article_paths):
    try:
        rt = read_raw_text(path)
        raw_text.append(rt)
    except FileNotFoundError as e:
        print(e)

txt_files = [path.stem for path in bbb_article_paths]
text_df = pd.DataFrame({
    'doi_suffix': txt_files,
    'path': bbb_article_paths,
    'text': raw_text})

def mixing_chamber_douglas_bag(text):
    # text = text.lower()
    mixing_chamber_re = re.compile(r'mixing.{0,2}chamber', re.DOTALL)
    douglas_bag_re = re.compile(r'douglas.{0,2}bag', re.DOTALL)

    re_list = [mixing_chamber_re, douglas_bag_re]

    out = [rl.findall(text) for rl in re_list if rl.search(text)]
    out = flatten_list(out)
    out = list(set(out))

    return out if out else False
    
text_df['mc_db'] = text_df['text'].progress_apply(lambda x: mixing_chamber_douglas_bag(x))

surrounding_text = []
for idx, row in tqdm(text_df.iterrows(), total=text_df.shape[0]):
    temp_list = []
    if isinstance(row['mc_db'], list):
        for term in row['mc_db']:
            temp = get_surrounding_text(phrase=term, text=row['text'], chars=250, gas_context=False)
            temp_list.append(temp)
        temp_list = [item for item in temp_list if item is not None]
        flat_list = flatten_list(temp_list)
        unique_list = list(set(flat_list))
        comb_text_list = string_list_overlap(str_list=unique_list, full_text=row['text']) # combine text together to eliminate some later reading
        if comb_text_list:
            surrounding_text.append(comb_text_list)
        else:
            surrounding_text.append(False)
    else:
        surrounding_text.append(False)

text_df['mc_db_text'] = surrounding_text
text_df[text_df['mc_db'] != False]


# this will help with reading later
surrounding_text_cap = []
for idx, row in tqdm(text_df.iterrows(), total=text_df.shape[0]):
    temp = []
    if row['mc_db_text']:
        for text in row['mc_db_text']:
            for term in row['mc_db']:
                if term in text:
                    text = capitalize_substring(main_string=text, sub_string=term)
            temp.append(text)
        surrounding_text_cap.append(temp)
    else:
        surrounding_text_cap.append(row['mc_db_text'])

text_df['mc_db_text'] = surrounding_text_cap


def bbb_text(text):
    # text = text.lower()
    bbb_re = re.compile(r'(?:breath.{0,5}breath)|(?:b[btx]b)', re.DOTALL)
    if bbb_re.search(text):
        out = bbb_re.findall(text)
        out = flatten_list(out)
        out = list(set(out))
        return out if out else False
    else:
        return False

text_df['bbb_terms'] = text_df['text'].progress_apply(lambda x: bbb_text(x))

surrounding_text = []
for idx, row in tqdm(text_df.iterrows(), total=text_df.shape[0]):
    temp_list = []
    if isinstance(row['bbb_terms'], list):
        for term in row['bbb_terms']:
            temp = get_surrounding_text(phrase=term, text=row['text'], chars=250, gas_context=False)
            temp_list.append(temp)
        temp_list = [item for item in temp_list if item is not None]
        flat_list = flatten_list(temp_list)
        unique_list = list(set(flat_list))
        comb_text_list = string_list_overlap(str_list=unique_list, full_text=row['text']) # combine text together to eliminate some later reading
        if comb_text_list:
            surrounding_text.append(comb_text_list)
        else:
            surrounding_text.append(False)
    else:
        surrounding_text.append(False)

text_df['bbb_text'] = surrounding_text
text_df[text_df['bbb'] != False]


# this will help with reading later
surrounding_text_cap = []
for idx, row in tqdm(text_df.iterrows(), total=text_df.shape[0]):
    temp = []
    if row['bbb_text']:
        for text in row['bbb_text']:
            for term in row['bbb_terms']:
                if term in text:
                    text = capitalize_substring(main_string=text, sub_string=term)
            temp.append(text)
        surrounding_text_cap.append(temp)
    else:
        surrounding_text_cap.append(row['bbb_text'])

text_df['bbb_text'] = surrounding_text_cap

mc_db_df = text_df[['doi_suffix', 'mc_db', 'mc_db_text', 'bbb', 'bbb_text']]
mc_db_df['doi_suffix'] = mc_db_df['doi_suffix'].astype('str')

file_path = Path('/Users/antonhesse/Desktop/Anton/Education/UMN/Lab and Research/HSPL/CPET_scoping_review/data/cpet_articles/text_analysis/mixing_chamber_douglas_bag.csv')
mc_db_df.to_clipboard(file_path, index=False)

# TODO add specific systems that are known NOT to be breath-by-breath
# e.g. Parvo 2400
# MedGraphics VO2000

def find_specific_systems(text):
    medgraphics_brand_re = re.compile(r'medgraphics|medical.{0,2}graphics|\smgc\s', re.DOTALL)
    megraphics_vo2000_re = re.compile(r'vo2000')

    re_list = [medgraphics_brand_re, megraphics_vo2000_re]

    # check if both the brand and model are found
    mo_list = [rl.search(text) for rl in re_list]
    
    # cosmed fitmate

    out = [rl.findall(text) for rl in re_list if rl.search(text)]
    out = flatten_list(out)
    out = list(set(out))

    return out if out else False