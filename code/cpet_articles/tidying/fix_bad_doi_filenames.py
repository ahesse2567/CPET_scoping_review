from pathlib import Path
import re
import shutil
from tqdm import tqdm

# we're changing bad characters to _._
# e.g. 0008-6363(95)00199-9 becomes 0008-6363_._95_._00199-9

pdf_file_paths = list(Path('/Users/antonhesse/Desktop/Anton/Education/UMN/Lab and Research/HSPL/CPET_scoping_review/data/cpet_articles/full_texts/pdfs').glob('*.pdf'))
txt_file_paths = list(Path('/Users/antonhesse/Desktop/Anton/Education/UMN/Lab and Research/HSPL/CPET_scoping_review/data/cpet_articles/full_texts/txts').glob('*.txt'))
epub_file_paths = list(Path('/Users/antonhesse/Desktop/Anton/Education/UMN/Lab and Research/HSPL/CPET_scoping_review/data/cpet_articles/full_texts/epubs').glob('*.epub'))
all_paths = pdf_file_paths + txt_file_paths + epub_file_paths

bad_chars_re = re.compile(r"""([()\\*,"': /?;<>]+)""")
for path in tqdm(all_paths):
    if bad_chars_re.search(str(path)):
        stem = path.stem
        stem = bad_chars_re.sub('_._', stem) # fix bad chars
        stem = re.sub(r'(_._){2,}', '_._', stem) + path.suffix # replace _.__._ with _._
        new_path = path.parent / stem
        try:
            shutil.move(path, new_path)
        except FileNotFoundError as e:
            print(e)
