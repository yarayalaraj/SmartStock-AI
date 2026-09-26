# ============================================================
# SMARTSTOCK AI
# اختبار Inventory Service
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

from services.inventory_service import InventoryService


# ============================================================
# إنشاء Inventory Service
# ============================================================

inventory_service = InventoryService()


# ============================================================
# Location ID
# ============================================================

location_id = "LCQJDMZ076NK1"


# ============================================================
# بناء Inventory Records
# ============================================================

inventory = inventory_service.build_inventory_records(
    location_id=location_id
)


# ============================================================
# عرض النتائج
# ============================================================

print("=" * 70)
print("SMARTSTOCK AI - INVENTORY SERVICE")
print("=" * 70)

print("\nNumber of Inventory Records:")
print(len(inventory))


for index, record in enumerate(
    inventory,
    start=1
):

    print("\n" + "-" * 70)

    print(
        f"INVENTORY #{index}"
    )

    print("-" * 70)

    for key, value in record.items():

        print(
            f"{key}: {value}"
        )


print("\n" + "=" * 70)
print("TEST FINISHED")
print("=" * 70)
