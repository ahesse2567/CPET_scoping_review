import subprocess
from pathlib import Path # not sure if I need this or not
from tqdm import tqdm
import re
import pandas as pd
import itertools
import pandas as pd

"""
Flow of this file
1.) Find all txt stem names
2.) Find txt files in 'bad' folders
3.) Finall all PDF stem names
4.) Compare PDF stems agains txt stems to find PDFs that have yet to be converted
"""

#  find txt files and stems
existing_txt_file_paths = list(Path('/Users/antonhesse/Desktop/Anton/Education/UMN/Lab and Research/HSPL/CPET_scoping_review/data/cpet_articles/full_texts/txts').rglob('*.txt'))
len(existing_txt_file_paths)
existing_txt_files = [path.stem for path in existing_txt_file_paths]
# find txt error folders
full_text_folders = [folder for folder in list(Path('/Users/antonhesse/Desktop/Anton/Education/UMN/Lab and Research/HSPL/CPET_scoping_review/data/cpet_articles/full_texts').iterdir()) if folder.is_dir()]
txt_error_folders = ['non-english', 'empty_txt_conv', 'pdf_to_txt_parsing_error']
txt_error_folders_paths = [folder for folder in full_text_folders if folder.name in txt_error_folders]
#  find txt error files
txt_error_file_path_list = [path.glob('*.txt') for path in txt_error_folders_paths]
txt_error_file_paths = list(itertools.chain.from_iterable(txt_error_file_path_list))
txt_error_files = [path.stem for path in txt_error_file_paths]
# find PDF files
existing_pdf_file_paths = list(Path('/Users/antonhesse/Desktop/Anton/Education/UMN/Lab and Research/HSPL/CPET_scoping_review/data/cpet_articles/full_texts/pdfs').rglob('*.pdf'))
len(existing_pdf_file_paths)
existing_pdf_files = [path.stem for path in existing_pdf_file_paths]
# determine PDFs that have yet to be converted
txt_error_files = [path.stem for path in txt_error_file_paths]
pdfs_to_convert = [pdf for pdf in existing_pdf_files if pdf not in existing_txt_files and pdf not in txt_error_files]
len(pdfs_to_convert)

pdf = pdfs_to_convert[0]
pdf
existing_pdf_file_path_strings = list(map(str, existing_pdf_file_paths))
pdf_file_paths_to_convert = []
for pdf in tqdm(pdfs_to_convert):
    pdf_re = re.compile('.*' + re.escape(pdf) + '.*')
    file_path = list(filter(pdf_re.match, existing_pdf_file_path_strings))[0]
    pdf_file_paths_to_convert.append(file_path)

# # after running this loop, move all txt files from pdf folders into txt folders
file_path = pdf_file_paths_to_convert[432]
file_path

def pdf_to_txt(file_path):
    pdf_stem = Path(file_path).stem
    log = {'doi': pdf_stem}
    txt_folder_path = re.sub(r'/pdfs/', '/txts/', file_path)
    txt_file_path = re.sub(r'.pdf', '.txt', txt_folder_path)
    cmd = f'pdf2txt.py -o {txt_file_path} {file_path}'
    run = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    try:
        out, err = run.communicate(timeout=90)
        if err:
            log.update({'error': err})
            print(err)
    except Exception as e:
        run.kill()
        out, err = run.communicate()
        if err:
            log.update({'error': err})
            print(err) # display errors if they occur

    return log

errors = [pdf_to_txt(file_path) for file_path in tqdm(pdf_file_paths_to_convert)]

error_df = pd.DataFrame(errors)
error_df = error_df.rename(columns={'doi': 'doi_suffix'})
error_df.to_csv('data/cpet_articles/unpaywall/pdf2txt_conv_errors.csv', index=False)
# errors = {}

# for f in tqdm(pdf_file_paths_to_convert):
#     txt_filename = f.split('.pdf')[0]
#     cmd = 'pdf2txt.py -o %s.txt %s' % (txt_filename, f)
#     run = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
#     try:
#         out, err = run.communicate(timeout=90)
#         if err:
#             errors.update({f: err})
#             print(err) # display errors if they occur
#     except Exception as e:
#         run.kill()
#         out, err = run.communicate()
#         if err:
#             errors.update({f: err})
#             print(err) # display errors if they occur