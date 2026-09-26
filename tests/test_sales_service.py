# ============================================================
# SMARTSTOCK AI
# اختبار Sales Service
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

from services.sales_service import SalesService


# ============================================================
# إنشاء Sales Service
# ============================================================

sales_service = SalesService()


# ============================================================
# Location ID
# ============================================================

location_id = "LCQJDMZ076NK1"


# ============================================================
# بناء Sales Records
# ============================================================

sales = sales_service.build_sales_records(
    location_id=location_id,
    limit=100
)


# ============================================================
# عرض النتيجة
# ============================================================

print("=" * 70)
print("SMARTSTOCK AI - SALES SERVICE")
print("=" * 70)

print("\nNumber of Sales Records:")
print(len(sales))


for index, sale in enumerate(
    sales,
    start=1
):

    print("\n" + "-" * 70)

    print(
        f"SALE #{index}"
    )

    print("-" * 70)

    for key, value in sale.items():

        print(
            f"{key}: {value}"
        )


print("\n" + "=" * 70)
print("TEST FINISHED")
print("=" * 70)