from urllib import response
import requests
import pandas as pd
from math import ceil
import numpy as np
import re

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

wos_records = pd.read_csv('/Users/antonhesse/Desktop/Anton/Education/UMN/Lab and Research/HSPL/CPET_scoping_review/data/cpet_articles/web_of_science/web_of_science_records_tidy.csv')
pmid = wos_records[wos_records['pubmed_id'].notnull().dropna()]['pubmed_id'].astype(str)
trailing_zero = re.compile(r'\.0')
pmid = pmid.apply(lambda x: trailing_zero.sub('',x))

base_url  = "https://www.ncbi.nlm.nih.gov/pmc/utils/idconv/v1.0/"
tool = 'cpet_scoping_review'
email = 'hesse151@umn.edu'
idtype = 'pmid'
format = 'json'

id_conv = []
id_df_list = []

# can only request 200 article conversions at a time, so use divisions to split up into
# chunks that are up to 200 items long
pmid_sections = divisions(len(pmid), ceil(len(pmid) / 200))

for i, nums in enumerate(pmid_sections):
    pmid_string = pmid.iloc[nums].str.cat(sep = ',')
    link = base_url + '?tool=' + tool + '&email=' + email + '&ids=' + pmid_string + \
        '&idtype=' + idtype + '&format=' + format
    response = requests.get(url = link)
    id_conv.append(response.json())

    json_dat = response.json()
    temp_df = pd.DataFrame.from_dict(json_dat['records'])
    temp_df = temp_df[["pmcid", "pmid", "doi"]]
    id_df_list.append(temp_df)
    print(f'{round(i/len(pmid_sections)*100,0)}%')

id_df = pd.concat(id_df_list)
id_df = id_df[id_df['doi'].notnull()] # if the search didn't yeild new DOI's, we don't need it
id_df = id_df.reset_index(drop = True)
id_df.to_csv('/Users/antonhesse/Desktop/Anton/Education/UMN/Lab and Research/HSPL/CPET_scoping_review/data/cpet_articles/web_of_science/wos_pmc_conv.csv',\
    index=False)