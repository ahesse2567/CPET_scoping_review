import requests
import pandas as pd
import requests
from unpywall.utils import UnpywallCredentials
from unpywall import Unpywall

UnpywallCredentials('hesse151@umn.edu')

articles = pd.read_csv('/Users/antonhesse/Desktop/Anton/Education/UMN/Lab and Research/HSPL/CPET_data_analysis/data/cpet_articles/ovid/unpaywall_info.csv')
springer_non_oa_articles = articles[(articles['is_oa'] == False) & \
    (articles['publisher'] == 'Springer Science and Business Media LLC')]

