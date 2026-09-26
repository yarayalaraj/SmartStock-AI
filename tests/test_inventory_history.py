# ============================================================
# SMARTSTOCK AI
# فحص سجل تغييرات المخزون بالتفصيل
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
from integrations.square.square_client import SquareClient


# إنشاء عميل Square
square = SquareClient()


# بيانات المنتج والموقع
catalog_object_id = "CHI74NB3HRW3WABQQJ2RUX42"
location_id = "LCQJDMZ076NK1"


print("=" * 70)
print("SMARTSTOCK AI - DETAILED INVENTORY HISTORY")
print("=" * 70)


# جلب سجل المخزون
history = square.get_inventory_history(
    catalog_object_id,
    location_id
)


if history:

    changes = history

    print("\nNumber of Changes:", len(changes))

    print("\n" + "=" * 70)

    for index, change in enumerate(changes, start=1):

        print(f"\nCHANGE #{index}")
        print("-" * 70)

        print("Change Type:")
        print(change.get("type"))

        # ----------------------------------------------------
        # إذا كان التغيير من نوع ADJUSTMENT
        # ----------------------------------------------------
        if change.get("type") == "ADJUSTMENT":

            adjustment = change.get(
                "adjustment",
                {}
            )

            print("\nAdjustment ID:")
            print(adjustment.get("id"))

            print("\nReference ID:")
            print(adjustment.get("reference_id"))

            print("\nCatalog Object ID:")
            print(adjustment.get("catalog_object_id"))

            print("\nCatalog Object Type:")
            print(adjustment.get("catalog_object_type"))

            print("\nFrom State:")
            print(adjustment.get("from_state"))

            print("\nTo State:")
            print(adjustment.get("to_state"))

            print("\nFrom Location:")
            print(adjustment.get("from_location_id"))

            print("\nTo Location:")
            print(adjustment.get("to_location_id"))

            print("\nQuantity:")
            print(adjustment.get("quantity"))

            print("\nOccurred At:")
            print(adjustment.get("occurred_at"))

            print("\nCreated At:")
            print(adjustment.get("created_at"))

            print("\nTransaction ID:")
            print(adjustment.get("transaction_id"))

            print("\nRefund ID:")
            print(adjustment.get("refund_id"))

            print("\nPurchase Order ID:")
            print(adjustment.get("purchase_order_id"))

            print("\nGoods Receipt ID:")
            print(adjustment.get("goods_receipt_id"))

            print("\nPhysical Count ID:")
            print(adjustment.get("physical_count_id"))

            print("\nReason ID:")
            print(adjustment.get("reason_id"))

            # ------------------------------------------------
            # مصدر التغيير
            # ------------------------------------------------
            source = adjustment.get(
                "source",
                {}
            )

            print("\nSource:")
            print(source)

            print("\nSource Product:")
            print(source.get("product"))

            print("\nSource Application ID:")
            print(source.get("application_id"))

            print("\nSource Name:")
            print(source.get("name"))

        print("\n" + "=" * 70)

else:

    print("\nFailed to retrieve inventory history.")


print("\nTEST FINISHED")
print("=" * 70)