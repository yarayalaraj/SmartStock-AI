# ============================================================
# SMARTSTOCK AI
# اختبار إنشاء Payment في Square Sandbox
# ============================================================

from integrations.square.square_client import SquareClient


print("=" * 60)
print("SMARTSTOCK AI - CREATE PAYMENT TEST")
print("=" * 60)


# إنشاء عميل Square
square = SquareClient()


# Order ID الموجود لدينا
order_id = "pm1dMWlPowPWjTWBTQPT2kx227aZY"


# إجمالي الطلب = 350 cents = 3.50 USD
amount = 350


# إنشاء Payment
payment = square.create_payment(
    order_id,
    amount
)


print("=" * 60)


if payment:

    print("CREATE PAYMENT TEST: SUCCESS")

    print("-" * 40)

    print("Payment ID:", payment.get("id"))

    print("Order ID:", payment.get("order_id"))

    print("Status:", payment.get("status"))

    print("Amount:", payment.get("amount_money"))

else:

    print("CREATE PAYMENT TEST: FAILED")


print("=" * 60)