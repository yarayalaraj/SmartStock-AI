# ============================================================
# SMARTSTOCK AI
# اختبار Demand Dataset
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


from services.demand_dataset import DemandDataset


# ============================================================
# إنشاء Demand Dataset
# ============================================================

demand_dataset = DemandDataset()


# ============================================================
# Location ID
# ============================================================

location_id = "LCQJDMZ076NK1"


# ============================================================
# الحصول على بيانات الطلب اليومية
# ============================================================

dataframe = demand_dataset.get_daily_demand_dataframe(
    location_id=location_id,
    sales_limit=100
)


# ============================================================
# عرض النتائج
# ============================================================

print("=" * 70)
print("SMARTSTOCK AI - DEMAND DATASET")
print("=" * 70)


print("\nDataFrame Shape:")
print(dataframe.shape)


print("\nColumns:")
print(dataframe.columns.tolist())


print("\nData Types:")
print(dataframe.dtypes)


print("\nDaily Demand Data:")

if dataframe.empty:

    print("No demand data found.")

else:

    print(
        dataframe.to_string(
            index=False
        )
    )


print("\n" + "=" * 70)
print("TEST FINISHED")
print("=" * 70)