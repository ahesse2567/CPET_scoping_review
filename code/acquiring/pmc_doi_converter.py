import requests
import json
import pandas as pd
from math import ceil
import numpy as np

# PMC ID converter API documentation: https://www.ncbi.nlm.nih.gov/pmc/tools/id-converter-api/

def divisions(dividend, divisor):
    remainder = dividend % divisor
    arr1 = np.repeat(dividend // divisor + 1, repeats = remainder)
    arr2 = np.repeat(dividend // divisor, repeats = divisor - remainder)
    parts = np.concatenate([arr1, arr2])
    sections = []
    for i in range(len(parts)):
        if i == 0:
            sections.append(list(range(parts[i])))
        else:
            sections.append(list(range(sections[i-1][-1] + 1, (sections[i-1][-1] + 1) + parts[i])))
    return sections

base_url  = "https://www.ncbi.nlm.nih.gov/pmc/utils/idconv/v1.0/"
tool = 'cpet_data_analysis'
email = 'hesse151@umn.edu'
pmc_ids = 'PMC8505378,PMC8505311'
idtype = 'pmcid'
format = 'json'

link = base_url + '?tool=' + tool + '&email=' + email + '&ids=' + pmc_ids + '&idtype=' + idtype \
    + '&format=' + format

r = requests.get(url = link)
r.url
r.json()

ovid_output = pd.read_csv('/Users/antonhesse/Desktop/Anton/Education/UMN/Lab and Research/HSPL/CPET_data_analysis/data/raw/ovid_records_combined.csv')
ovid_output
pmc = ovid_output.PM[ovid_output.PM.notnull()]
pmc

pmc.str.cat(sep = ',')

pmc_sections = divisions(len(pmc), ceil(len(pmc) / 200))
url_string = pmc.iloc[pmc_sections[0]].str.cat(sep = ',')
pmc_string = url_string.replace('https://www.ncbi.nlm.nih.gov/pmc/articles/', '')

link = base_url + '?tool=' + tool + '&email=' + email + '&ids=' + pmc_string + '&idtype=' + idtype \
    + '&format=' + format

r = requests.get(url = link)
r.url
r.json()

# let's try this with a dictionary
# payload = {
#     'tool': 'cpet_data_analysis',
#     'email': 'hesse151%40umn.edu',
#     'pmc_id': 'PMC8505378',
#     'idtype': 'pmcid',
#     'format': 'json'
# }`

# r2 = requests.get(url = base_url, params = payload)
# r2.json() for some reason this doesn't work...