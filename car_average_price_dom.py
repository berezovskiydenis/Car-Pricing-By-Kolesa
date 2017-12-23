import time
import json
import requests
from datetime import date
from requests.exceptions import ReadTimeout
from bs4 import BeautifulSoup


def build_indexes():
    cars = {}  # dict for cars: marks and models and their indexes
    
    # Make dummy request to get MARKS catalog
    URL = "https://kolesa.kz/analytics/"
    payload = {'mark': '1', 'model': '1', 'year': '2015'}  # Use just dummy data
    try:
        r = requests.get(URL, params=payload, timeout=5)
    except ReadTimeout as tmout:
        raise ReadTimeout('Remote server did not respond. Try later...')
    

    # DOM objects are used to read the MARKS
    soup = BeautifulSoup(r.text, 'html.parser')

    # Car's Models are located in unnumbered list 'ul'
    marks = soup.find('ul', class_="selectbox-options")
    for mark in marks.find_all('li')[2:]:  # first two rows are common data, not cars
        try:
            cars[mark['data-alias']] = {'_index': mark['data-value']}
        except KeyError as i:
            # Continue if DOM object '<li>' does not contain attributes
            continue


    # By this point we have MARKS catalog in 'car' dict.
    # We are going to loop through catalog and make requests for each MARK
    # to receive MODELS catalog
    for k, v in cars.items():
        # Build new request for each MARK to get MODELS catalog
        payload = {'mark': str(v['_index']), 'model': '1', 'year': '2015'}
        try:
            r = requests.get(URL, params=payload, timeout=5)
        except ReadTimeout as tmout:
            raise ReadTimeout('Remote server did not respond. Try later...')

        # Use DOM objects. MODELS are located in the second list 'ul' on page
        soup = BeautifulSoup(r.text, 'html.parser')
        marks = soup.find_all('ul', class_="selectbox-options")[1]
        
        # Loop through each MODEL '<li>' in the list '<ul>'
        for model in marks.find_all('li'):
            try:
                cars[k][model['data-alias']] = model['data-value']
            except KeyError as e:
                continue

        time.sleep(10)  # Use timer to sleep otherwise ToManyRequses Error

    # Parse cars dict to JSON object
    json.dump(cars, open('res.json', 'w'))

    return dict



class CarsCatalog:
    def __init__(self):
        self._catalog = {}  # dictionary for cars and models
        self._most_often_used = {}  # cars that are requested more often
        if self._load_catalog():
            print("Cars catalog was uploaded.")
        else:
            print("Cars catalog is empty. You must build cars catalog using appropriate method.")
    
    
    def __len__(self):
        """Marks size of catalog."""
        return len(self._catalog)
    
    
    def _load_catalog(self):
        """Read catalog from filesystem. If file not found return NotFound error."""
        try:
            self._catalog = json.load(open('res.json'))
            return True
        except FileNotFoundError as ferr:
            return False
    

    def get_price(self, model, mark, year):
        """"Request car average price. Return tuple (price, car title)."""
        # Validate catalog
        if len(self._catalog) == 0:
            raise ValueError("Car catalog is empty. Build car catalog.")
        
        # Find index for mark
        try:
            mark_index = self._catalog[model.lower()]['_index']
        except KeyError as e:
            raise KeyError('{} does not exists'.format(mark))
        
        # Find index for model
        try:
            model_index = self._catalog[model.lower()][mark.lower()]
        except KeyError as e:
            raise KeyError('{} does not exists'.format(model))
        
        # Check if car has been requested 'today'. Memoization technique is used
        car_exists = self._most_often_used.get((mark_index, model_index))
        if car_exists is not None:
            if car_exists['date'] == date.today():
                return (car_exists['price'], car_exists['title'])
            elif car_exists['date'] < date.today():  # old data
                del self._most_often_used[(mark_index, model_index)]
        
        # Make request
        URL = "https://kolesa.kz/analytics/"
        payload = {"mark": mark_index, "model": model_index,"year": str(year)}
        headers = {
            'content-type': "application/json",
            'x-requested-with': "XMLHttpRequest",
            'cache-control': "no-cache",
            }
        response = requests.request("GET", URL, headers=headers, params=payload, timeout=5)
        json_response = response.json()
        car_price = json_response['data']['avgPrice']
        car_title = json_response['data']['title']

        self._most_often_used[(mark_index, model_index)] = {
            'date': date.today(),
            'price': car_price,
            'title': car_title
        }

        return (car_price, car_title)


    def scrape_catalog(self):
        """Build marks and models catalog by scrapping 'kolesa' web page.
        
        Method takes some time to complete, please be patient.
        """
        print("Start building cars catalog. It takes time...")
         # Make dummy request to get MARKS catalog
        URL = "https://kolesa.kz/analytics/"
        payload = {'mark': '1', 'model': '1', 'year': '2015'}  # Use just dummy data
        try:
            r = requests.get(URL, params=payload, timeout=10)
        except ReadTimeout as tmout:
            raise ReadTimeout('Remote server did not respond. Try later...')
        
        # DOM objects are used to read the MARKS
        soup = BeautifulSoup(r.text, 'html.parser')

        # Car's Models are located in unnumbered list 'ul'
        marks = soup.find('ul', class_="selectbox-options")
        for mark in marks.find_all('li')[2:]:  # first two rows are common data, not cars
            try:
                self._catalog[mark['data-alias']] = {'_index': mark['data-value']}
            except KeyError as i:
                # Continue if DOM object '<li>' does not contain attributes
                continue
        print("Marks catalog has been built...")

        # By this point we have MARKS catalog in 'car' dict.
        # We are going to loop through catalog and make requests for each MARK
        # to receive MODELS catalog
        i = 1
        for k, v in self._catalog.items():
            print('({} / {}) Models for {} are being built...'.format(i, len(self._catalog), k))
            # Build new request for each MARK to get MODELS catalog
            payload = {'mark': str(v['_index']), 'model': '1', 'year': '2015'}
            try:
                r = requests.get(URL, params=payload, timeout=10)
            except ReadTimeout as tmout:
                raise ReadTimeout('Remote server did not respond. Try later...')

            # Use DOM objects. MODELS are located in the second list 'ul' on page
            soup = BeautifulSoup(r.text, 'html.parser')
            marks = soup.find_all('ul', class_="selectbox-options")[1]
            
            # Loop through each MODEL '<li>' in the list '<ul>'
            for model in marks.find_all('li'):
                try:
                    self._catalog[k][model['data-alias']] = model['data-value']
                except KeyError as e:
                    continue

            time.sleep(15)  # Use timer to sleep otherwise ToManyRequses Error
            i += 1
        print("Catalog was build successfuly. It contains {} marks".format(len(self._catalog)))




if __name__ == '__main__':
    c = CarsCatalog()
    c.scrape_catalog()
    assert len(c) > 0
    