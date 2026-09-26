# ============================================================
# SMARTSTOCK AI
# فحص إعدادات Inventory و Sold Out
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


# Item Variation
variation_id = "CHI74NB3HRW3WABQQJ2RUX42"

# موقع Square
location_id = "LCQJDMZ076NK1"


print("=" * 70)
print("SMARTSTOCK AI - INVENTORY TRACKING STATUS")
print("=" * 70)


# جلب بيانات المنتج
catalog_object = square.get_catalog_object(
    variation_id
)


if catalog_object:

    item_variation = catalog_object.get(
        "item_variation_data",
        {}
    )

    print("\nCatalog Object Type:")
    print(catalog_object.get("type"))

    print("\nCatalog Object ID:")
    print(catalog_object.get("id"))

    print("\nItem Variation Name:")
    print(item_variation.get("name"))

    print("\nGlobal Track Inventory:")
    print(item_variation.get("track_inventory"))

    print("\nGlobal Sold Out:")
    print(item_variation.get("sold_out"))

    # ========================================================
    # إعداد الموقع
    # ========================================================

    location_overrides = item_variation.get(
        "location_overrides",
        []
    )

    print("\nNumber of Location Overrides:")
    print(len(location_overrides))

    found = False

    for override in location_overrides:

        if override.get("location_id") == location_id:

            found = True

            print("\n" + "=" * 70)
            print("TARGET LOCATION")
            print("=" * 70)

            print("\nLocation ID:")
            print(override.get("location_id"))

            print("\nTrack Inventory:")
            print(override.get("track_inventory"))

            print("\nSold Out:")
            print(override.get("sold_out"))

            print("\nFull Override:")
            print(override)

            break

    if not found:

        print("\nTarget location was not found.")


else:

    print("\nFailed to retrieve catalog object.")


print("\n" + "=" * 70)
print("TEST FINISHED")
print("=" * 70)