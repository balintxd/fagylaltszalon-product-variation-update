from woocommerce import API
import os
from dotenv import load_dotenv

load_dotenv()

wcapi = API(
    url=os.getenv('WC_URL'),
    consumer_key=os.getenv('WC_CONSUMER_KEY'),
    consumer_secret=os.getenv('WC_CONSUMER_SECRET'),
    version='wc/v3'
)

products = []

for i in range(1, 4):
    product_params = {
        'per_page': 100,
        'type': 'variable',
        'page': i
    }

    products += wcapi.get('products', params=product_params).json()

class Row:
    def __init__(self, sku, name, slice, price_new, price_old, price_diff):
        self.sku = sku
        self.name = name
        self.slice = int(slice)
        self.price_new = int(price_new)
        self.price_old = int(price_old)
        self.price_diff = int(price_diff)

    def __str__(self):
        return '{} {} {} {} {} {}'.format(self.sku, self.name, self.slice, self.price_new, self.price_old, self.price_diff)

lines = open('data.csv', mode='r', encoding='utf-8-sig').readlines()[1:]
rows = []

for line in lines:
    item = line.strip().split(';')
    row = Row(item[0], item[1], item[2], item[3], item[4], item[5])
    rows.append(row)

for row in rows:
    update_data = {
        'update': []
    }

    for product in products:
        if product['name'] == row.name:
            for i in range(1, 3):
                variation_params = {
                    'per_page': 100,
                    'page': i
                }

                variations = wcapi.get('products/{}/variations'.format(product['id']), params=variation_params).json()

                for variation in variations:

                    for attribute in variation['attributes']:
                        if attribute['name'] == 'Szeletszám' and int(attribute['option']) == int(row.slice):
                            print('{} {} {} {} -> {}'.format(variation['id'], row.name, attribute['option'], variation['regular_price'], str(int(variation['regular_price']) + int(row.price_diff))))
                            update_data['update'].append({
                                'id': variation['id'],
                                'regular_price': str(int(variation['regular_price']) + int(row.price_diff)),
                            })

            wcapi.post('products/{}/variations/batch'.format(product['id']), update_data).json()
            print('done')
