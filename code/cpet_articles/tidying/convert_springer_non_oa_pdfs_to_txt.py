from distutils.log import error
import subprocess
import glob
from tqdm import tqdm
import shutil
import pandas as pd

springer_non_oa_files = glob.glob('data/cpet_articles/pdfs/springer_non_oa_pdfs/*.pdf')

errors = {}

remaining_files1 = springer_non_oa_files[698:] # got stuck at 697
remaining_files2 = remaining_files1[409:]

for f in tqdm(remaining_files2):
    f_no_suffix = f.split('.pdf')[0]
    cmd = 'pdf2txt.py -o %s.txt %s' % (f_no_suffix, f)
    run = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    try:
        out, err = run.communicate(timeout=60)
        if err:
            errors.update({f: err})
            print(err) # display errors if they occur
    except Exception as e:
        run.kill()
        out, err = run.communicate()
        if err:
            errors.update({f: err})
            print(err) # display errors if they occur


error_df = pd.DataFrame.from_dict(errors, orient='index')
error_df.index.name = 'newhead'
error_df.reset_index(inplace=True)
error_df = error_df.rename({'newhead': 'file_name',0: 'error_msg'}, axis=1)
error_df.to_csv('data/cpet_articles/pdf_to_txt_conv_derrors.csv', index=False)

txt_files = glob.glob('data/cpet_articles/pdfs/springer_non_oa_pdfs/*.txt')
new_folder = 'data/cpet_articles/txts/'

for f in txt_files:
    try:
        shutil.move(f, new_folder)
    except shutil.Error as e:
        print(e)