from pathlib import Path
import shutil

# get paths of files that converted to an empty txt file
empty_txt_conv_paths = list(Path('/Users/antonhesse/Desktop/Anton/Education/UMN/Lab and Research/HSPL/CPET_scoping_review/data/cpet_articles/full_texts/empty_txt_conv').glob('*.txt'))
empty_txt_conv_file_stems = [path.stem for path in empty_txt_conv_paths]

# get the full list of pdf and epub paths
pdf_file_paths = list(Path('/Users/antonhesse/Desktop/Anton/Education/UMN/Lab and Research/HSPL/CPET_scoping_review/data/cpet_articles/full_texts/pdfs').glob('*.pdf'))
epub_file_paths = list(Path('/Users/antonhesse/Desktop/Anton/Education/UMN/Lab and Research/HSPL/CPET_scoping_review/data/cpet_articles/full_texts/epubs').glob('*.epub'))

def flatten_list(lst):
    out = []
    for l in lst:
        if isinstance(l, list):
            for item in l:
                out.append(item)
        else:
            out.append(l)
    if any([isinstance(o, list) for o in out]):
        out = flatten_list(out)
    return out

# use flatten list function to squish the pdf and epub file paths into one larger list
pdf_epub_file_paths = flatten_list([pdf_file_paths, epub_file_paths])

# get pdf and epub file paths
empty_file_conv_paths = [path for path in pdf_epub_file_paths if path.stem in empty_txt_conv_file_stems]

file_extensions = {}
for path in empty_file_conv_paths:
    if (path.suffix in file_extensions):
        file_extensions[path.suffix] += 1
    else:
        file_extensions[path.suffix] = 1

file_extensions # all of these are PDFs

dest_folder = Path('/Users/antonhesse/Desktop/Anton/Education/UMN/Lab and Research/HSPL/CPET_scoping_review/data/cpet_articles/full_texts/empty_txt_conv_pdfs')

for path in empty_file_conv_paths:
    # combine dest folder with file name
    dest_path = dest_folder / path.name
    
    # copy file
    try:
        shutil.copy(src=path, dst=dest_path)
    except FileNotFoundError as e:
        print(e)