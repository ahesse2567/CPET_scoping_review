from pathlib import Path
import re
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer, WordNetLemmatizer

def tokenize_file(file_path, mode = 'lemm'):
    # check file size to make sure the txt file actually has text
    file_size = 0
    while file_size == 0:
        file_size = Path(file_path).stat().st_size
        if file_size != 0: # check if conversion to txt didn't work
            with open(str(file_path), 'r') as f:
                text = f.read()
        else:
            print('Empty file, returning None')
            return None
    text_lower = text.lower()
    tokens = word_tokenize(text_lower)
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

def read_raw_text(file_path):
    # check file size to make sure the txt file actually has text
    file_size = 0
    while file_size == 0:
        file_size = Path(file_path).stat().st_size
        if file_size != 0: # check if conversion to txt didn't work
            with open(str(file_path), 'r') as f:
                text = f.read()
        else:
            print('Empty file, returning None')
            return None
    text_lower = text.lower()
    
    return text_lower