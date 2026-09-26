# ============================================================
# SMARTSTOCK AI
# اختبار نموذج التنبؤ بالطلب
# ============================================================
# ============================================================
# SMARTSTOCK AI
# اختبار نموذج التنبؤ بالطلب
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

from services.demand_model import DemandModel


print("=" * 60)
print("SMARTSTOCK AI - DEMAND MODEL TEST")
print("=" * 60)

model = DemandModel()

try:
    metrics = model.train()

    print("\nModel Training Completed.")

    print("\nEvaluation Metrics:")

    for metric_name, metric_value in metrics.items():
        print(f"{metric_name}: {metric_value}")

except ValueError as error:

    print("\nModel Training Not Started.")
    print(f"Reason: {error}")

except Exception as error:

    print("\nUnexpected Error:")
    print(error)

from services.demand_model import DemandModel


print("=" * 60)
print("SMARTSTOCK AI - DEMAND MODEL TEST")
print("=" * 60)

model = DemandModel()

try:

    metrics = model.train()

    print("\nModel Training Completed.")
    print("\nEvaluation Metrics:")

    for metric_name, metric_value in metrics.items():
        print(
            f"{metric_name}: {metric_value}"
        )

except ValueError as error:

    print("\nModel Training Not Started.")
    print(f"Reason: {error}")

except Exception as error:

    print("\nUnexpected Error:")
    print(error)