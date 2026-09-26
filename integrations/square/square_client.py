
# ============================================================
# SMARTSTOCK AI
# Square API Client
# ============================================================

from config.config import (
    SQUARE_ACCESS_TOKEN,
    SQUARE_BASE_URL
)

import requests
import uuid
from datetime import datetime, timezone


class SquareClient:
    """
    هذا الكلاس مسؤول عن الاتصال بـ Square API.
    """

    def __init__(self):

        # حفظ رابط Square API
        self.base_url = SQUARE_BASE_URL

        # حفظ Access Token
        self.access_token = SQUARE_ACCESS_TOKEN

        # إنشاء Headers للطلبات
        self.headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
            "Accept": "application/json",

            # إصدار Square API المستخدم في المشروع
            "Square-Version": "2026-09-16"
        }

    # ============================================================
    # اختبار الاتصال بـ Square
    # ============================================================

    def test_connection(self):
        """
        اختبار الاتصال بـ Square.
        """

        if not self.access_token:

            print("Square Access Token: NOT SET")
            print("Connection test skipped.")

            return False

        try:

            response = requests.get(
                f"{self.base_url}/locations",
                headers=self.headers,
                timeout=10
            )

            print("HTTP Status:", response.status_code)

            if response.status_code == 200:

                print("Square API Connection: SUCCESS")

                return True

            else:

                print("Square API Connection: FAILED")
                print("Response:", response.text)

                return False

        except requests.exceptions.RequestException as error:

            print("Connection Error:")
            print(error)

            return False

    # ============================================================
    # جلب المنتجات من Square Catalog
    # ============================================================

    def get_catalog_items(self):
        """
        جلب المنتجات من Square Catalog API.
        """

        if not self.access_token:

            print("Square Access Token: NOT SET")

            return None

        try:

            response = requests.get(
                f"{self.base_url}/catalog/list",
                headers=self.headers,
                params={
                    "types": "ITEM,ITEM_VARIATION"
                },
                timeout=10
            )

            print(
                "Catalog API HTTP Status:",
                response.status_code
            )

            if response.status_code == 200:

                data = response.json()

                items = data.get("objects", [])

                print(
                    "Number of Catalog Objects:",
                    len(items)
                )

                return items

            else:

                print("Catalog API Request Failed")
                print("Response:", response.text)

                return None

        except requests.exceptions.RequestException as error:

            print("Catalog API Connection Error:")
            print(error)

            return None

    # ============================================================
    # جلب مواقع النشاط التجاري
    # ============================================================

    def get_locations(self):
        """
        جلب مواقع النشاط التجاري من Square.
        """

        if not self.access_token:

            print("Square Access Token: NOT SET")

            return None

        try:

            response = requests.get(
                f"{self.base_url}/locations",
                headers=self.headers,
                timeout=10
            )

            print(
                "Locations API HTTP Status:",
                response.status_code
            )

            if response.status_code == 200:

                data = response.json()

                locations = data.get("locations", [])

                print(
                    "Number of Locations:",
                    len(locations)
                )

                return locations

            else:

                print("Locations API Request Failed")
                print("Response:", response.text)

                return None

        except requests.exceptions.RequestException as error:

            print("Locations API Connection Error:")
            print(error)

            return None

    # ============================================================
    # إنشاء منتج جديد
    # ============================================================

    def create_catalog_item(self, name, price):
        """
        إنشاء منتج جديد داخل Square Catalog.
        """

        if not self.access_token:

            print("Square Access Token: NOT SET")

            return None

        try:

            temporary_id = "#" + str(uuid.uuid4())

            payload = {

                "idempotency_key": str(uuid.uuid4()),

                "object": {

                    "type": "ITEM",

                    "id": temporary_id,

                    "item_data": {

                        "name": name,

                        "description":
                            "منتج تجريبي لمشروع SmartStock AI",

                        "variations": [

                            {

                                "type": "ITEM_VARIATION",

                                "id":
                                    "#" + str(uuid.uuid4()),

                                "item_variation_data": {

                                    "item_id":
                                        temporary_id,

                                    "name":
                                        "Regular",

                                    "pricing_type":
                                        "FIXED_PRICING",

                                    "price_money": {

                                        "amount":
                                            int(price * 100),

                                        "currency":
                                            "USD"
                                    }
                                }
                            }
                        ]
                    }
                }
            }

            response = requests.post(

                f"{self.base_url}/catalog/object",

                headers=self.headers,

                json=payload,

                timeout=10
            )

            print(
                "Create Catalog HTTP Status:",
                response.status_code
            )

            if response.status_code in [200, 201]:

                data = response.json()

                print(
                    "Catalog Item Created Successfully"
                )

                return data

            else:

                print(
                    "Create Catalog Item Failed"
                )

                print(
                    "Response:",
                    response.text
                )

                return None

        except requests.exceptions.RequestException as error:

            print(
                "Create Catalog Connection Error:"
            )

            print(error)

            return None

    # ============================================================
    # جلب كمية المخزون
    # ============================================================


    def get_inventory_count(
                self,
                catalog_object_id=None,
                location_id=None
        ):
            """
            جلب الكمية الحالية من مخزون Square.

            إذا تم تمرير catalog_object_id:
                يتم جلب مخزون منتج/Variation محدد.

            إذا كان catalog_object_id = None:
                يتم استخدام Batch Retrieve لجلب جميع
                كميات المخزون في الموقع المحدد.

            لا يتم وضع أي كمية ثابتة داخل الكود.
            جميع الكميات تأتي مباشرة من Square API.
            """

            if not self.access_token:
                print("Square Access Token: NOT SET")

                return []

            try:

                # ====================================================
                # الحالة الأولى:
                # جلب مخزون Variation / Catalog Object محدد
                # ====================================================

                if catalog_object_id:

                    response = requests.get(

                        f"{self.base_url}/inventory/{catalog_object_id}",

                        headers=self.headers,

                        params={
                            "location_ids": location_id
                        } if location_id else {},

                        timeout=10
                    )

                    print(
                        "Inventory API HTTP Status:",
                        response.status_code
                    )

                    if response.status_code == 200:
                        data = response.json()

                        counts = data.get(
                            "counts",
                            []
                        )

                        print(
                            "Number of Inventory Counts:",
                            len(counts)
                        )

                        return counts

                    print(
                        "Inventory API Request Failed:"
                    )

                    print(
                        response.text
                    )

                    return []

                # ====================================================
                # الحالة الثانية:
                # جلب جميع كميات المخزون
                # ====================================================

                url = (
                    f"{self.base_url}"
                    "/inventory/counts/batch-retrieve"
                )

                payload = {}

                if location_id:
                    payload["location_ids"] = [
                        location_id
                    ]

                # نطلب فقط العناصر الموجودة في المخزون.
                payload["states"] = [
                    "IN_STOCK"
                ]

                payload["limit"] = 1000

                response = requests.post(

                    url,

                    headers=self.headers,

                    json=payload,

                    timeout=20
                )

                print(
                    "Inventory Batch API HTTP Status:",
                    response.status_code
                )

                if response.status_code != 200:
                    print(
                        "Inventory Batch API Request Failed:"
                    )

                    print(
                        response.text
                    )

                    return []

                data = response.json()

                counts = data.get(
                    "counts",
                    []
                )

                print(
                    "Number of Inventory Counts:",
                    len(counts)
                )

                # ====================================================
                # التعامل مع Pagination
                # ====================================================

                all_counts = list(counts)

                cursor = data.get(
                    "cursor"
                )

                while cursor:

                    payload["cursor"] = cursor

                    response = requests.post(

                        url,

                        headers=self.headers,

                        json=payload,

                        timeout=20
                    )

                    if response.status_code != 200:
                        print(
                            "Inventory Pagination Request Failed:"
                        )

                        print(
                            response.text
                        )

                        break

                    page_data = response.json()

                    page_counts = page_data.get(
                        "counts",
                        []
                    )

                    all_counts.extend(
                        page_counts
                    )

                    cursor = page_data.get(
                        "cursor"
                    )

                print(
                    "Total Inventory Counts:",
                    len(all_counts)
                )

                return all_counts

            except requests.exceptions.RequestException as error:

                print(
                    "Inventory API Connection Error:"
                )

                print(error)

                return []



    # ============================================================
    # إضافة كمية إلى المخزون
    # ============================================================

    def add_inventory_stock(
        self,
        catalog_object_id,
        location_id,
        quantity
    ):
        """
        إضافة كمية جديدة إلى مخزون منتج في Square.
        """

        if not self.access_token:

            print("Square Access Token: NOT SET")

            return None

        try:

            payload = {

                "idempotency_key":
                    str(uuid.uuid4()),

                "changes": [

                    {

                        "type":
                            "ADJUSTMENT",

                        "adjustment": {

                            "from_state":
                                "NONE",

                            "to_state":
                                "IN_STOCK",

                            "catalog_object_id":
                                catalog_object_id,

                            "from_location_id":
                                location_id,

                            "to_location_id":
                                location_id,

                            "quantity":
                                str(quantity),

                            "occurred_at":
                                datetime.now(
                                    timezone.utc
                                ).isoformat()
                        }
                    }
                ]
            }

            response = requests.post(

                f"{self.base_url}/inventory/changes/batch-create",

                headers=self.headers,

                json=payload,

                timeout=10
            )

            print(
                "Add Inventory HTTP Status:",
                response.status_code
            )

            if response.status_code == 200:

                data = response.json()

                print(
                    "Inventory Stock Added Successfully"
                )

                return data

            else:

                print(
                    "Add Inventory Failed"
                )

                print(
                    "Response:",
                    response.text
                )

                return None

        except requests.exceptions.RequestException as error:

            print(
                "Inventory API Connection Error:"
            )

            print(error)

            return None

    # ============================================================
    # جلب الطلبات والمبيعات المكتملة
    # ============================================================

    def get_orders(
        self,
        location_id,
        limit=20
    ):
        """
        جلب الطلبات المكتملة من Square.
        """

        if not self.access_token:

            print("Square Access Token: NOT SET")

            return None

        try:

            payload = {

                "location_ids": [
                    location_id
                ],

                "query": {

                    "filter": {

                        "state_filter": {

                            "states": [
                                "COMPLETED"
                            ]
                        },

                        "date_time_filter": {

                            "created_at": {

                                "start_at":
                                    "2026-09-23T00:00:00Z"
                            }
                        }
                    },

                    "sort": {

                        "sort_field":
                            "CREATED_AT",

                        "sort_order":
                            "DESC"
                    }
                },

                "limit":
                    limit
            }

            response = requests.post(

                f"{self.base_url}/orders/search",

                headers=self.headers,

                json=payload,

                timeout=10
            )

            print(
                "Orders API HTTP Status:",
                response.status_code
            )

            if response.status_code == 200:

                data = response.json()

                orders = data.get(
                    "orders",
                    []
                )

                print(
                    "Number of Orders:",
                    len(orders)
                )

                return orders

            else:

                print(
                    "Orders API Request Failed"
                )

                print(
                    "Response:",
                    response.text
                )

                return None

        except requests.exceptions.RequestException as error:

            print(
                "Orders API Connection Error:"
            )

            print(error)

            return None

    # ============================================================
    # جلب Order محدد باستخدام Order ID
    # ============================================================

    def get_order(self, order_id):
        """
        جلب تفاصيل Order مباشرة من Square.
        """

        if not self.access_token:

            print("Square Access Token: NOT SET")

            return None

        try:

            endpoint = (
                f"{self.base_url}/orders/{order_id}"
            )

            response = requests.get(

                endpoint,

                headers=self.headers,

                timeout=10
            )

            print(
                "Get Order HTTP Status:",
                response.status_code
            )

            if response.status_code == 200:

                data = response.json()

                return data.get(
                    "order"
                )

            else:

                print(
                    "Order Error:"
                )

                print(
                    response.text
                )

                return None

        except requests.exceptions.RequestException as error:

            print(
                "Get Order API Connection Error:"
            )

            print(error)

            return None

    # ============================================================
    # إنشاء Order
    # ============================================================

    def create_order(
        self,
        location_id,
        catalog_object_id,
        quantity=1
    ):
        """
        إنشاء طلب جديد في Square.
        """

        if not self.access_token:

            print("Square Access Token: NOT SET")

            return None

        try:

            payload = {

                "idempotency_key":
                    str(uuid.uuid4()),

                "order": {

                    "location_id":
                        location_id,

                    "line_items": [

                        {

                            "catalog_object_id":
                                catalog_object_id,

                            "quantity":
                                str(quantity)
                        }
                    ]
                }
            }

            response = requests.post(

                f"{self.base_url}/orders",

                headers=self.headers,

                json=payload,

                timeout=10
            )

            print(
                "Create Order HTTP Status:",
                response.status_code
            )

            if response.status_code == 200:

                data = response.json()

                order = data.get(
                    "order"
                )

                print(
                    "Order Created Successfully"
                )

                return order

            else:

                print(
                    "Create Order Failed"
                )

                print(
                    "Response:",
                    response.text
                )

                return None

        except requests.exceptions.RequestException as error:

            print(
                "Orders API Connection Error:"
            )

            print(error)

            return None

    # ============================================================
    # إنشاء Payment
    # ============================================================

    def create_payment(
        self,
        order_id,
        amount
    ):
        """
        إنشاء دفعة تجريبية في Square Sandbox.
        """

        if not self.access_token:

            print("Square Access Token: NOT SET")

            return None

        try:

            payload = {

                "source_id":
                    "cnon:card-nonce-ok",

                "idempotency_key":
                    str(uuid.uuid4()),

                "amount_money": {

                    "amount":
                        amount,

                    "currency":
                        "USD"
                },

                "order_id":
                    order_id,

                "autocomplete":
                    False
            }

            response = requests.post(

                f"{self.base_url}/payments",

                headers=self.headers,

                json=payload,

                timeout=10
            )

            print(
                "Create Payment HTTP Status:",
                response.status_code
            )

            if response.status_code == 200:

                data = response.json()

                payment = data.get(
                    "payment"
                )

                print(
                    "Payment Created Successfully"
                )

                return payment

            else:

                print(
                    "Create Payment Failed"
                )

                print(
                    "Response:",
                    response.text
                )

                return None

        except requests.exceptions.RequestException as error:

            print(
                "Payments API Connection Error:"
            )

            print(error)

            return None

    # ============================================================
    # إتمام Order ودفعه
    # ============================================================

    def pay_order(
        self,
        order_id,
        payment_id
    ):
        """
        إتمام الطلب باستخدام Payment.
        """

        if not self.access_token:

            print("Square Access Token: NOT SET")

            return None

        try:

            payload = {

                "idempotency_key":
                    str(uuid.uuid4()),

                "payment_ids": [
                    payment_id
                ]
            }

            response = requests.post(

                f"{self.base_url}/orders/{order_id}/pay",

                headers=self.headers,

                json=payload,

                timeout=10
            )

            print(
                "Pay Order HTTP Status:",
                response.status_code
            )

            if response.status_code == 200:

                data = response.json()

                order = data.get(
                    "order"
                )

                print(
                    "Order Paid Successfully"
                )

                return order

            else:

                print(
                    "Pay Order Failed"
                )

                print(
                    "Response:",
                    response.text
                )

                return None

        except requests.exceptions.RequestException as error:

            print(
                "Pay Order API Connection Error:"
            )

            print(error)

            return None

    # ============================================================
    # جلب تفاصيل Payment
    # ============================================================

    def get_payment(
        self,
        payment_id
    ):
        """
        جلب تفاصيل Payment من Square.
        """

        if not self.access_token:

            print("Square Access Token: NOT SET")

            return None

        try:

            endpoint = (
                f"{self.base_url}/payments/{payment_id}"
            )

            response = requests.get(

                endpoint,

                headers=self.headers,

                timeout=10
            )

            print(
                "Get Payment HTTP Status:",
                response.status_code
            )

            if response.status_code == 200:

                data = response.json()

                return data.get(
                    "payment"
                )

            else:

                print(
                    "Payment Error:"
                )

                print(
                    response.text
                )

                return None

        except requests.exceptions.RequestException as error:

            print(
                "Get Payment API Connection Error:"
            )

            print(error)

            return None

    # ============================================================
    # جلب تاريخ تغييرات المخزون
    # ============================================================

    def get_inventory_history(
        self,
        catalog_object_id,
        location_id
    ):
        """
        جلب تاريخ تغييرات مخزون منتج محدد.
        """

        if not self.access_token:

            print("Square Access Token: NOT SET")

            return None

        try:

            payload = {

                "catalog_object_ids": [
                    catalog_object_id
                ],

                "location_ids": [
                    location_id
                ],

                "types": [
                    "PHYSICAL_COUNT",
                    "ADJUSTMENT"
                ],

                "limit":
                    100,

                "sort": {

                    "field":
                        "OCCURRED_AT",

                    "order":
                        "ASC"
                }
            }

            response = requests.post(

                f"{self.base_url}/inventory/changes/batch-retrieve",

                headers=self.headers,

                json=payload,

                timeout=10
            )

            print(
                "Inventory History HTTP Status:",
                response.status_code
            )

            if response.status_code == 200:

                data = response.json()

                changes = data.get(
                    "changes",
                    []
                )

                print(
                    "Number of Inventory Changes:",
                    len(changes)
                )

                return changes

            else:

                print(
                    "Inventory History Request Failed"
                )

                print(
                    "Response:",
                    response.text
                )

                return None

        except requests.exceptions.RequestException as error:

            print(
                "Inventory History API Connection Error:"
            )

            print(error)

            return None

    # ============================================================
    # قراءة Catalog Object محدد
    # ============================================================

    def get_catalog_object(
        self,
        catalog_object_id
    ):
        """
        جلب بيانات Catalog Object من Square.
        """

        if not self.access_token:

            print("Square Access Token: NOT SET")

            return None

        try:

            response = requests.get(

                f"{self.base_url}/catalog/object/{catalog_object_id}",

                headers=self.headers,

                params={
                    "include_related_objects":
                        "true"
                },

                timeout=10
            )

            print(
                "Catalog Object HTTP Status:",
                response.status_code
            )

            if response.status_code == 200:

                data = response.json()

                catalog_object = data.get(
                    "object"
                )

                print(
                    "Catalog Object Retrieved Successfully"
                )

                return catalog_object

            else:

                print(
                    "Catalog Object Request Failed"
                )

                print(
                    "Response:",
                    response.text
                )

                return None

        except requests.exceptions.RequestException as error:

            print(
                "Catalog API Connection Error:"
            )

            print(error)

            return None

    # ============================================================
    # البحث عن حركات SOLD
    # ============================================================

    def get_sold_inventory_changes(
        self,
        catalog_object_id,
        location_id
    ):
        """
        البحث عن جميع حركات SOLD
        لمنتج وموقع محددين.
        """

        if not self.access_token:

            print("Square Access Token: NOT SET")

            return []

        try:

            url = (
                f"{self.base_url}/inventory/changes/batch-retrieve"
            )

            payload = {

                "catalog_object_ids": [
                    catalog_object_id
                ],

                "location_ids": [
                    location_id
                ],

                "states": [
                    "SOLD"
                ],

                "types": [
                    "ADJUSTMENT"
                ],

                "limit":
                    100
            }

            response = requests.post(

                url,

                headers=self.headers,

                json=payload,

                timeout=10
            )

            print(
                "SOLD Inventory History HTTP Status:",
                response.status_code
            )

            if response.status_code == 200:

                data = response.json()

                return data.get(
                    "changes",
                    []
                )

            else:

                print(
                    "SOLD Inventory Request Failed"
                )

                print(
                    "Response:",
                    response.text
                )

                return []

        except requests.exceptions.RequestException as error:

            print(
                "Inventory SOLD API Connection Error:"
            )

            print(error)

            return []
