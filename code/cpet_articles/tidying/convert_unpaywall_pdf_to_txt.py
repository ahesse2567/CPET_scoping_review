import subprocess
import glob
# from pathlib import Path # not sure if I need this or not
from tqdm import tqdm

unpaywall_files = glob.glob('data/cpet_articles/pdfs/unpaywall_oa/*.pdf')

errors = {}

#  got stuck at file 503
unpaywall_files = unpaywall_files[503:]

for f in tqdm(unpaywall_files):
    txt_filename = f.split('.pdf')[0]
    cmd = 'pdf2txt.py -o %s.txt %s' % (txt_filename, f)
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

# next step: move files from the same folder to another folder
# should this just be part of the loop?