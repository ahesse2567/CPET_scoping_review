import requests
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

ovid_output = pd.read_csv('/Users/antonhesse/Desktop/Anton/Education/UMN/Lab and Research/HSPL/CPET_data_analysis/data/processed/ovid_export_tidy.csv')
pmc = ovid_output.PM[ovid_output.PM.notnull()]

base_url  = "https://www.ncbi.nlm.nih.gov/pmc/utils/idconv/v1.0/"
tool = 'cpet_data_analysis'
email = 'hesse151@umn.edu'
idtype = 'pmcid'
format = 'json'

id_conv = []
id_df_list = []

# can only request 200 article conversions at a time, so use divisions to split up into
# chunks that are up to 200 items long
pmc_sections = divisions(len(pmc), ceil(len(pmc) / 200))

for i in range(len(pmc_sections)):
    url_string = pmc.iloc[pmc_sections[i]].str.cat(sep = ',')
    pmc_string = url_string.replace('https://www.ncbi.nlm.nih.gov/pmc/articles/', '')
    link = base_url + '?tool=' + tool + '&email=' + email + '&ids=' + pmc_string + '&idtype=' + idtype \
    + '&format=' + format
    r = requests.get(url = link)
    id_conv.append(r.json())

    json_dat = r.json()
    temp_df = pd.DataFrame.from_dict(json_dat['records'])
    temp_df = temp_df[["pmcid", "pmid", "doi"]]
    id_df_list.append(temp_df)

id_df = pd.concat(id_df_list)
id_df = id_df[id_df['doi'].notnull()] # if the search didn't yeild new DOI's, we don't need it
id_df = id_df.reset_index(drop = True)
id_df.to_csv("/Users/antonhesse/Desktop/Anton/Education/UMN/Lab and Research/HSPL/CPET_data_analysis/data/raw/pmc_conv.csv",\
    index=False)