import requests


def request_models(mark):
    """Request remote server 'kolesa.kz' and
        return models dictionary for given mark.
    
        Otherwise return None.
    """

    if mark is None or not isinstance(mark, int):
        raise ValueError('Input argument is missing or not int type.')
    
    # Prepare url and request parameters
    url = "https://kolesa.kz/a/ajax-get-value-parameter"
    
    headers = {
        'user-agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:57.0) Gecko/20100101 Firefox/57.0",
        'content-type': "application/json",
        'x-requested-with': "XMLHttpRequest"
        }
    
    # Every MARK requires single request by using mark's index
    querystring = {
        "value": mark,  # this is index of a car's mark
        "category": "2",  # this and below are default params
        "dependent": "auto.car.mm[1]",
        "name": "auto.car.mm",
        "order-form":"4"
        }
    
    try:
        # Request MODELS list. It contains [0..n] MODELS
        response = requests.get(url, headers=headers, params=querystring, timeout=5)
        if response.status_code != 200:
            return None
    except requests.exceptions.ReadTimeout as e:
        raise requests.exceptions.ReadTimeout("\nRemote server does not respond. Try later...")
    
    result = response.json()
    if len(result['value']) == 0:  # there are no MODELS for given MARK
        return None

    models = {}  # dict to hold MODELS values: alias and index
    # Loop through the list of MODELS and add values to the dictionary
    for model in result['value']:
        s = model['extra']['alias']
        
        # Avoid compound key, '1,2,3'
        if model['key'].find(',') >= 0:
            continue

        # Remove whitespaces
        models[s.strip()] = int(model['key'])

    return models

if __name__ == '__main__':
    import time
    assert request_models(10) == {'bertone': '1'}
    time.sleep(1)
    assert len(request_models(10)) == 1
    time.sleep(1)
    assert request_models(8) is None
    