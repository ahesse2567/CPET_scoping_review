from pathlib import Path
import shutil
import re
import itertools

pdf_folders = list(Path('data/cpet_articles/full_texts/pdfs').glob('*'))
unpaywall_re = re.compile(r'/.*unpaywall.*')
unpaywall_pdf_folders = list(filter(unpaywall_re.search, list(map(str, pdf_folders))))
unpaywall_pdf_list = [list(Path(folder).glob('*.pdf')) for folder in unpaywall_pdf_folders]
unpaywall_pdf_paths = list(itertools.chain.from_iterable(unpaywall_pdf_list))
unpaywall_pdfs = [path.stem for path in unpaywall_pdf_paths]

existing_txt_paths = list(Path('data/cpet_articles/full_texts/txts').glob('*.txt'))
existings_txts = [path.stem for path in existing_txt_paths]

# move unpaywall txt files
for pdf_path in unpaywall_pdf_paths:
    pdf = pdf_path.stem
    if pdf in existings_txts:
        txt_file_re = re.compile('.*' + pdf + '.txt')
        source = list(filter(txt_file_re.match, list(map(str, existing_txt_paths))))[0]
        dest = re.sub(r'/txts/', '/txts/unpaywall_oa/', source)
        shutil.move(src=source, dst=dest)

# move springer txt files
springer_pdf_paths = list(Path('data/cpet_articles/full_texts/pdfs/springer_non_oa').glob('*.pdf'))
springer_pdfs = [path.stem for path in springer_pdf_paths]

for pdf_path in springer_pdf_paths:
    pdf = pdf_path.stem
    if pdf in existings_txts:
        txt_file_re = re.compile('.*' + pdf + '.txt')
        source = list(filter(txt_file_re.match, list(map(str, existing_txt_paths))))[0]
        dest = re.sub(r'/txts/', '/txts/springer_non_oa/', source)
        try:
            shutil.move(src=source, dst=dest)
        except FileNotFoundError as e:
            print(e)