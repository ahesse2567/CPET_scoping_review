#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Mar  1 14:39:06 2022

@author: antonhesse
"""
#%%
from matplotlib.pyplot import axis
import pandas as pd
from unpywall.utils import UnpywallCredentials
from unpywall import Unpywall
import re
import numpy as np
#%%

UnpywallCredentials('hesse151@umn.edu')
               
dois = pd.read_csv('/Users/antonhesse/Desktop/Anton/Education/UMN/Lab and Research/HSPL/CPET_data_analysis/data/cpet_articles/doi_merged.csv')
id_only = dois['doi_clean'].astype(str).to_list()

# id_only = [re.sub(pre_doi_re, '', str(doi)) for doi in dois['DO'].tolist()]
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

doi_divisions = divisions(len(id_only), 100)
#%%
df = pd.DataFrame()
for i in range(len(doi_divisions)):
    df = df.append(Unpywall.doi(dois=id_only[doi_divisions[i][0]:doi_divisions[i][-1]], \
        progress=True, errors = 'ignore'))
    print(i)
df.to_csv('/Users/antonhesse/Desktop/Anton/Education/UMN/Lab and Research/HSPL/CPET_data_analysis/data/cpet_articles/unpaywall_info.csv',\
    index=False)