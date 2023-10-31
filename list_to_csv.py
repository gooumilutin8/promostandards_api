import csv

from distributor_central import DistributorCentral

client_id = 'o1ot95uaobxio3uxrb59br06hg7i9bi'
store_hash = 'wivwtpaw3w'
access_token = 'd0v14qcpj6vf90blnfc1mcz36pcp923'

api_key = '223290D1-F133-497B-B5EF-653B5D06054B'
api_password = 'QJDA3JB-K3C4S2V-NYVQZ0V-29EK49Y'

suppliers = [
    # 'aaa innovations',
    # 'A+ Wine Designs',
    # 'ETS Express',
    # 'Goldstar',
    # 'Hirsch',
    # 'HIT Promotional Products',
    # 'PCNA',
    # 'Sanmar',
    # 'Spector',
    # 'St Regis Crystal',
    # 'Storm Creek',
    # 'Sunjoy',
    # 'Terrytown',
    # 'TomaxUSA',
    # 'Zing Manufacturing',
    'Ariel Premium Supply',
    'Gemline',
    'Hub Pen',
    'S&S Activewear'
]


def format_product_data(supplier_code, product, inventory_level=None):
    rows = []

    product_detail = product.Product

    # Pricing Groups
    bulk_pricing_rules = []
    pricing_group_array = product_detail.ProductPriceGroupArray[0]

    # for pricing_group in pricing_group_array:
    product_price_array = pricing_group_array.ProductPriceArray
    for index, product_price in enumerate(product_price_array):
        discount_code = product_price.discountCode
        price = {
            'quantity_min': product_price.quantityMin,
            'amount': product_price.price,
            'discount_code': discount_code
        }

        if 'quantityMax' in product_price:
            price['quantity_max'] = product_price.quantityMax
        else:
            if index < len(product_price_array) - 1:
                price['quantity_max'] = product_price_array[index + 1].quantityMin - 1
            else:
                price['quantity_max'] = product_price.quantityMin * 2

        bulk_pricing_rules.append(price)

    row = [
        supplier_code,
        product_detail.productId,
        product_detail.productName,
        product_detail.description[0],
        product_detail.imprintSize,
        None,
        None,
        None
    ]

    for pricing_rule in bulk_pricing_rules[:5]:
        row.append(pricing_rule['quantity_min'])
        row.append(pricing_rule['quantity_max'])
        row.append(pricing_rule['amount'])
        row.append(pricing_rule['discount_code'])

    rows.append(row)

    for index, product_part in enumerate(product_detail.ProductPartArray):
        try:
            part_level = inventory_level.Inventory.PartInventoryArray[index].quantityAvailable.Quantity.value
        except Exception as e:
            part_level = 0

        row = [
            supplier_code,
            product_part.partId,
            product_part.partName if product_part.partName else product_part.description[0],
            product_part.ColorArray[0].colorName if len(product_part.ColorArray) > 0 else None,
            product_part.ColorArray[0].hex if len(product_part.ColorArray) > 0 else None,
            part_level,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
        ]

        rows.append(row)

    return rows


if __name__ == '__main__':

    distributor_central_client = DistributorCentral(api_key, api_password, suppliers)

    suppliers_product_ids = distributor_central_client.get_product_ids()

    header = [
        'Supplier Code',
        'Product ID #',
        'Product Name',
        'Product Description',
        'Imprint Size',
        'Color Name',
        'Color Value',
        'Inventory Level',
        'Quantity Min',
        'Quantity Max',
        'Price',
        'Discount Code',
        'Quantity Min',
        'Quantity Max',
        'Price',
        'Discount Code',
        'Quantity Min',
        'Quantity Max',
        'Price',
        'Discount Code',
        'Quantity Min',
        'Quantity Max',
        'Price',
        'Discount Code',
        'Quantity Min',
        'Quantity Max',
        'Price',
        'Discount Code',
    ]

    for supplier_product_ids in suppliers_product_ids:
        csv_rows = []
        code = supplier_product_ids['supplier_code']
        product_ids = supplier_product_ids['product_ids']

        for product_id in product_ids:
            try:
                product_data = distributor_central_client.get_product_data(code, product_id)

                print("=========================================")
                print("SKU: ", product_data.Product.productId)
                print("Name: ", product_data.Product.productName)

                inventory_levels = distributor_central_client.get_inventory_levels(code, product_id)
                rows = format_product_data(code, product_data, inventory_levels)
                csv_rows = csv_rows + rows
            except Exception as e:
                print(e)

        with open(f'product_data_{code}.csv', 'w', newline='', encoding='utf-8') as csv_file:
            writer = csv.writer(csv_file, delimiter=',')
            writer.writerow(header)
            writer.writerows(csv_rows)
