import requests
from typing import List
from munch import DefaultMunch
import json


class DistributorCentral:
    codes = []

    def __init__(self, api_key: str, api_password: str, suppliers: List[str]):
        self.api_key = api_key
        self.api_password = api_password
        self.suppliers = suppliers
        self.map_supplier_to_code()

    def map_supplier_to_code(self):
        url = 'https://api.dc-onesource.com/ps/companies'
        response = requests.get(url)
        companies = response.json()
        l_company_names = [company['Name'].lower() for company in companies]
        l_company_codes = [company['Code'].lower() for company in companies]
        company_codes = [company['Code'] for company in companies]
        for supplier in self.suppliers:
            if supplier.lower() in l_company_names:
                index = l_company_names.index(supplier.lower())
                code = company_codes[index]
                self.codes.append(code)
            elif supplier.lower() in l_company_codes:
                index = l_company_codes.index(supplier.lower())
                code = company_codes[index]
                self.codes.append(code)

    def get_auth_header(self):
        return {
            'Authorization': self.api_key + '|' + self.api_password
        }

    def get_product_ids(self):
        result = []
        for code in self.codes:
            url = f"https://api.dc-onesource.com/json/{code}/ps/product/getProductSellable"
            headers = self.get_auth_header()

            response = requests.get(url, headers=headers)
            data = response.json()
            if 'ProductSellableArray' in data['data']:
                product_ids_array = data['data']['ProductSellableArray']

                product_ids = []

                for product_id_data in product_ids_array:
                    product_ids.append(product_id_data['productId'])

                distinct_product_ids = list(set(product_ids))
                distinct_product_ids.sort()

                result.append({
                    'supplier_code': code,
                    'product_ids': distinct_product_ids
                })

        return result

    def get_product_data(self, supplier_code: str, product_id: str, to_object: bool = True):
        url = f'https://api.dc-onesource.com/json/{supplier_code}/ps/product/getProduct/{product_id}?localizationCountry=US'
        headers = self.get_auth_header()
        response = requests.get(url, headers=headers)
        data = response.json()
        if not to_object:
            return data['data']['Product']
        return DefaultMunch.fromDict(data['data'])

    def get_inventory_levels(self, supplier_code: str, product_id: str, to_object: bool = True):
        url = f'https://api.dc-onesource.com/json/{supplier_code}/ps/inv/getInventoryLevels/{product_id}'
        headers = self.get_auth_header()
        response = requests.get(url, headers=headers)
        data = response.json()

        if 'errors' in data:
            return None
        if 'data' not in data:
            return None
        try:
            if not to_object:
                return data['data']['Inventory']
            return DefaultMunch.fromDict(data['data'])
        except Exception as e:
            print(e)
            return None

    def get_media_content(self, supplier_code: str, product_id: str, to_object: bool = True):
        url = f'https://api.dc-onesource.com/json/{supplier_code}/ps/med/getMediaContent/{product_id}'
        headers = self.get_auth_header()
        response = requests.get(url, headers=headers)
        data = response.json()
        try:
            if not to_object:
                return data['data']['MediaContentArray']
            return DefaultMunch.fromDict(data['data'])
        except Exception as e:
            return []

    def get_fobs(self, supplier_code: str, product_id: str, to_object: bool = True):
        url = f'https://api.dc-onesource.com/json/{supplier_code}/ps/ppc/getFobPoints/{product_id}'
        headers = self.get_auth_header()
        response = requests.get(url, headers=headers)
        data = response.json()
        try:
            if not to_object:
                return data['data']['FobPointArray']
            return DefaultMunch.fromDict(data['data'])
        except Exception as e:
            return []

    def get_product_price_config(self, supplier_code: str, product_id: str, fob_id: str, to_object: bool = True):
        url = f'https://api.dc-onesource.com/json/{supplier_code}/ps/ppc/getConfigurationAndPricing/{product_id}?fobId={fob_id}&priceType=List'
        headers = self.get_auth_header()
        response = requests.get(url, headers=headers)
        data = response.json()
        try:
            if not to_object:
                return data['data']['Configuration']
            return DefaultMunch.fromDict(data['data'])
        except Exception as e:
            return []
