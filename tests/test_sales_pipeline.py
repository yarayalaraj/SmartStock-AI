# ============================================================
# SMARTSTOCK AI
# اختبار Sales Data Pipeline من Square
# ============================================================

import sys
import os
import requests

# إضافة مجلد المشروع الرئيسي إلى مسار Python
PROJECT_ROOT = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

sys.path.insert(0, PROJECT_ROOT)

from integrations.square.square_client import SquareClient


# ============================================================
# إنشاء عميل Square
# ============================================================

square = SquareClient()


# ============================================================
# Location ID
# ============================================================

location_id = "LCQJDMZ076NK1"


# ============================================================
# جلب Payments
# ============================================================

payments_endpoint = (
    f"{square.base_url}/payments"
)

payments_params = {
    "location_id": location_id,
    "limit": 20
}


try:

    payments_response = requests.get(
        payments_endpoint,
        headers=square.headers,
        params=payments_params,
        timeout=10
    )

    print("=" * 70)
    print("SMARTSTOCK AI - SALES DATA PIPELINE")
    print("=" * 70)

    print("\nPayments HTTP Status:")
    print(payments_response.status_code)


    if payments_response.status_code != 200:

        print("\nFailed to retrieve Payments.")

        print(
            payments_response.text
        )

        sys.exit()


    payments_data = (
        payments_response.json()
    )

    payments = payments_data.get(
        "payments",
        []
    )


    print("\nNumber of Payments:")
    print(len(payments))


    # ========================================================
    # معالجة كل Payment
    # ========================================================

    for payment_index, payment in enumerate(
        payments,
        start=1
    ):

        print("\n" + "-" * 70)
        print(
            f"PAYMENT #{payment_index}"
        )
        print("-" * 70)

        payment_id = payment.get(
            "id"
        )

        order_id = payment.get(
            "order_id"
        )

        payment_status = payment.get(
            "status"
        )

        created_at = payment.get(
            "created_at"
        )

        amount_money = payment.get(
            "amount_money",
            {}
        )


        print("\nPayment ID:")
        print(payment_id)

        print("\nPayment Status:")
        print(payment_status)

        print("\nOrder ID:")
        print(order_id)

        print("\nPayment Created At:")
        print(created_at)

        print("\nPayment Amount:")
        print(amount_money)


        # ====================================================
        # جلب Order المرتبط بالـ Payment
        # ====================================================

        if not order_id:

            print(
                "\nNo Order ID associated with Payment."
            )

            continue


        order_endpoint = (
            f"{square.base_url}"
            f"/orders/{order_id}"
        )


        order_response = requests.get(
            order_endpoint,
            headers=square.headers,
            timeout=10
        )


        print(
            "\nOrder HTTP Status:"
        )

        print(
            order_response.status_code
        )


        if order_response.status_code != 200:

            print(
                "\nFailed to retrieve Order."
            )

            print(
                order_response.text
            )

            continue


        order_data = (
            order_response.json()
        )

        order = order_data.get(
            "order",
            {}
        )


        # ====================================================
        # معلومات Order
        # ====================================================

        print("\nOrder State:")
        print(
            order.get("state")
        )

        print("\nOrder Created At:")
        print(
            order.get("created_at")
        )

        print("\nOrder Updated At:")
        print(
            order.get("updated_at")
        )


        # ====================================================
        # استخراج المنتجات المباعة
        # ====================================================

        line_items = order.get(
            "line_items",
            []
        )


        print("\nNumber of Line Items:")
        print(
            len(line_items)
        )


        for item_index, item in enumerate(
            line_items,
            start=1
        ):

            print(
                f"\nProduct #{item_index}"
            )

            print(
                "Product Name:"
            )

            print(
                item.get("name")
            )

            print(
                "Quantity:"
            )

            print(
                item.get("quantity")
            )

            print(
                "Catalog Object ID:"
            )

            print(
                item.get(
                    "catalog_object_id"
                )
            )

            print(
                "Total Money:"
            )

            print(
                item.get(
                    "total_money"
                )
            )


except requests.exceptions.RequestException as error:

    print(
        "\nSquare API Connection Error:"
    )

    print(error)


print("\n" + "=" * 70)
print("SALES PIPELINE TEST FINISHED")
print("=" * 70)