from pathlib import Path
import pandas as pd
import re
from tqdm import tqdm
tqdm.pandas()
from code.cpet_articles.analysis.helper_funcs.comb_overlapping_str import *
from code.cpet_articles.analysis.helper_funcs.text_analysis import read_raw_text

def get_doi_suffix(doi):
    doi_suffix = str(doi.split('/', 1)[1:]).strip("[']")
    doi_suffix = re.sub(r"""([()\\*,"': /?;<>])""", '_._', doi_suffix) # remove bad chars
    doi_suffix = re.sub(r'(_._){2,}', '_._', doi_suffix) # remove multiple sequences of _._
    return doi_suffix

txt_file_paths = list(Path('/Users/antonhesse/Desktop/Anton/Education/UMN/Lab and Research/HSPL/CPET_scoping_review/data/cpet_articles/full_texts/txts').rglob('*.txt'))

bbb_articles = pd.read_csv('/Users/antonhesse/Desktop/Anton/Education/UMN/Lab and Research/HSPL/CPET_scoping_review/data/cpet_articles/text_analysis/bbb_articles.csv')
bbb_articles['doi_suffix'] = bbb_articles['doi'].apply(lambda x: get_doi_suffix(x))

bbb_article_paths = [path for path in txt_file_paths if path.stem in bbb_articles['doi_suffix'].to_list()]

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

def find_outlier_text(text):
    cough_re = re.compile(r'\s(?:cough(?:ing)?)', re.IGNORECASE) # cough is always included
    # at least one other term is required to accompany 'cough' in order to reference outliers
    weird_breath_re = re.compile(r'\s(?:swallow|sigh|talk|(?:throat.{0,2}clear|clear(?:ing)?.{0,2}throat))', re.DOTALL| re.IGNORECASE)

    error_synosyms_re = re.compile(r'\serrant|\saberrant', re.IGNORECASE) # these almost always refer to breaths
    # outlying, outlier, deviating, erroneous. These options sometimes appear but aren't reliable
    local_mean_re = re.compile(r'\slocal.{0,2}(?:mean|average)', re.DOTALL | re.IGNORECASE) # 'local mean' always refers to outliers
    
    # search for terms related to finding standard deviations
    # (?:breath|v.{0,3}o2).{0,175}?[^a-zA-Z0-9_.](?:three|four|3|4)\D{0,2}(?:sd|standard.{0,2}deviations?)\W|[^a-zA-Z0-9_.](?:three|four|3|4)\D{0,2}(?:sd|standard.{0,2}deviations?)\W(?:breath|v.{0,3}o2).{0,175}?
    sd_re = re.compile(r'''(
        (?:breath|v.{0,3}o2).{0,175}?[^a-zA-Z0-9_.](?:three|four|3|4)\D{0,2}(?:sd|standard.{0,2}deviations?)\W|
        [^a-zA-Z0-9_.](?:three|four|3|4)\D{0,2}(?:sd|standard.{0,2}deviations?)\W(?:breath|v.{0,3}o2).{0,175}?
    )''', re.IGNORECASE | re.DOTALL | re.VERBOSE)

    # v?\W{0,3}o2\b.{0,300}?out.{0,50}prediction.{0,2}(interval|band) |prediction.{0,2}(interval|band).{0,50}out.{0,300}?v\W{0,3}o2\b
    prediction_interval_re = re.compile(r'''(
        v?\W{0,3}o2\b.{0,300}?out.{0,50}prediction.{0,2}(?:interval|band)
        |prediction.{0,2}(?:interval|band).{0,50}out.{0,300}?v\W{0,3}o2\b)''', re.DOTALL | re.IGNORECASE | re.VERBOSE)
    # out.{0,20} needs to incldue 'out' as in outlier, outside, etc
    cough_breath_bool = all([cough_re.search(text), weird_breath_re.search(text)])
    other_bool = any([error_synosyms_re.search(text), local_mean_re.search(text),prediction_interval_re.search(text),sd_re.search(text)])

    if cough_breath_bool or other_bool:
        mo_list = [
            cough_re.findall(text),
            weird_breath_re.findall(text),
            error_synosyms_re.findall(text),
            local_mean_re.findall(text),
            prediction_interval_re.findall(text),
            sd_re.findall(text)]
        out = [mo for mo in mo_list if mo] # change to [mo[0] for mo in mo_list if mo] to only get string, not the list?
        return out
    else:
        return False

# import random
# n = random.randint(0, text_df.shape[0])
# text = text_df.loc[n,:]['text']
text = text_df.loc[text_df['doi_suffix'] == 'mss.0b013e318217d439',:]['text'].values[0]
find_outlier_text(text)

