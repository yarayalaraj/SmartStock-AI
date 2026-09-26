# ============================================================
# SMARTSTOCK AI
# اختبار جلب المنتجات من Square
# ============================================================

from integrations.square.square_client import SquareClient


print("=" * 60)
print("SMARTSTOCK AI - SQUARE CATALOG TEST")
print("=" * 60)

# إنشاء Square Client
square = SquareClient()

# جلب المنتجات
items = square.get_catalog_items()

print("=" * 60)

if items is not None:

    print("CATALOG API TEST: SUCCESS")
    print("عدد العناصر:", len(items))

    # عرض أول 5 عناصر فقط
    for item in items[:5]:

        print("-" * 40)
        print("Type:", item.get("type"))
        print("ID:", item.get("id"))

        # إذا كان العنصر منتجًا
        if item.get("type") == "ITEM":

            item_data = item.get("item_data", {})

            print("Name:", item_data.get("name"))

else:

    print("CATALOG API TEST: FAILED")

print("=" * 60)