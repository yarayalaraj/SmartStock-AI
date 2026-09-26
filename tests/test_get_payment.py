# ============================================================
# SMARTSTOCK AI
# اختبار قراءة تفاصيل Payment من Square
# ============================================================

import sys
import os

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
# Payment ID الذي تم إنشاؤه سابقًا
# ============================================================

payment_id = "V2CQnDnvjPezS8Eyf4Ra1S5vzQLZY"


# ============================================================
# جلب Payment
# ============================================================

payment = square.get_payment(payment_id)


# ============================================================
# عرض النتائج
# ============================================================

if payment:

    print("=" * 70)
    print("SMARTSTOCK AI - PAYMENT DETAILS")
    print("=" * 70)

    print("\nPayment ID:")
    print(payment.get("id"))

    print("\nStatus:")
    print(payment.get("status"))

    print("\nOrder ID:")
    print(payment.get("order_id"))

    print("\nAmount Money:")
    print(payment.get("amount_money"))

    print("\nSource Type:")
    print(payment.get("source_type"))

    print("\nCreated At:")
    print(payment.get("created_at"))

    print("\nUpdated At:")
    print(payment.get("updated_at"))

else:

    print("\nFailed to retrieve payment.")


print("\n" + "=" * 70)
print("TEST FINISHED")
print("=" * 70)