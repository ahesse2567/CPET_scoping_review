from pathlib import Path
import pandas as pd
import re
from tqdm import tqdm
tqdm.pandas()
from code.cpet_articles.analysis.helper_funcs.comb_overlapping_str import string_list_overlap
from code.cpet_articles.analysis.helper_funcs.text_analysis import read_raw_text, capitalize_substring
from code.cpet_articles.utils.article_names import get_doi_suffix

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

interpolate_re = re.compile(r'.{0,200}interpolat.{0,200}', re.DOTALL)

text_df['interpolation_text'] = text_df['text'].progress_apply(lambda x: interpolate_re.findall(x) if re.search(r'interpolat', x) else False)
text_df[text_df['interpolation_text'] != False]
# text_df['interpolate'].value_counts()
interpolation_details_re = re.compile(r'^(?=.*(gas|breath|v.{0,2}o2))(?=.*(\d.{0,2}s(?:econd)?\b|second.{0,2}by.{0,2}second|\d.{0,2}hz)).*$', re.DOTALL)
comb_text_list = []
gas_texts = []
for i, row in tqdm(text_df.iterrows(), total=text_df.shape[0]):
    if isinstance(row['interpolation_text'], list):
        comb_text = string_list_overlap(row['interpolation_text'], row['text'])
        comb_text_list.append(comb_text)
        temp = [ct for ct in comb_text if interpolation_details_re.search(re.escape(ct))]
        if temp:
            gas_texts.append(temp)
        else:
            gas_texts.append(False)
    else:
        comb_text_list.append(False)
        gas_texts.append(False)

text_df['interpolation_text'] = comb_text_list
# text_df['gas_interpolation_text'] = gas_texts

# this will help with reading later
surrounding_text_cap = []
for idx, row in tqdm(text_df.iterrows(), total=text_df.shape[0]):
    temp = []
    if row['interpolation_text']:
        for text in row['interpolation_text']:
            text = capitalize_substring(main_string=text, sub_string='interpolat')
            temp.append(text)
        surrounding_text_cap.append(temp)
    else:
        surrounding_text_cap.append(row['interpolation_text'])

text_df['interpolation_text'] = surrounding_text_cap

# interpolation_df = text_df[text_df['interpolation_text'] != False]['interpolation_text']
# interpolation_df
# text_df['interpolation_details'] = text_df['interpolation_text'].progress_apply(lambda x: [l for l in x if interpolation_details_re.search(l) else False])

manual_text_analysis_path = Path('/Users/antonhesse/Desktop/Anton/Education/UMN/Lab and Research/HSPL/CPET_scoping_review/data/cpet_articles/text_analysis/Interpolation - Interpolation.csv')
manual_text_analysis_df = pd.read_csv(manual_text_analysis_path, dtype='str')

manual_text_analysis_df = manual_text_analysis_df[['done', 'doi_suffix','Data Processing Text',
'Interpolation type', 'Interpolation time (s)', 'Notes']]

merge_df = pd.merge(manual_text_analysis_df, text_df[['doi_suffix', 'interpolation_text']], how='outer', on='doi_suffix').drop_duplicates(subset='doi_suffix')

def reorder_columns(dataframe, col_name, position):
    temp_col = dataframe[col_name] # store col to move
    dataframe = dataframe.drop(columns=[col_name]) # drop old position
    dataframe.insert(loc=position, column=col_name, value=temp_col) # insert at new position
    print(dataframe.columns)
    return dataframe

merge_df = reorder_columns(merge_df, 'interpolation_text', position=3)
merge_df.columns
merge_df['doi_suffix'] = merge_df['doi_suffix'].astype('str')
merge_df.to_clipboard(index=False)