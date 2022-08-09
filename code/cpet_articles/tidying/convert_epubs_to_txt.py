from pathlib import Path
from epub2txt import epub2txt
import pandas as pd
from tqdm import tqdm

proj_folder_path = Path('/Users/antonhesse/Desktop/Anton/Education/UMN/Lab and Research/HSPL/CPET_scoping_review')
epub_folder = proj_folder_path / 'data' / 'cpet_articles' / 'full_texts' / 'epubs'
epub_paths = list(epub_folder.glob('*.epub'))

txt_folder = proj_folder_path / 'data' / 'cpet_articles' / 'full_texts' # / 'txts'
log =[]
for path in tqdm(epub_paths):
    out = {'doi_suffix': path.stem}
    try:
        res = epub2txt(path)
        fname = str(txt_folder / (path.stem + '.txt'))
        with open(fname, 'w') as f:
            f.write(res)
    except Exception as e:
        out.update({'error': e})
    log.append(out)

log_df = pd.DataFrame(log)
log_df[~log_df['error'].isna()]
