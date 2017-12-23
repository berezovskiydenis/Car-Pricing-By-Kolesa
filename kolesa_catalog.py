import os
import time
import sqlite3
from datetime import date

from request_models_kolesa import request_models
from request_car_info_kolesa import request_car_info, request_car_price


class CarCatalog:

    def __init__(self):
        self.catalog = {}  # marks and models
        if len(self.catalog) == 0:  # If catalog is empty
            if not self.load_persistence_layer():  # then load it from memory
                self.scrape_it()  # if persistence layer not exists load it
                self.create_persistence_layer()  # and create it


    def scrape_it(self, how_many_cars=201):
        # Suppose catalog has up to 200 marks
        for mark_counter in range(1, how_many_cars):

            # Query for models for current mark_counter
            models_dict = request_models(mark_counter)
            
            # Let it sleep to avoid kolesa's developers pain in ass
            time.sleep(1)

            if models_dict is None:
                continue

            # Query for mark information for current mark_counter
            current_mark = request_car_info(mark_counter, 1, date.today().year)

            # Let it sleep to avoid kolesa's developers pain in ass
            time.sleep(1)

            if current_mark is None:
                continue

            # Add values to the catalog
            self.catalog[current_mark[2]] = {'index': mark_counter}
            self.catalog[current_mark[2]]['models'] = models_dict
        
        return True

    def load_persistence_layer(self):
        """Load data from local DB to the class' dictionary."""
        if not os.path.exists('car_catalog.db'):
            return False
        
        self.catalog.clear()
        
        with sqlite3.connect('car_catalog.db') as conn:
            c = conn.cursor()
            r = """select marks.mark_alias, marks.mark_index, models.model_alias, models.model_index
                from marks left join models on marks.mark_index = models.mark_index
                order by marks.mark_index, models.model_index
                """
            # Load marks
            c.execute("SELECT mark_alias, mark_index FROM marks ORDER BY mark_index")
            marks = c.fetchall()  # list [('bmw', 1), ('audi', 2), ...]            

            # Load models
            c.execute(r)
            models = c.fetchall() # list [('bmw', 1, '320', 1), ('audi', 2, 'a8', 1), ...]

            for mark in marks:
                self.catalog[mark[0]] = {'index': mark[1], 'models': {}}
            
            for model in models:
                self.catalog[model[0]]['models'][model[2]] = model[3]
        
        return True


    def create_persistence_layer(self):
        """Create local Sqlite DB and parse data to the 2 tables."""
        
        if os.path.exists('car_catalog.db'):
            os.remove('car_catalog.db')
            print('\nDB deleted... New DB is about to be created...')
        
        with sqlite3.connect('car_catalog.db') as conn:
            c = conn.cursor()

            # Create 2 tables for marks and models
            c.execute("""CREATE TABLE marks (mark_index INTEGER, mark_alias TEXT)""")
            c.execute("""CREATE TABLE models (mark_index INTEGER, model_index INTEGER, model_alias TEXT)""")
            
            # Prepare list of marks and insert them to the table
            marks = [(x[0], x[1]['index']) for x in self.catalog.items()]
            c.executemany("INSERT INTO marks (mark_alias, mark_index) VALUES (?, ?)", marks)
            conn.commit()

            # Prepare list of models and insert them to the table
            models = []
            # Append data to the list in format (mark_index, model_alias, model_index)
            for i in self.catalog.values():
                for m in i['models'].items():
                    models.append((i['index'], m[0], m[1]))
            c.executemany("INSERT INTO models (mark_index, model_alias, model_index) VALUES (?, ?, ?)", models)
            conn.commit()
        return True
    
    def car_price(self, mark, model, year):
        """Return average price for given car."""
        
        if len(self.catalog) == 0:
            raise ValueError("Catalog is empty.")
        
        try:
            _mark = self.catalog[mark]['index']
            _model = self.catalog[mark]['models'][model]
        except KeyError as i:
            raise KeyError("Car {} {} not found".format(mark, model))
        
        return request_car_price(_mark, _model, year)
        


if __name__ == '__main__':
    cc = CarCatalog()
    assert cc.car_price('toyota', 'camry', 2002) == 2837778
    print(cc.car_price('isuzu', 'trooper', 1998))
