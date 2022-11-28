from pathlib import Path
from tqdm import tqdm
from code.cpet_articles.analysis.helper_funcs.text_analysis import read_raw_text
import pandas as pd
tqdm.pandas()

txt_file_paths = list(Path('/Users/antonhesse/Desktop/Anton/Education/UMN/Lab and Research/HSPL/CPET_scoping_review/data/cpet_articles/full_texts/txts').rglob('*.txt'))
dest_folder = Path('/Users/antonhesse/Desktop/Anton/Education/UMN/Lab and Research/HSPL/CPET_scoping_review/data/cpet_articles/full_texts/clean_txts')

for path in tqdm(txt_file_paths):
    try:
        rt = read_raw_text(path)
        new_path = Path(dest_folder / path.stem).resolve().with_suffix('.txt')
        with open(new_path, 'w') as f:
            f.write(rt)
    except FileExistsError as e:
        print(e)
