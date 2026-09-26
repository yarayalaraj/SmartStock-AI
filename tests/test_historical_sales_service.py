# ============================================================
# SMARTSTOCK AI
# اختبار Historical Sales Service
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


from services.historical_sales_service import HistoricalSalesService


# ============================================================
# إنشاء Historical Sales Service
# ============================================================

historical_service = HistoricalSalesService()


# ============================================================
# Location ID
# ============================================================

location_id = "LCQJDMZ076NK1"


# ============================================================
# جمع وحفظ المبيعات الحقيقية
# ============================================================

dataframe = historical_service.save_sales(
    location_id=location_id,
    limit=100
)


# ============================================================
# عرض النتائج
# ============================================================

print("\n" + "=" * 70)
print("SMARTSTOCK AI - HISTORICAL SALES TEST")
print("=" * 70)


print("\nDataFrame Shape:")
print(dataframe.shape)


print("\nColumns:")
print(dataframe.columns.tolist())


print("\nHistorical Sales:")

if dataframe.empty:

    print("No historical sales found.")

else:

    print(
        dataframe.to_string(
            index=False
        )
    )


print("\n" + "=" * 70)
print("TEST FINISHED")
print("=" * 70)