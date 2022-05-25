#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Mar  1 14:39:06 2022

@author: antonhesse
"""
#%%
import pandas as pd
from unpywall.utils import UnpywallCredentials
from unpywall import Unpywall
import numpy as np
#%%

UnpywallCredentials('hesse151@umn.edu')
               
dois = pd.read_csv('/Users/antonhesse/Desktop/Anton/Education/UMN/Lab and Research/HSPL/CPET_scoping_review/data/cpet_articles/dois_combined.csv')
doi_list = dois['doi'].astype(str).to_list()

# doi_list = [re.sub(pre_doi_re, '', str(doi)) for doi in dois['DO'].tolist()]
#%%

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

doi_divisions = divisions(len(doi_list), 100)
# %%
df_list = []
for i, division in enumerate(doi_divisions):
    temp_df = Unpywall.doi(dois=doi_list[division[0]:division[-1]], progress=True, errors = 'ignore')
    df_list.append(temp_df)
    pct_complete = round((i+1) / len(doi_divisions) * 100,1)
    print(f'{pct_complete}%')
# %%

df = pd.concat(df_list)

df.to_csv('/Users/antonhesse/Desktop/Anton/Education/UMN/Lab and Research/HSPL/CPET_scoping_review/data/cpet_articles/unpaywall/unpaywall_info.csv',\
    index=False)