def get_surrounding_text(phrase, text, chars=100):
    esc_phrase = re.escape(phrase) # prevent escape character issues

    surrounding_text_re = re.compile(
        fr'''(.{{0,{chars}}}{esc_phrase}.{{0,{chars}}})''',
        re.IGNORECASE | re.DOTALL | re.VERBOSE)
    
    if surrounding_text_re.search(text):
        return surrounding_text_re.findall(text)

get_surrounding_text(' aberrant', text, chars=100)

text_df['outlier_terms'] = text_df['text'].progress_apply(lambda x: find_outlier_text(x))

row = text_df.loc[139,:]
row = text_df.loc[text_df['doi_suffix'] == 'mss.0b013e318217d439',:]
row

outlier_text = []
for i, row in tqdm(text_df.iterrows(), total=text_df.shape[0]):
    outlier_terms = row['outlier_terms']
    if outlier_terms:
        surrounding_text_lists = [get_surrounding_text(item, text=row['text'], chars=100) for terms in outlier_terms for item in terms]
        flat_list = [item for sublist in surrounding_text_lists for item in sublist]
        flat_list = list(set(flat_list)) # remove some duplicates

        # [o in other_o for i, o in enumerate(out) for other_o in out[:i] + out[i+1:]]
        substring_list = []
        for i, l in enumerate(flat_list):
            sub_list = flat_list[:i] + flat_list[i+1:]
            for s in sub_list:
                if l in s:
                    substring_list.append(l)

        flat_list = [l for l in flat_list if l not in substring_list]
        
        for i, l in enumerate(flat_list):
            print(f's{i} = """{l}"""')

        overlapping_strings = string_list_overlap(flat_list, full_text=row['text'])
        outlier_text.append(overlapping_strings)
        
    else:
        outlier_text.append(False)

text_df['outlier_text'] = outlier_text

# search the outlier text for the specific number of SD's they used as their cutoff?
# (?:prediction.{0,2}(?:band|interval))|(?:two|three|four|[2-4]).{0,2}(?:sd|standard.{0,2}deviations?)

# note, researchers appear to create a local mean based on a rolling average of a certain number of breaths
# It does not seem like they make a crazy GAM model with multiple inputs

# text_df[text_df['outlier_terms'] != False]
text_df[text_df['outlier_terms'] != False]
text_df[text_df['outlier_terms'] != False]['outlier_text'].apply(lambda x: len(x))
text_df[text_df['outlier_terms'] != False]['outlier_text'].apply(lambda x: len(x)).value_counts()

list_lens = text_df[text_df['outlier_terms'] != False]['outlier_text'].apply(lambda x: len(x))

text_df['list_lens'] = list_lens


def reorder_columns(dataframe, col_name, position):
    temp_col = dataframe[col_name] # store col to move
    dataframe = dataframe.drop(columns=[col_name]) # drop old position
    dataframe.insert(loc=position, column=col_name, value=temp_col) # insert at new position
    print(dataframe.columns)
    return dataframe
# load then merge with manual analysis df
manual_text_analysis_path = Path('/Users/antonhesse/Desktop/Anton/Education/UMN/Lab and Research/HSPL/CPET_scoping_review/data/cpet_articles/text_analysis/Manual text analysis - Data.csv')
manual_text_analysis_df = pd.read_csv(manual_text_analysis_path, dtype='str')

merge_df = pd.merge(manual_text_analysis_df.drop('outlier_terms', axis=1), text_df[['doi_suffix', 'outlier_terms', 'outlier_text']], how='outer', on='doi_suffix').drop_duplicates(subset='doi_suffix')
merge_df = reorder_columns(merge_df, 'outlier_terms', position=12)
merge_df = reorder_columns(merge_df, 'outlier_text', position=13)
merge_df['doi_suffix'] = merge_df['doi_suffix'].astype('str')
merge_df.to_clipboard(index=False)
merge_df['outlier_terms'].to_clipboard(index=False)
merge_df['outlier_text'].to_clipboard(index=False)
merge_df['doi_suffix'].to_clipboard(index=False)

# merge_df.loc[merge_df['doi_suffix'] == 'ajpregu.00015.2019',:]


# lump different cutoff amounts using the empiricle rule (68, 95, 99%)
# 95% = 2 SD (yes, it's techincally 1.96), 99% = 3 SD, 99.99% = 4 SD

# REMEMBER TO CLEAR THE NA VALUES IN THE OUTLIERS COLUMN LATER!
