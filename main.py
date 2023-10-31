# from bigcommerce_service import Bigcommerce
from distributor_central import DistributorCentral
import json

client_id = 'o1ot95uaobxio3uxrb59br06hg7i9bi'
store_hash = 'wivwtpaw3w'
access_token = 'd0v14qcpj6vf90blnfc1mcz36pcp923'

api_key = '223290D1-F133-497B-B5EF-653B5D06054B'
api_password = 'QJDA3JB-K3C4S2V-NYVQZ0V-29EK49Y'

suppliers = [
    # 'ETS',
    # 'PCNA',
    # 'HIT Promotional Products',
    # 'Ariel Premium Supply',
    # 'Gemline',
    # 'Hub Pen',
    'ETS Express'
    # 'S&S Activewear'
    # 'STOPNGO Line',
    # 'Snugz',
    # 'Alpi International, Ltd.',
    # 'Imagen Brands'
]

if __name__ == '__main__':
    # bigCommerce = Bigcommerce(client_id, store_hash, access_token)

    distributor_central_client = DistributorCentral(api_key, api_password, suppliers)

    suppliers_product_ids = distributor_central_client.get_product_ids()
    for supplier_product_ids in suppliers_product_ids:
        code = supplier_product_ids['supplier_code']
        product_ids = supplier_product_ids['product_ids']
        # product_id = product_ids[0]
        product_id = '1403'

        # for product_id in product_ids:
        product_data = distributor_central_client.get_product_data(code, product_id)

        print("=========================================")
        print("SKU: ", product_data.Product.productId)
        print("Name: ", product_data.Product.productName)

        inventory_levels = distributor_central_client.get_inventory_levels(code, product_id)
        media_content = distributor_central_client.get_media_content(code, product_id)

        media_content_array = media_content.MediaContentArray

        filtered_media_content_array = []
        for media_content_item in media_content_array:
            classTypes = media_content_item.ClassTypeArray
            for classType in classTypes:
                if classType.classTypeName == 'Primary':
                    filtered_media_content_array.append(media_content_item)
                    break

        print(filtered_media_content_array)

        max_resolutions = {}

        for filtered_media_content in filtered_media_content_array:
            if filtered_media_content.partId not in max_resolutions:
                max_resolutions[filtered_media_content.partId] = {
                    'width': filtered_media_content.width,
                    'urls': [filtered_media_content.url]
                }
            else:
                if max_resolutions[filtered_media_content.partId]['width'] == filtered_media_content.width:
                    max_resolutions[filtered_media_content.partId]['urls'].append(filtered_media_content.url)
                if max_resolutions[filtered_media_content.partId]['width'] < filtered_media_content.width:
                    max_resolutions[filtered_media_content.partId] = {
                        'width': filtered_media_content.width,
                        'urls': [filtered_media_content.url]
                    }

        print(max_resolutions)

        fobs = distributor_central_client.get_fobs(code, product_id)

        ppc_data = []
        for fob in fobs.FobPointArray:
            config_data = distributor_central_client.get_product_price_config(code, product_id, fob.fobId)
            ppc_data.append(config_data)

        print(product_data)

        # product = bigCommerce.create_product(product_data, inventory_levels, media_content)

        # if product is False:
        #     print("Product Already Exist")
        # else:
        #     print("Product ID: ", product['id'])
