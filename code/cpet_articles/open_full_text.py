from pathlib import Path
import re
# from subprocess 

full_text_folder_path = Path('/Users/antonhesse/Desktop/Anton/Education/UMN/Lab and Research/HSPL/CPET_scoping_review/data/cpet_articles/full_texts')

file_name = str(input('Enter the name of the file you wish to open: '))
file_stem = Path(file_name).stem

extensions = ['pdfs', 'epubs', 'txts']

for ext in extensions:
    ext_singular = re.sub(r's$', '', ext)
    file_paths = list(Path(full_text_folder_path / ext).rglob(f'*.{ext_singular}'))
    stems = [path.stem for path in file_paths]
    if file_stem in stems:
        try: