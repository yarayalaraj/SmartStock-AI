# ============================================================
# SMARTSTOCK AI
# اختبار بيئة Python
# ============================================================

# طباعة رسالة للتأكد أن Python يعمل
print("========================================")

print("SMARTSTOCK AI")

print("Python environment is working!")

print("========================================")


# ------------------------------------------------------------
# اختبار المكتبات الأساسية
# ------------------------------------------------------------

# استدعاء مكتبة pandas
# سنستخدمها لاحقاً لمعالجة بيانات المشروع
try:
    import pandas as pd

    print("Pandas: OK")

except ImportError:
    print("Pandas: NOT INSTALLED")


# ------------------------------------------------------------
# اختبار مكتبة requests
# ------------------------------------------------------------

# requests ستستخدم للاتصال بالـ APIs
try:
    import requests

    print("Requests: OK")

except ImportError:
    print("Requests: NOT INSTALLED")


# ------------------------------------------------------------
# إنشاء بيانات بسيطة للتجربة
# ------------------------------------------------------------

products = [
    {
        "name": "Coffee",
        "category": "Cafe",
        "stock": 50
    },
    {
        "name": "Milk",
        "category": "Raw Material",
        "stock": 20
    },
    {
        "name": "T-Shirt",
        "category": "Clothing",
        "stock": 35
    }
]


# طباعة المنتجات
print("\nProducts:")

for product in products:

    print(
        product["name"],
        "-",
        product["category"],
        "- Stock:",
        product["stock"]
    )


print("\nTest completed successfully!")