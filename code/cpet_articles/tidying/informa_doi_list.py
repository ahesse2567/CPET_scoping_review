import pandas as pd
import os

os.getcwd()
articles = pd.read_csv('data/cpet_articles/unpaywall/unpaywall_info.csv')
pd.set_option("display.max_rows", 10)
articles['publisher'].value_counts()
informa_articles = articles[articles['publisher'] == "Informa UK Limited"]
informa_dois = informa_articles.filter(['doi'], axis=1).reset_index(drop=True)
informa_dois
informa_dois.to_csv('data/cpet_articles/informa_dois.csv',index=False)