from pathlib import Path
from tqdm import tqdm
# from code.cpet_articles.analysis.helper_funcs.text_analysis import normalize_text
import re
import shutil

parsing_error_txt_file_paths = list(Path('/Users/antonhesse/Desktop/Anton/Education/UMN/Lab and Research/HSPL/CPET_scoping_review/data/cpet_articles/full_texts/pdf_to_txt_parsing_error').rglob('*.txt'))

dest_folder = Path('/Users/antonhesse/Desktop/Anton/Education/UMN/Lab and Research/HSPL/CPET_scoping_review/data/cpet_articles/full_texts/fixed_pdf_to_txt_parsing_error')

raw_text = []
for path in tqdm(parsing_error_txt_file_paths):
    with open(path, 'r') as f:
        text = f.read()
    text = text.lower()
    text = re.sub(r'(?<=\S)\n(?=\S)', '', text) # rm excessive newlines between non-space chars
    text = re.sub(r'(?<= \w) (?=\w )', '', text) # remove excessive spaces
    text = re.sub(r'(?<=[^.?!])\s{2,}', ' ', text) # remove excessive whitespace (mostly newlines) between words
    # text = normalize_text(text)
    file_name = dest_folder / path.name
    with open(file_name, 'w') as f:
        f.write(text)

fixed_parsing_error_txt_file_paths = list(Path('/Users/antonhesse/Desktop/Anton/Education/UMN/Lab and Research/HSPL/CPET_scoping_review/data/cpet_articles/full_texts/fixed_pdf_to_txt_parsing_error').rglob('*.txt'))
txt_folder = Path('/Users/antonhesse/Desktop/Anton/Education/UMN/Lab and Research/HSPL/CPET_scoping_review/data/cpet_articles/full_texts/txts')

for path in tqdm(fixed_parsing_error_txt_file_paths):
    try:
        new_path = Path(path.parent.parent / 'txts').resolve() / path.name
        shutil.copy(path, new_path)
    except FileNotFoundError as e:
        print(e)
    