from zeep import Client


class PromoStandard:
    def __init__(self, supplier):
        self.id = supplier['id']
        self.password = supplier['password']
        self.inv = supplier['inv']
        self.product = supplier['product']
        self.ppc = supplier['ppc']
        self.media = supplier['media']
        self.product_client = Client(self.product)
        self.inv_client = Client(self.inv)
        self.ppc_client = Client(self.ppc)
        self.media_client = Client(self.media)

    def get_sellable_products(self):
        request_data = {
            'id': self.id,
            'password': self.password,
            'wsVersion': '2.0.0',
            'localizationCountry': 'US',
            'localizationLanguage': 'en',
            'isSellable': 1
        }

        response = self.product_client.service.getProductSellable(**request_data)

        return response

    def get_product_detail(self, product_id, part_id=None):
        request_data = {
            'id': self.id,
            'password': self.password,
            'wsVersion': '2.0.0',
            'localizationCountry': 'US',
            'localizationLanguage': 'en',
            'productId': product_id,
        }

        if part_id:
            request_data['partId'] = part_id

        response = self.product_client.service.getProduct(**request_data)

        return response

    def get_inventory_levels(self, product_id):
        request_data = {
            'id': self.id,
            'password': self.password,
            'wsVersion': '2.0.0',
            'productId': product_id,
        }

        response = self.inv_client.service.getInventoryLevels(**request_data)

        return response

    def get_media_content(self, product_id):
        request_data = {
            'id': self.id,
            'password': self.password,
            'wsVersion': '2.0.0',
            'productId': product_id,
            'mediaType': 'Image'
        }

        response = self.media_client.service.getMediaContent(**request_data)

        return response

