from pathlib import Path
import re
import shutil

# we're changing bad characters to _._
# e.g. 0008-6363(95)00199-9 becomes 0008-6363_._95_._00199-9

pdf_file_paths = list(Path('/Users/antonhesse/Desktop/Anton/Education/UMN/Lab and Research/HSPL/CPET_scoping_review/data/cpet_articles/full_texts/pdfs').rglob('*.pdf'))
pdf_files = [path.stem for path in pdf_file_paths]
# I'm not sure I can fix this with shutil since it can't figure out how to use
# forward slashes / in file names. It think it's a folder separator

test_path = 'data/cpet_articles/full_texts/pdfs/unpaywall_oa/0008-6363(95)00199-9.pdf'
bad_chars_re = re.compile(r"""((?=/full_texts/pdfs/.{0,100}/).*[()\\*,"': ?;<>]+.*(?<=\.pdf))""")
bad_chars_re.search(test_path).group()
bad_names = list(filter(bad_chars_re.search, list(map(str, pdf_file_paths))))
len(bad_names)
# good_names = [re.sub(r"""([()\\*,"': ?;<>])""", '_._', name) for name in bad_names]
# good_names

for name in bad_names:
    try:
        path = Path(name)
        new_stem = re.sub(r"""([()\\*,"': ?;<>])""", '_._', path.stem)
        new_name = path.parent / str(new_stem + '.pdf')
        shutil.move(src=name, dst=new_name)
    except Exception as e:
        print(e)


# there were some problems where there was _._ many times in a row
# e.g. _.__.__.__._
# the code below removes all but one _._
pdf_file_paths = list(Path('/Users/antonhesse/Desktop/Anton/Education/UMN/Lab and Research/HSPL/CPET_scoping_review/data/cpet_articles/full_texts/pdfs').glob('*.pdf'))
txt_file_paths = list(Path('/Users/antonhesse/Desktop/Anton/Education/UMN/Lab and Research/HSPL/CPET_scoping_review/data/cpet_articles/full_texts/txts').glob('*.txt'))
epub_file_paths = list(Path('/Users/antonhesse/Desktop/Anton/Education/UMN/Lab and Research/HSPL/CPET_scoping_review/data/cpet_articles/full_texts/epubs').glob('*.epub'))
all_paths = pdf_file_paths + txt_file_paths + epub_file_paths

re_undotun = re.compile(r'(_._){2,}')
bad_path_names = list(filter(re_undotun.search, list(map(str,pdf_file_paths))))

for path in bad_path_names:
    fixed_name = re_undotun.sub('_._', str(path))
    shutil.move(path, fixed_name)