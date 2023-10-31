import requests
from distributor_central import DistributorCentral
import json

client_id = 'o1ot95uaobxio3uxrb59br06hg7i9bi'
store_hash = 'wivwtpaw3w'
access_token = 'd0v14qcpj6vf90blnfc1mcz36pcp923'

api_key = '223290D1-F133-497B-B5EF-653B5D06054B'
api_password = 'QJDA3JB-K3C4S2V-NYVQZ0V-29EK49Y'

admin_api_server = 'http://127.0.0.1:8000/api/v1/admin'
admin_api_server_user_name = 'test@gmail.com'
admin_api_server_password = '123'

if __name__ == '__main__':
    result = requests.post(f'{admin_api_server}/auth/login', data=json.dumps({
        'email': admin_api_server_user_name,
        'password': admin_api_server_password
    }), headers={
        'Content-Type': 'application/json',
    })

    cookie = result.cookies['cm_admin_token']

    response = requests.get(f'{admin_api_server}/suppliers', headers={
        'Accept': 'application/json, text/plain, */*',
        'Cookie': f'cm_admin_token={cookie}'
    })
    data = response.json()

    suppliers_data = data['data']

    response = requests.get(f'{admin_api_server}/suppliers', headers={
        'Accept': 'application/json, text/plain, */*',
        'Cookie': f'cm_admin_token={cookie}'
    })
    data = response.json()

    suppliers = [supplier_data['name'] for supplier_data in suppliers_data if supplier_data['supplier_status'] == 'active']

    distributor_central_client = DistributorCentral(api_key, api_password, suppliers)

    suppliers_product_ids = distributor_central_client.get_product_ids()
    for supplier_product_ids in suppliers_product_ids:
        code = supplier_product_ids['supplier_code']
        product_ids = supplier_product_ids['product_ids']

        for product_id in product_ids:
            product_data = distributor_central_client.get_product_data(code, product_id, False)

            print("=========================================")
            print("SKU: ", product_data['productId'])
            print("Name: ", product_data['productName'])

            inventory_levels = distributor_central_client.get_inventory_levels(code, product_id, False)
            media_content = distributor_central_client.get_media_content(code, product_id, False)

            part_ids = [product_part['partId'] for product_part in product_data['ProductPartArray']]
            for part_id in part_ids:
                if part_id in product_ids and part_id != product_id:
                    product_ids.remove(part_id)
                    media_content = media_content + distributor_central_client.get_media_content(code, part_id, False)

            product_data['Inventory'] = inventory_levels
            product_data['MediaContentArray'] = media_content
            product_data['supplier'] = code

            response = requests.post(f'{admin_api_server}/products/from_dc', headers={
                'Content-Type': 'application/json',
                'Accept': 'application/json, text/plain, */*',
                'Cookie': f'cm_admin_token={cookie}'
            }, data=json.dumps(product_data))
            data = response.json()
