from cgitb import reset
import pandas as pd

exer_records = pd.read_csv('/Users/antonhesse/Desktop/Anton/Education/UMN/Lab and Research/HSPL/CPET_scoping_review/data/cpet_articles/dois_combined.csv')
no_exer_records = pd.read_csv('/Users/antonhesse/Desktop/Anton/Education/UMN/Lab and Research/HSPL/CPET_scoping_review/data/cpet_articles/no_exer/dois_combined.csv')

merge = pd.merge(exer_records, no_exer_records, how='outer', indicator=True)
merge['_merge'].value_counts()

no_exer_only = merge[merge['_merge'] == 'right_only'].dropna().reset_index(drop=True)
no_exer_only

no_exer_only.to_csv('/Users/antonhesse/Desktop/Anton/Education/UMN/Lab and Research/HSPL/CPET_scoping_review/data/cpet_articles/no_exer_only.csv',
    index=False)