import pandas as pd

no_exer_dois = pd.read_csv('/Users/antonhesse/Desktop/Anton/Education/UMN/Lab and Research/HSPL/CPET_scoping_review/data/cpet_articles/no_exer_dois.csv')
no_exer_unpaywall_info = pd.read_csv('/Users/antonhesse/Desktop/Anton/Education/UMN/Lab and Research/HSPL/CPET_scoping_review/data/cpet_articles/no_exer/unpaywall/unpaywall_info.csv')

merge = pd.merge(no_exer_dois['doi'], no_exer_unpaywall_info, how='outer', indicator=True)

exer_unpaywall_info = merge[merge['_merge'] == 'right_only'].reset_index(drop=True)
exer_unpaywall_info

unpaywall_exer_new = pd.read_csv('/Users/antonhesse/Desktop/Anton/Education/UMN/Lab and Research/HSPL/CPET_scoping_review/data/cpet_articles/unpaywall/unpaywall_info_new_exer.csv')

df_list = [exer_unpaywall_info, unpaywall_exer_new]
exer_unpaywall_info = pd.concat(df_list).drop_duplicates().reset_index(drop=True)

exer_unpaywall_info.to_csv('/Users/antonhesse/Desktop/Anton/Education/UMN/Lab and Research/HSPL/CPET_scoping_review/data/cpet_articles/unpaywall/unpaywall_info.csv',
    index=False)