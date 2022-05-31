import subprocess
import glob
# from pathlib import Path # not sure if I need this or not
from tqdm import tqdm

unpaywall_files = glob.glob('data/cpet_articles/pdfs/unpaywall_oa/*.pdf')

errors = {}

for f in tqdm(unpaywall_files):
    txt_filename = f.split('.pdf')[0]
    cmd = 'pdf2txt.py -o %s.txt %s' % (txt_filename, f)
    run = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = run.communicate()
    # display errors if they occur 
    if err:
        errors.update({f: err})
        print(err)