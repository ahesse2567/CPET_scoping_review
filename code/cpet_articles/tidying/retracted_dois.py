import requests
import pandas as pd
from tqdm import tqdm
import random
import crossref_commons.retrieval
from crossref_commons.iteration import iterate_publications_as_json

r = requests.get(url = 'http://api.crossref.org/works', params = {'filter': 'update-type:retraction'})
total_retractions = r.json()['message']['total-results']

retracted_articles = list(iterate_publications_as_json(filter={'update-type': 'retraction'}, max_results=total_retractions))
retracted_dois = [article['DOI'] for article in retracted_articles]

all_articles = pd.read_csv('/Users/antonhesse/Desktop/Anton/Education/UMN/Lab and Research/HSPL/CPET_scoping_review/data/cpet_articles/unpaywall/unpaywall_info.csv')

# convert all DOIs to lower case to plan against that potential issue
retracted_dois_lower = list(map(lambda x: x.lower(), retracted_dois))
article_dois_lower = list(map(lambda x: x.lower(), all_articles['doi'].to_list()))

bad_dois = [doi for doi in tqdm(retracted_dois_lower) if doi in article_dois_lower]
bad_dois # huh. No results


all_articles.loc[10000:11000, 'doi'].to_clipboard(index=False)
# repeat 10000 to 11000?