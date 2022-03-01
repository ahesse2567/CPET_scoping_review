#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Mar  1 14:39:06 2022

@author: antonhesse
"""


#%%
import pandas as pd
import requests
from unpywall.utils import UnpywallCredentials
from unpywall import Unpywall
import re
#%%

UnpywallCredentials('hesse151@umn.edu')

               
dois = pd.read_csv('/Users/antonhesse/Desktop/Anton/Education/UMN/Lab and Research/HSPL/CPET_data_analysis/data/raw/ovid_records_combined.csv')

pre_doi_re = re.compile('https://dx.doi.org/')


id_only = [re.sub(pre_doi_re, '', str(doi)) for doi in dois['DO'].tolist()]

df = Unpywall.doi(dois=id_only, progress=True, errors = 'ignore')
