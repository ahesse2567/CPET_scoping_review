# This script removes non-English articles and those with txt conversion errors
import fasttext
from pathlib import Path
import pandas as pd
from tqdm import tqdm
import shutil
import numpy as np
from code.cpet_articles.analysis.helper_funcs.text_analysis import tokenize_text, read_raw_text

txt_file_paths = list(Path('/Users/antonhesse/Desktop/Anton/Education/UMN/Lab and Research/HSPL/CPET_scoping_review/data/cpet_articles/full_texts/txts').rglob('*.txt'))

raw_text = []
token_lists = []
for f in tqdm(txt_file_paths):
    try:
        rt = read_raw_text(f)
        raw_text.append(rt)
        tl = tokenize_text(rt)
        token_lists.append(tl)
    except IndexError as e:
        print(e)
        token_lists.append((f, e))


txt_files = [path.stem for path in txt_file_paths]
words_df = pd.DataFrame({
    'doi_suffix': txt_files,
    'path': txt_file_paths,
    'text': raw_text,
    'tokens': token_lists})

# move empty txt files. The PDFs were probably images, so pdf2txt.py didn't work properly
for idx, row in tqdm(words_df.iterrows(), total=words_df.shape[0]):
    try:
        if row['tokens'] == None:
            new_dest = row['path'].parent.parent / 'empty_txt_conv' / row['path'].name
            shutil.move(row['path'], new_dest)
        elif len(row['tokens']) == 0:
            new_dest = row['path'].parent.parent / 'empty_txt_conv' / row['path'].name
            shutil.move(row['path'], new_dest)
    except (FileNotFoundError, TypeError) as e:
        print(e)


# move parsing error files. Parsing errors may have also stemmed from the PDFs as images problem
tqdm.pandas()

words_df['num_words'] = words_df['tokens'].progress_apply(lambda x: len(x) if x != None else 0)
words_df['avg_word_len'] = words_df.progress_apply(
    lambda x: np.mean(list(map(len, x['tokens']))) if isinstance(x['tokens'], list) else 0, axis=1)

for idx, row in tqdm(words_df.iterrows(), total=words_df.shape[0]):
    if row['avg_word_len'] < 1.5 or np.isnan(row['avg_word_len']):
        new_dest = row['path'].parent.parent / 'pdf_to_txt_parsing_error' / row['path'].name
        try:
            shutil.move(row['path'], new_dest)
        except FileNotFoundError as e: # in case I already moved the file previously
            print(e)


# Analyze language and move non-english files
# from lingua import Language, LanguageDetectorBuilder # this seems veeerrrryyy slow, but a little more accurate
# languages = [
#     Language.ENGLISH, Language.FRENCH, Language.GERMAN, Language.SPANISH, Language.CHINESE, Language.KOREAN, Language.JAPANESE,
#     Language.PORTUGUESE, Language.RUSSIAN, Language.ITALIAN, Language.DUTCH]

# detector = LanguageDetectorBuilder.from_languages(*languages).with_preloaded_language_models().build()
# detector.detect_language_of(' '.join(words_df.loc[4561,'tokens']))
# words_df['language'] = words_df.progress_apply(lambda x: detector.detect_language_of(x['text']) if x['text'] != None else np.nan, axis=1)

PRETRAINED_MODEL_PATH = '/Users/antonhesse/opt/anaconda3/bin/lid.176.bin'
model = fasttext.load_model(PRETRAINED_MODEL_PATH)
model.predict(' '.join(words_df.loc[0,'tokens']))

words_df['language'] = words_df.progress_apply(lambda x: model.predict(' '.join(x['tokens'])) if x['text'] != None else np.nan, axis=1)
words_df['lang_code'] = words_df.progress_apply(lambda x: x['language'][0][0], axis=1)
words_df['lang_code'].value_counts()

words_df['language'].value_counts()

words_df[(words_df['lang_code'] != '__label__en') & (words_df['lang_code'] != '__label__de')]
# words_df[words_df['lang_code'] == '__label__fr']
# most languages specified as 'de' are actually english
non_eng_df = words_df[(words_df['lang_code'] != '__label__en') & (words_df['lang_code'] != '__label__de')].reset_index(drop=True)

row = non_eng_df.loc[0,:]
for idx, row in non_eng_df.iterrows():
    new_dest = row['path'].parent.parent / 'non-english' / row['path'].name
    try:
        shutil.move(row['path'], new_dest)
    except FileNotFoundError as e: # in case I already moved the file previously
        print(e)