# ============================================================
# SMARTSTOCK AI
# اختبار تفاصيل Order المكتمل وربطه بالمنتج
# ============================================================

import sys
import os

# ============================================================
# إضافة مجلد المشروع الرئيسي إلى مسار Python
# ============================================================

PROJECT_ROOT = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

sys.path.insert(0, PROJECT_ROOT)


# ============================================================
# استيراد SquareClient بعد إضافة مسار المشروع
# ============================================================

from integrations.square.square_client import SquareClient


# ============================================================
# إنشاء عميل Square
# ============================================================

square = SquareClient()


# ============================================================
# رقم Order الذي أنشأناه واختبرناه سابقًا
# ============================================================

order_id = "pm1dMWlPowPWjTWBTQPT2kx227aZY"


# ============================================================
# جلب تفاصيل Order
# ============================================================

order = square.get_order(order_id)


# ============================================================
# عرض النتائج
# ============================================================

if order:

    print("=" * 70)
    print("SMARTSTOCK AI - COMPLETED ORDER DETAILS")
    print("=" * 70)

    print("\nOrder ID:")
    print(order.get("id"))

    print("\nLocation ID:")
    print(order.get("location_id"))

    print("\nState:")
    print(order.get("state"))

    print("\nCreated At:")
    print(order.get("created_at"))

    print("\nUpdated At:")
    print(order.get("updated_at"))

    print("\nSource:")
    print(order.get("source"))


    # ========================================================
    # تفاصيل المنتجات داخل Order
    # ========================================================

    line_items = order.get("line_items", [])

    print("\n" + "=" * 70)
    print("LINE ITEMS")
    print("=" * 70)

    print("\nNumber of Line Items:")
    print(len(line_items))

    for index, item in enumerate(line_items, start=1):

        print(f"\nLINE ITEM #{index}")
        print("-" * 70)

        print("Name:")
        print(item.get("name"))

        print("Quantity:")
        print(item.get("quantity"))

        print("Catalog Object ID:")
        print(item.get("catalog_object_id"))

        print("Catalog Version:")
        print(item.get("catalog_version"))

        print("Base Price Money:")
        print(item.get("base_price_money"))

        print("Total Money:")
        print(item.get("total_money"))

        print("Variation Name:")
        print(item.get("variation_name"))


    # ========================================================
    # المدفوعات
    # ========================================================

    tenders = order.get("tenders", [])

    print("\n" + "=" * 70)
    print("TENDERS")
    print("=" * 70)

    print("\nNumber of Tenders:")
    print(len(tenders))

    for index, tender in enumerate(tenders, start=1):

        print(f"\nTENDER #{index}")
        print("-" * 70)

        print("Tender ID:")
        print(tender.get("id"))

        print("Type:")
        print(tender.get("type"))

        print("Amount Money:")
        print(tender.get("amount_money"))

        print("Payment ID:")
        print(tender.get("payment_id"))

        # لا نطبع تفاصيل البطاقة حفاظًا على الخصوصية


    # ========================================================
    # Fulfillments
    # ========================================================

    fulfillments = order.get("fulfillments", [])

    print("\n" + "=" * 70)
    print("FULFILLMENTS")
    print("=" * 70)

    print("\nNumber of Fulfillments:")
    print(len(fulfillments))


else:

    print("\nFailed to retrieve order.")


print("\n" + "=" * 70)
print("TEST FINISHED")
print("=" * 70)