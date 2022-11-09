import requests

def elsevier_full_text_download(
    doi,
    api_key,
    dest_folder,
    insttoken=None,
    user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:101.0) Gecko/20100101 Firefox/101.0',
    file_ext='txt',
    httpAccept='text/plain',
    view='FULL',
    allow_redirects=True,
    verify=True):

    elsevier_params = {
        'apiKey': api_key,
        'httpAccept': httpAccept,
        'view': view
    }
    elsevier_headers ={'User-Agent': user_agent}

    doi_url = 'https://api.elsevier.com/content/article/doi/' + doi
    temp_dict = {'doi': doi}

    try:
        r = requests.get(url=doi_url, params=elsevier_params, headers=elsevier_headers,
        allow_redirects=allow_redirects, verify=verify)
        temp_dict.update({'publisher_status_code': r.status_code})

        if r.status_code == 200:
            doi_suffix = str(doi.split('/')[1:]).strip("[']")
            filename = f'{dest_folder}/{doi_suffix}.{file_ext}'
            
            with open(filename, mode='wb') as f:
                f.write(r.content)

    except Exception as e:
        print(f'Exception at DOI {doi}')
        temp_dict.update({'error': e})

    return temp_dict