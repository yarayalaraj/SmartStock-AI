# ============================================================
# SMARTSTOCK AI
# البحث عن SOLD Inventory Adjustments
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


square = SquareClient()


catalog_object_id = "CHI74NB3HRW3WABQQJ2RUX42"
location_id = "LCQJDMZ076NK1"


print("=" * 70)
print("SMARTSTOCK AI - SOLD INVENTORY TEST")
print("=" * 70)


# البحث عن حركات البيع
changes = square.get_sold_inventory_changes(
    catalog_object_id,
    location_id
)


print("\nNumber of SOLD Changes:")
print(len(changes))


for index, change in enumerate(changes, start=1):

    print("\n" + "=" * 70)
    print(f"SOLD CHANGE #{index}")
    print("=" * 70)

    print("\nChange Type:")
    print(change.get("type"))

    adjustment = change.get(
        "adjustment",
        {}
    )

    print("\nAdjustment:")
    print(adjustment)


print("\n" + "=" * 70)
print("TEST FINISHED")
print("=" * 70)