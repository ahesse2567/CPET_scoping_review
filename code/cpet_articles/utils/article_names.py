import re

def get_doi_suffix(doi):
    doi_suffix = re.sub(r'10.\d+/', '', doi)
    doi_suffix = re.sub(r"""([()\\*,"': /?;<>])""", '_._', doi_suffix) # remove bad chars
    doi_suffix = re.sub(r'(_._){2,}', '_._', doi_suffix) # remove multiple sequences of _._
    return doi_suffix
