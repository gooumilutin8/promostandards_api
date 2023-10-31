import bigcommerce
import json


class Bigcommerce:
    def __init__(self, client_id, store_hash, access_token):
        self.client_id = client_id
        self.store_hash = store_hash
        self.access_token = access_token

        self.api = bigcommerce.api.BigcommerceApi(client_id=client_id, store_hash=store_hash, access_token=access_token)
        self.v3client = bigcommerce.connection.OAuthConnection(
            client_id=client_id,
            store_hash=store_hash,
            access_token=access_token,
            api_path='/stores/{}/v3/{}'
        )

    @property
    def categories(self):
        return self.api.Categories.all()

    def create_category(self, category):
        parent = category.category
        sub_category = category.subCategory

        parent_id = None
        if type(self.categories) != list:
            parent_category = self.api.Categories.create(parent_id=0, name=parent)
            parent_id = parent_category.id

            created_category = self.api.Categories.create(parent_id=parent_id, name=sub_category)

            return created_category.id

        for category in self.categories:
            if category.name.lower() == parent.lower():
                parent_id = category.id

        if parent_id is not None:
            for category in self.categories:
                if category.name.lower() == sub_category.lower() and parent_id == category.parent_id:
                    return category.id

            created_category = self.api.Categories.create(parent_id=parent_id, name=sub_category)
            return created_category.id
        else:
            parent_category = self.api.Categories.create(parent_id=0, name=parent)
            parent_id = parent_category.id

            created_category = self.api.Categories.create(parent_id=parent_id, name=sub_category)

            return created_category.id

    def create_product(self, product_detail, inventory_levels=None, media_content=None):
        product_detail = product_detail.Product
        sku = product_detail.productId
        name = product_detail.productName
        description = product_detail.description[0]
        product_type = 'physical'

        # Check product exist in Bigcommerce store
        sku_products = self.api.Products.all(sku=sku)
        if type(sku_products) is list and len(self.api.Products.all(sku=sku)) > 0:
            return False

        # Set custom field values
        custom_fields = []
        if 'imprintSize' in product_detail:
            custom_fields.append({
                'name': 'Imprint Size',
                'value': product_detail.imprintSize
            })
        if 'defaultSetupCharge' in product_detail:
            custom_fields.append({
                'name': 'Setup Charge',
                'value': product_detail.defaultSetupCharge
            })

        for location_decoration in product_detail.LocationDecorationArray:
            if location_decoration.locationName not in [custom_field['name'] for custom_field in custom_fields]:
                if 'maxImprintColors' in location_decoration:
                    custom_fields.append({
                        'name': location_decoration.locationName,
                        'value': f'Max Imprint Colors: {location_decoration.maxImprintColors}, Price Includes: {"Yes" if location_decoration.priceIncludes else "No"}'
                    })
                else:
                    custom_fields.append({
                        'name': location_decoration.locationName,
                        'value': f'Price Includes: {"Yes" if location_decoration.priceIncludes else "No"}'
                    })

        # Creating Categories
        category_ids = []
        categories = product_detail.ProductCategoryArray
        for category in categories:
            try:
                category_id = self.create_category(category)
                category_ids.append(category_id)
            except Exception as e:
                error_data = json.loads(e.content.decode('utf-8'))[0]
                if error_data['status'] == 409:
                    category_id = error_data['details']['duplicate_category']
                    category_ids.append(category_id)
                print(e)

        # Pricing Groups
        bulk_pricing_rules = []
        pricing_group_array = product_detail.ProductPriceGroupArray[0]
        main_price = 0

        min_quantity = 2147483647

        # for pricing_group in pricing_group_array:
        product_price_array = pricing_group_array.ProductPriceArray
        for index, product_price in enumerate(product_price_array):
            discount_code = product_price.discountCode
            if discount_code in ['F', 'U', 'G', 'V', 'H', 'W', 'I', 'X']:
                multiplier = 1.43
            else:
                multiplier = 2

            price = {
                'quantity_min': product_price.quantityMin,
                'type': 'fixed',
                'amount': float(product_price.price) * 60 / 100 * multiplier
            }

            if 'quantityMax' in product_price:
                price['quantity_max'] = product_price.quantityMax
            else:
                if index < len(product_price_array) - 1:
                    price['quantity_max'] = product_price_array[index + 1].quantityMin - 1
                else:
                    price['quantity_max'] = product_price.quantityMin * 2

            bulk_pricing_rules.append(price)

            main_price = max(main_price, float(product_price.price) * 60 / 100 * multiplier)
            min_quantity = min(min_quantity, product_price.quantityMin)

        meta_keywords = [product_keyword.keyword for product_keyword in
                         product_detail.ProductKeywordArray]
        weight = float(product_detail.ProductPartArray[0].Dimension.weight)

        total_inventory_levels = 0

        variants = []
        for index, product_part in enumerate(product_detail.ProductPartArray):
            variants.append({
                'weight': float(product_part.Dimension.weight) if product_part.Dimension.weight else 0,
                'width': float(product_part.Dimension.width) if product_part.Dimension.width else 0,
                'height': float(product_part.Dimension.height) if product_part.Dimension.height else 0,
                'depth': float(product_part.Dimension.depth) if product_part.Dimension.depth else 0,
                'inventory_level': float(inventory_levels.Inventory.PartInventoryArray.PartInventory[
                                             index].quantityAvailable.Quantity.value) if inventory_levels.Inventory else 0,
                'sku': product_part.partId,
                'gtin': product_part.gtin,
                'option_values': [{
                    'option_display_name': 'Color',
                    'label': product_part.ColorArray[0].colorName
                }]
            })

            total_inventory_levels += float(inventory_levels.Inventory.PartInventoryArray[
                                        index].quantityAvailable.Quantity.value) if inventory_levels.Inventory else 0

        product = {
            'sku': sku,
            'name': name,
            'description': description,
            'type': product_type,
            'weight': weight,
            'categories': category_ids,
            'inventory_level': total_inventory_levels,
            'bulk_pricing_rules': bulk_pricing_rules,
            'variants': variants,
            'price': main_price,
            'meta_keywords': meta_keywords,
            'availability': 'available',
            'custom_fields': custom_fields,
            'inventory_tracking': 'variant',
            'purchasing_disabled': False,
            'order_quantity_minimum': min_quantity
        }

        created_product = self.v3client.create('/catalog/products', product)

        try:
            media_list = media_content.MediaContentArray

            product_data = created_product['data']

            product_id = product_data['id']

            images = []
            part_id = None
            image_data = {
                'product_id': product_id,
                'description': name,
                'is_thumbnail': True
            }
            for media in media_list:
                if media.partId != part_id:
                    images.append(image_data)
                    part_id = media.partId
                    image_data = {
                        'product_id': product_id,
                        'description': name,
                    }
                if media.width == 50:
                    image_data['url_thumbnail'] = media.url
                elif media.width == 250:
                    image_data['url_tiny'] = media.url
                elif media.width == 500:
                    image_data['url_standard'] = media.url
                elif media.width == 1200:
                    image_data['image_url'] = media.url
                    image_data['url_zoom'] = media.url
            images.append(image_data)

            for image in images:
                self.v3client.create(f'/catalog/products/{product_id}/images', image)

            variants = product_data['variants']
            for variant in variants:
                product_id = variant['product_id']
                variant_id = variant['id']
                sku = variant['sku']
                for media in media_list:
                    if media.partId == sku and media.ClassTypeArray[0].classTypeName == 'Blank':
                        image_data = {
                            'image_url': media.url
                        }
                        self.v3client.create(f'/catalog/products/{product_id}/variants/{variant_id}/image', image_data)
                        break
        except Exception as e:
            print(e)

        return created_product['data']
