from pathlib import Path
import pandas as pd
import re
from tqdm import tqdm
from code.cpet_articles.analysis.helper_funcs.text_analysis import read_raw_text
from code.cpet_articles.utils.article_names import get_doi_suffix
tqdm.pandas()

try: # this feels hacky, but I should be able to run this program from the terminal and while tinkering in VScode
    if __file__:
        txt_folder = Path.cwd() / 'data' / 'cpet_articles' / 'full_texts' / 'txts'
        txt_file_paths = list(txt_folder.rglob('*.txt'))
except NameError:
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

mixing_chamber_re = re.compile(r'mixing.{0,2}chamber', re.DOTALL)
text_df['mixing_chamber'] = text_df['text'].progress_apply(lambda x: mixing_chamber_re.findall(x) if mixing_chamber_re.search(x) else False)
text_df[text_df['mixing_chamber'] != False]

douglas_bag_re = re.compile(r'douglas.{0,2}bag', re.DOTALL)
text_df['douglas_bag'] = text_df['text'].progress_apply(lambda x: douglas_bag_re.findall(x) if douglas_bag_re.search(x) else False)
text_df[text_df['douglas_bag'] != False]