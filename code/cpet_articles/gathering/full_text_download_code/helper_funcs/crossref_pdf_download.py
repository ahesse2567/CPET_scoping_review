import requests
from code.cpet_articles.utils.article_names import get_doi_suffix
from code.cpet_articles.gathering.full_text_download_code.helper_funcs.articles import download_pdf

def crossref_pdf_download(
    doi,
    accept,
    dest,
    user_agent=None,
    application='pdf',
    TDM_header=None,
    TDM_token=None,
    verify=True):

    doi_url = 'https://doi.org/' + str(doi)
    out = {'doi': doi}
    crossref_headers = {'Accept': accept, 'User-Agent': user_agent}

    try:
        crossref_response = requests.get(
                url = doi_url,
                headers=crossref_headers,
                allow_redirects=True,
                verify=verify)
        
        out.update({'CR_status_code': crossref_response.status_code})

        if crossref_response.status_code != 200:
            print(f'Status code {crossref_response.status_code} for DOI {doi}')
            return out
        
        pdf_url = crossref_response.json()['link'][0]['URL']

        publisher_headers = {
            'User-Agent': user_agent,
            'Content-Type': str('application/' + application)
        }
        if (TDM_header != None) & (TDM_token != None):
            publisher_headers.update({TDM_header: TDM_token})

        publisher_response = requests.get(pdf_url, headers = publisher_headers, allow_redirects=True, verify=verify)
        out.update({'publisher_status_code': publisher_response.status_code})

        if publisher_response.status_code != 200:
            # print(f'Status code {publisher_response.status_code} for DOI {doi}')
            return out
        
        doi_suffix = get_doi_suffix(doi)

        download_pdf(doi=doi, dest_folder=dest, content=publisher_response.content)

        # filename = f'{dest}/{doi_suffix}.{application}'

        # with open(filename, mode='wb') as f:
        #     f.write(publisher_response.content)

    except Exception as e:
        print(f'Exception at DOI {doi}')
        print(e)
        out.update({'error': e})
    
    return out

