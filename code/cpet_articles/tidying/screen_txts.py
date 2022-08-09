from pathlib import Path
import pandas as pd
from tqdm import tqdm
import shutil
import numpy as np
import sys
from langdetect import detect
sys.path.append('/Users/antonhesse/Desktop/Anton/Education/UMN/Lab and Research/HSPL/CPET_scoping_review/code/cpet_articles/analysis/helper_funcs')
from text_analysis import tokenize_file, process_file_one_string


txt_file_paths = list(Path('/Users/antonhesse/Desktop/Anton/Education/UMN/Lab and Research/HSPL/CPET_scoping_review/data/cpet_articles/full_texts/txts').glob('*.txt'))

word_lists = []
for f in tqdm(txt_file_paths):
    try:
        wl = process_file(f.stem, list(map(str, txt_file_paths)))
        word_lists.append(wl)
    except IndexError as e:
        print(e)
        word_lists.append((f.stem, e))


txt_files = [path.stem for path in txt_file_paths]
words_df = pd.DataFrame({
    'doi_suffix': txt_files,
    'path': txt_file_paths,
    'words': word_lists})

# move empty txt files. The PDFs were probably images, so pdf2txt.py didn't work properly
for idx, row in tqdm(words_df.iterrows()):
    try:
        if row['words'] == None:
            new_dest = row['path'].parent.parent / 'empty_txt_conv' / row['path'].name
            shutil.move(row['path'], new_dest)
        elif len(row['words']) == 0:
            new_dest = row['path'].parent.parent / 'empty_txt_conv' / row['path'].name
            shutil.move(row['path'], new_dest)
    except (FileNotFoundError, TypeError) as e:
        print(e)

words_df[words_df['words'].isnull()]


# parsing errors may have also stemmed from the PDFs as images problem
tqdm.pandas()

words_df['num_words'] = words_df['words'].progress_apply(lambda x: len(x) if x != None else 0)
words_df['avg_word_len'] = words_df.progress_apply(
    lambda x: np.mean(list(map(len, x['words']))) if isinstance(x['words'], list) else 0, axis=1)

for idx, row in tqdm(words_df.iterrows()):
    if row['avg_word_len'] < 1.5 or np.isnan(row['avg_word_len']):
        try:
            new_dest = row['path'].parent.parent / 'pdf_to_txt_parsing_error' / row['path'].name
            shutil.move(row['path'], new_dest)
        except FileNotFoundError as e: # in case I already moved the file previously
            print(e)

words_df['language'] = words_df.progress_apply(lambda x: detect(x['']))


# TODO analyze language and move non-english files