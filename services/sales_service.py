# ============================================================
# SMARTSTOCK AI
# Sales Service
# ============================================================

import requests

from integrations.square.square_client import SquareClient


class SalesService:
    """
    خدمة مسؤولة عن جلب وتنظيم بيانات المبيعات
    من Square API.
    """

    def __init__(self):
        """
        إنشاء Square Client.
        """

        self.square = SquareClient()


    # ========================================================
    # جلب Payments من Square
    # ========================================================

    def get_payments(
        self,
        location_id,
        limit=100
    ):
        """
        جلب عمليات الدفع من Square.
        """

        if not self.square.access_token:

            print(
                "Square Access Token: NOT SET"
            )

            return []


        endpoint = (
            f"{self.square.base_url}/payments"
        )


        params = {

            "location_id":
                location_id,

            "limit":
                limit
        }


        try:

            response = requests.get(

                endpoint,

                headers=self.square.headers,

                params=params,

                timeout=10
            )


            print(
                "Payments API HTTP Status:",
                response.status_code
            )


            if response.status_code == 200:

                data = response.json()

                return data.get(
                    "payments",
                    []
                )


            print(
                "Payments API Request Failed:"
            )

            print(
                response.text
            )

            return []


        except requests.exceptions.RequestException as error:

            print(
                "Payments API Connection Error:"
            )

            print(error)

            return []


    # ========================================================
    # جلب Order بواسطة ID
    # ========================================================

    def get_order(
        self,
        order_id
    ):
        """
        جلب Order من Square بواسطة Order ID.
        """

        if not order_id:

            return None


        endpoint = (
            f"{self.square.base_url}"
            f"/orders/{order_id}"
        )


        try:

            response = requests.get(

                endpoint,

                headers=self.square.headers,

                timeout=10
            )


            print(
                "Order API HTTP Status:",
                response.status_code
            )


            if response.status_code == 200:

                data = response.json()

                return data.get(
                    "order"
                )


            print(
                "Order API Request Failed:"
            )

            print(
                response.text
            )

            return None


        except requests.exceptions.RequestException as error:

            print(
                "Order API Connection Error:"
            )

            print(error)

            return None


    # ========================================================
    # تحويل Payment + Order إلى Sales Records
    # ========================================================

    def build_sales_records(
        self,
        location_id,
        limit=100
    ):
        """
        تحويل بيانات Square الخام إلى
        سجلات مبيعات منظمة ومناسبة للـ ML.
        """

        payments = self.get_payments(
            location_id=location_id,
            limit=limit
        )


        sales_records = []


        for payment in payments:

            # ------------------------------------------------
            # معلومات Payment
            # ------------------------------------------------

            payment_id = payment.get(
                "id"
            )

            order_id = payment.get(
                "order_id"
            )

            payment_status = payment.get(
                "status"
            )

            payment_created_at = payment.get(
                "created_at"
            )


            amount_money = payment.get(
                "amount_money",
                {}
            )


            payment_amount = (
                amount_money.get(
                    "amount"
                )
            )


            currency = (
                amount_money.get(
                    "currency"
                )
            )


            # ------------------------------------------------
            # نحتاج Order مرتبط بالـ Payment
            # ------------------------------------------------

            if not order_id:

                continue


            order = self.get_order(
                order_id
            )


            if not order:

                continue


            # ------------------------------------------------
            # معلومات Order
            # ------------------------------------------------

            order_location_id = (
                order.get(
                    "location_id"
                )
            )


            order_status = (
                order.get(
                    "state"
                )
            )


            order_created_at = (
                order.get(
                    "created_at"
                )
            )


            # ------------------------------------------------
            # المنتجات الموجودة داخل Order
            # ------------------------------------------------

            line_items = order.get(
                "line_items",
                []
            )


            for item in line_items:

                product_id = (
                    item.get(
                        "catalog_object_id"
                    )
                )


                product_name = (
                    item.get(
                        "name"
                    )
                )


                quantity = (
                    item.get(
                        "quantity"
                    )
                )


                item_total_money = (
                    item.get(
                        "total_money",
                        {}
                    )
                )


                item_total = (
                    item_total_money.get(
                        "amount"
                    )
                )


                # ------------------------------------------------
                # حساب السعر للوحدة
                # ------------------------------------------------

                unit_price = None


                try:

                    if (
                        quantity is not None
                        and item_total is not None
                        and float(quantity) != 0
                    ):

                        unit_price = (
                            float(item_total)
                            / float(quantity)
                        )

                except (
                    TypeError,
                    ValueError,
                    ZeroDivisionError
                ):

                    unit_price = None


                # ------------------------------------------------
                # إنشاء سجل مبيعات منظم
                # ------------------------------------------------

                sale_record = {

                    "sale_id":
                        f"{payment_id}_{product_id}",

                    "payment_id":
                        payment_id,

                    "order_id":
                        order_id,

                    "location_id":
                        order_location_id
                        or location_id,

                    "product_id":
                        product_id,

                    "product_name":
                        product_name,

                    "quantity":
                        quantity,

                    "unit_price":
                        unit_price,

                    "total_price":
                        item_total,

                    "currency":
                        currency,

                    "sale_datetime":
                        order_created_at
                        or payment_created_at,

                    "order_status":
                        order_status,

                    "payment_status":
                        payment_status
                }


                sales_records.append(
                    sale_record
                )


        return sales_records