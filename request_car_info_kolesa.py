import requests


def request_car_info(mark, model, year):
    """Request remote server 'kolesa.kz' with given mark, model and yaer.
    
        Return tuple (car title, average price, mark alias, model alias).
        Otherwise return None.
    """

    url = "https://kolesa.kz/analytics/"
    querystring = {"mark": mark, "model": model, "year": year}
    headers = {
        'content-type': "application/json",
        'x-requested-with': "XMLHttpRequest",
        'cache-control': "no-cache"
        }
    
    try:
        response = requests.get(url, headers=headers, params=querystring, timeout=5)
    except requests.exceptions.ReadTimeout as e:
        requests.exceptions.ReadTimeout("\nRemote server does not respond. Try later...")
    
    result = response.json()
        
    if response.status_code != 200:
        return None

    _title = result['data']['title']
    _price = result['data']['avgPrice']
    _mark_alias = result['data']['url'].split('/')[2]
    _model_alias = result['data']['url'].split('/')[3]
    
    # If mark's alias part in ulr is empty then no such car exists
    if len(_mark_alias) == 0:
        return None
    
    return (_title.strip(), _price, _mark_alias, _model_alias)


def request_car_price(mark, model, year):
    """Request remote server 'kolesa.kz'.

        Return car's average price for given mark, model and year.
        Otherwise return None.
    """

    result = request_car_info(mark, model, year)

    if result is None:
        return None

    return result[1]

    
if __name__ == '__main__':
    assert request_car_info(10, 12, 1999) is None
    assert request_car_info(86, 1, 1999) == ('Skoda 1203, 1999 года', 0, 'skoda', '1203')
    assert request_car_info(66, 2, 2005) == ('Nissan 100SX, 2005 года', 0, 'nissan', '100sx')

    assert request_car_price(10, 12, 1999) is None
    assert request_car_price(86, 1, 1999) == 0
    assert request_car_price(3, 2, 2005) == 455075
    assert request_car_price(9, 2, 2005) == 9999000
    assert request_car_price(96, 12, 2002) == 2837778