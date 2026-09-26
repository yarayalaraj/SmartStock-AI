# ============================================================
# SMARTSTOCK AI
# اختبار Inventory Dataset
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


from services.inventory_dataset import InventoryDataset


# ============================================================
# إنشاء Inventory Dataset
# ============================================================

inventory_dataset = InventoryDataset()


# ============================================================
# Location ID
# ============================================================

location_id = "LCQJDMZ076NK1"


# ============================================================
# الحصول على DataFrame
# ============================================================

dataframe = inventory_dataset.get_inventory_dataframe(
    location_id=location_id
)


# ============================================================
# عرض النتائج
# ============================================================

print("=" * 70)
print("SMARTSTOCK AI - INVENTORY DATASET")
print("=" * 70)

print("\nDataFrame Shape:")
print(dataframe.shape)


print("\nColumns:")
print(dataframe.columns.tolist())


print("\nData Types:")
print(dataframe.dtypes)


print("\nInventory Data:")
print(dataframe.to_string(index=False))


print("\n" + "=" * 70)
print("TEST FINISHED")
print("=" * 70)
