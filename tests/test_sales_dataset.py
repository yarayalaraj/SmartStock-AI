# ============================================================
# SMARTSTOCK AI
# اختبار Sales Dataset
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

from services.sales_dataset import SalesDataset


# ============================================================
# إنشاء Sales Dataset
# ============================================================

sales_dataset = SalesDataset()


# ============================================================
# Location ID
# ============================================================

location_id = "LCQJDMZ076NK1"


# ============================================================
# جلب بيانات المبيعات
# ============================================================

df = sales_dataset.get_sales_dataframe(
    location_id=location_id,
    limit=100
)


# ============================================================
# عرض النتائج
# ============================================================

print("=" * 70)
print("SMARTSTOCK AI - SALES DATASET")
print("=" * 70)


print("\nDataFrame Shape:")

print(
    df.shape
)


print("\nColumns:")

print(
    df.columns.tolist()
)


print("\nData Types:")

print(
    df.dtypes
)


print("\nSales Data:")

print(
    df.to_string(
        index=False
    )
)


print("\n" + "=" * 70)
print("TEST FINISHED")
print("=" * 70)