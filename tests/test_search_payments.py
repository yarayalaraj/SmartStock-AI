# ============================================================
# SMARTSTOCK AI
# اختبار البحث عن Payments من Square
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
# البحث عن Payments
# ============================================================

endpoint = (
    f"{square.base_url}/payments"
)

params = {
    "limit": 20
}


try:

    response = requests.get(
        endpoint,
        headers=square.headers,
        params=params,
        timeout=10
    )

    print("=" * 70)
    print("SMARTSTOCK AI - SEARCH PAYMENTS")
    print("=" * 70)

    print("\nHTTP Status:")
    print(response.status_code)

    print("\nResponse:")
    print(response.text)


    # ========================================================
    # تحليل النتيجة
    # ========================================================

    if response.status_code == 200:

        data = response.json()

        payments = data.get(
            "payments",
            []
        )

        print("\n" + "=" * 70)
        print("PAYMENTS SUMMARY")
        print("=" * 70)

        print("\nNumber of Payments:")
        print(len(payments))

        for index, payment in enumerate(
            payments,
            start=1
        ):

            print(f"\nPayment #{index}")

            print("Payment ID:")
            print(payment.get("id"))

            print("Status:")
            print(payment.get("status"))

            print("Order ID:")
            print(payment.get("order_id"))

            print("Amount Money:")
            print(payment.get("amount_money"))

            print("Created At:")
            print(payment.get("created_at"))

            print("Updated At:")
            print(payment.get("updated_at"))

    else:

        print("\nSearch Payments Failed.")


except requests.exceptions.RequestException as error:

    print("=" * 70)
    print("SMARTSTOCK AI - CONNECTION ERROR")
    print("=" * 70)

    print("\nError:")
    print(error)


print("\n" + "=" * 70)
print("TEST FINISHED")
print("=" * 70)