# ============================================================
# SMARTSTOCK AI
# اختبار Search Orders بدون Filters
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
# Location ID الخاص بحساب Square Sandbox
# ============================================================

location_id = "LCQJDMZ076NK1"


# ============================================================
# تنفيذ Search Orders بدون Filters
# ============================================================

endpoint = (
    f"{square.base_url}/orders/search"
)

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

                "closed_at": {

                    "start_at":
                        "2026-09-23T00:00:00Z"
                }
            }
        },

        "sort": {

            "sort_field":
                "CLOSED_AT",

            "sort_order":
                "DESC"
        }
    },

    "limit": 20,

    "return_entries": True
}


try:

    response = requests.post(
        endpoint,
        headers=square.headers,
        json=payload,
        timeout=10
    )

    print("=" * 70)
    print("SMARTSTOCK AI - SEARCH ALL ORDERS")
    print("=" * 70)

    print("\nHTTP Status:")
    print(response.status_code)

    print("\nResponse:")

    print(response.text)


    # ========================================================
    # تحليل النتيجة إذا كان الطلب ناجحًا
    # ========================================================

    if response.status_code == 200:

        data = response.json()

        orders = data.get(
            "orders",
            []
        )

        print("\n" + "=" * 70)
        print("ORDERS SUMMARY")
        print("=" * 70)

        print("\nNumber of Orders:")
        print(len(orders))

        for index, order in enumerate(
            orders,
            start=1
        ):

            print("\nOrder #", index)

            print("Order ID:")
            print(order.get("id"))

            print("State:")
            print(order.get("state"))

            print("Created At:")
            print(order.get("created_at"))

            print("Updated At:")
            print(order.get("updated_at"))

            print("Location ID:")
            print(order.get("location_id"))

    else:

        print("\nSearch Orders Failed.")


except requests.exceptions.RequestException as error:

    print("=" * 70)
    print("SMARTSTOCK AI - CONNECTION ERROR")
    print("=" * 70)

    print("\nError:")
    print(error)


print("\n" + "=" * 70)
print("TEST FINISHED")
print("=" * 70)