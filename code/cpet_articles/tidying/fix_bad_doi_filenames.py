from pathlib import Path
import re
import shutil

pdf_file_paths = list(Path('data/cpet_articles/full_texts/pdfs').rglob('*.pdf'))
# pdf_files = [path.stem for path in pdf_file_paths]
# I'm not sure I can fix this with shutil since it can't figure out how to use
# forward slashes / in file names. It think it's a folder separator

split_error_re = re.compile(r"', '")
split_errors = list(filter(split_error_re.search, list(map(str, pdf_file_paths))))
len(split_errors)
split_errors[0]

test_path = 'data/cpet_articles/full_texts/pdfs/unpaywall_oa/0008-6363(95)00199-9.pdf'
parens_re = re.compile(r'(?=/.{0,100}/).*[()]+.*(?<=\.pdf)')
# parens_re.search(test_path).group()

parens = list(filter(parens_re.search, list(map(str,pdf_file_paths))))
len(parens)
for p in parens:
    print(p)

pdf_path = split_errors[0]

for pdf_path in pdf_file_paths:
    if re.search(r"', '", str(pdf_path)):
        source = pdf_path
        dest = re.sub(r"', '", '/', source)
        shutil.move(source, dest)


if re.search(r"', '", str(pdf_path)):
    source = pdf_path
    dest = re.sub(r"', '", '', source)


shutil.move(source, dest)