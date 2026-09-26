# ============================================================
# SMARTSTOCK AI
# اختبار Demand Training Dataset
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


from services.demand_training_dataset import DemandTrainingDataset


# ============================================================
# إنشاء Dataset
# ============================================================

dataset = DemandTrainingDataset()


# ============================================================
# تجهيز البيانات
# ============================================================

dataframe = dataset.prepare_training_data()


# ============================================================
# التحقق من البيانات
# ============================================================

is_ready, message = dataset.validate_training_data(
    dataframe
)


# ============================================================
# عرض النتائج
# ============================================================

print("=" * 70)
print("SMARTSTOCK AI - DEMAND TRAINING DATASET")
print("=" * 70)

print("\nDataFrame Shape:")
print(dataframe.shape)

print("\nColumns:")
print(dataframe.columns.tolist())

print("\nTraining Data:")

if dataframe.empty:

    print("No training data found.")

else:

    print(
        dataframe.to_string(
            index=False
        )
    )


print("\nTraining Validation:")
print(message)

print("\nTraining Ready:")
print(is_ready)

print("\n" + "=" * 70)
print("TEST FINISHED")
print("=" * 70)