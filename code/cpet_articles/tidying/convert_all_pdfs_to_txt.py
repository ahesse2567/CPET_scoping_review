# Convert all PDFs to TXTs, overwriting what has already been converted
import subprocess
from pathlib import Path
import os
from tqdm import tqdm
import re
import pandas as pd

# file_path = Path('/Users/antonhesse/Desktop/Anton/Education/UMN/Lab and Research/HSPL/CPET_scoping_review/code/cpet_articles/tidying/convert_all_pdfs_to_txt.py')
project_dir = Path(__file__).parent.parent.parent.parent
pdf_folder = project_dir / 'data' / 'cpet_articles' / 'full_texts' / 'pdfs'
pdf_file_paths = list(pdf_folder.glob('*.pdf'))

def pdf_to_txt(file_path):
    pdf_stem = Path(file_path).stem
    log = {'doi_suffix': pdf_stem}
    txt_folder_path = re.sub(fr'{os.sep}pdfs{os.sep}', f'{os.sep}txts{os.sep}', str(file_path))
    txt_file_path = re.sub(r'.pdf', '.txt', txt_folder_path)
    cmd = f"'/Users/antonhesse/opt/anaconda3/bin/pdf2txt.py' -o '{txt_file_path}' '{file_path}'"
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

log_list = [pdf_to_txt(file_path) for file_path in tqdm(pdf_file_paths)]

log_df = pd.DataFrame(log_list)
log_df.to_csv('/Users/antonhesse/Desktop/Anton/Education/UMN/Lab and Research/HSPL/CPET_scoping_review/data/cpet_articles/unpaywall/pdf2txt_conv_errors.csv', index=False)
