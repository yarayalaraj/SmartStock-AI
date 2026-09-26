# ============================================================
# SMARTSTOCK AI
# اختبار AI Dataset
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


from services.ai_dataset import AIDataset


# ============================================================
# إنشاء AI Dataset
# ============================================================

ai_dataset = AIDataset()


# ============================================================
# Location ID
# ============================================================

location_id = "LCQJDMZ076NK1"


# ============================================================
# الحصول على البيانات المدمجة
# ============================================================

dataframe = ai_dataset.get_combined_dataframe(
    location_id=location_id,
    sales_limit=100
)


# ============================================================
# عرض النتائج
# ============================================================

print("=" * 70)
print("SMARTSTOCK AI - AI DATASET")
print("=" * 70)


print("\nDataFrame Shape:")
print(dataframe.shape)


print("\nColumns:")
print(dataframe.columns.tolist())


print("\nData Types:")
print(dataframe.dtypes)


print("\nCombined Data:")
print(dataframe.to_string(index=False))


print("\n" + "=" * 70)
print("TEST FINISHED")
print("=" * 70)