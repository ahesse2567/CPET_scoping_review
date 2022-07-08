import subprocess
import glob
from pathlib import Path # not sure if I need this or not
from tqdm import tqdm
import re

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
import shutil
txt_files = glob.glob('data/cpet_articles/pdfs/unpaywall_oa/*.txt')
new_folder = 'data/cpet_articles/full_texts/txts/'

for f in txt_files:
    shutil.move(f, new_folder)

# move empty files. Some files didn't convert properly
txt_files = glob.glob('data/cpet_articles/full_texts/txts/*.txt')

# move empty txt files into a folder just for them
for f in txt_files:
    if Path(f).stat().st_size == 0:
        dest = re.sub(r'full_texts/txts/', 'full_texts/txts/empty_txt_conv/', f)
        shutil.move(f, dest)