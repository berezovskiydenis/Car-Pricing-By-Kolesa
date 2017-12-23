# API for average car price in KZ

You can request average car price in KZ by given mark, model and year.

To start working you have to build cars catalog. It can take up to 10 minutes
depending on your channel bandwidth and remote server availability.

You can save cars catalog to the persistence layer (DB) to avoid rebuild catalog
every time you run script.

To start using app install requirements and use `kolesa_catalog.py`:

```
cc = CarCatalog()  # Create catalog and DB
print(cc.car_price('toyota', 'camry', 2002))  # 2837778
print(cc.car_price('isuzu', 'trooper', 1998))
```

After running script for the first time DB will be created. Further DB will be
used as a catalog data.
