from pathlib import Path
import re
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer, WordNetLemmatizer

# make text easy to work with
def normalize_text(text):
    text_lower = text.lower()
    # remove excessive space characters
    text_lower = re.sub(r' {2,}', ' ', text_lower)
    # remove excessive newlines with potential space and tab characters
    text_lower = re.sub(r'(?:[ \t]*\n[ \t]*){2,}', '\n', text_lower)
    # change excessive newlines to single newline
    text_lower = re.sub(r'\n{2,}', '\n', text_lower)
    # remove end of line hyphenations. This works b/c lookarounds don't(?) 'consume' their characters
    text_lower = re.sub(r'(?<=[a-zA-Z])-\n(?=[a-zA-Z])', '', text_lower)
    # remove newline characters mid paragraph. These are obviously needed to format the pdf
    # document, but we don't need them when anlyzing text.
    text_lower = re.sub(r'(?<!\n)\n(?=\S)', ' ', text_lower)
    # fix weird single-letter character spacing like P . M O G N O N I ()
    text_lower = re.sub(r'(?<= \w) (?=\w )', '', text_lower)
    # remove whitespace BEFORE punctuation marks
    text_lower = re.sub(r'\s(?=[.,?!;:])', '', text_lower)
    # fix errors related to parsi,ng V̇O2 (i.e. V with a dot above it?) # unsure if needed
    # text_lower = re.sub(r'v\W{0,3}o2\b', 'vo2', re.IGNORECASE)
    return text_lower

# read the file if the file isn't empty
def read_raw_text(file_path):
    # check file size to make sure the txt file actually has text
    if Path(file_path).stat().st_size > 0:
        with open(str(file_path), 'r') as f:
            text = f.read()
        text = normalize_text(text)
        return text
    else:
        return None

def tokenize_text(text, mode = 'lemm'):
    if text:
        tokens = word_tokenize(text)
        stop_words = set(stopwords.words('english'))

        filtered_tokens = [t for t in tokens if t not in stop_words]
        
        if mode == 'lemm':
            lemmatizer = WordNetLemmatizer()
            lemmatized_words = [lemmatizer.lemmatize(t) for t in filtered_tokens]

            return lemmatized_words
        
        elif mode == 'stem':
            stemmer = PorterStemmer()
            stemmed_words = [stemmer.stem(t) for t in filtered_tokens]
        
            return stemmed_words
    else:
        return None

def tokenize_file(file_path, mode = 'lemm'):
    text = read_raw_text(file_path)
    text = tokenize_text(text, mode = mode)
    return text

def get_surrounding_text(phrase, text, chars=200):
    # get surrounding text if it is near words like vo2, breath, or metabolic
    phrase = re.escape(phrase) # prevent escape character issues

    surrounding_text_re = re.compile(fr'''(.{{0,{chars}}}{phrase}.{{0,{chars}}}
        )''', re.DOTALL | re.VERBOSE)

    vo2_breath_re = re.compile(
        r'(?:v.{0,2})?o2|breath|metaboli|respirat|gas|air|ventilat|pulmonary|(oxygen|o2).{0,2}(consumption|uptake)', re.DOTALL)
    
    if surrounding_text_re.search(text):
        res = surrounding_text_re.findall(text)
        res = [r for r in res if vo2_breath_re.search(r)]
        if res:
            return res
        else:
            return None
    else:
        return None

def capitalize_substring(main_string, sub_string):
    out = main_string.replace(sub_string, sub_string.upper())
    return out
