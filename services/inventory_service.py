# ============================================================
# SMARTSTOCK AI
# Inventory Service
# ============================================================

from integrations.square.square_client import SquareClient


class InventoryService:
    """
    خدمة مسؤولة عن جلب بيانات المخزون
    من Square API.
    """

    def __init__(self):
        """
        إنشاء Square Client.
        """

        self.square = SquareClient()


    # ========================================================
    # جلب المنتجات من Catalog
    # ========================================================

    def get_catalog_items(self):
        """
        جلب المنتجات والـ Variations من Square.
        """

        items = self.square.get_catalog_items()

        if not items:
            return []

        return items


    # ========================================================
    # جلب المخزون لمنتج محدد
    # ========================================================

    def get_inventory(
        self,
        catalog_object_id,
        location_id
    ):
        """
        جلب كمية المخزون الحالية لمنتج محدد.
        """
        print("DEBUG catalog_object_id:", catalog_object_id)
        print("DEBUG location_id:", location_id)
        inventory = self.square.get_inventory_count(
            catalog_object_id=catalog_object_id,
            location_id=location_id
        )

        if not inventory:
            return []

        return inventory


    # ========================================================
    # بناء سجلات Inventory منظمة
    # ========================================================

    def build_inventory_records(
        self,
        location_id
    ):
        """
        تحويل بيانات Catalog + Inventory
        إلى سجلات منظمة.
        """

        catalog_items = self.get_catalog_items()

        inventory_records = []


        # ====================================================
        # المرور على المنتجات
        # ====================================================

        for item in catalog_items:

            object_type = item.get(
                "type"
            )

            # نريد فقط Item Variations
            if object_type != "ITEM_VARIATION":
                continue


            catalog_object_id = item.get(
                "id"
            )


            variation_data = item.get(
                "item_variation_data",
                {}
            )


            variation_name = variation_data.get(
                "name"
            )


            item_name = None


            # =================================================
            # الحصول على اسم المنتج الأساسي
            # =================================================

            parent_id = variation_data.get(
                "item_id"
            )


            if parent_id:

                parent_item = self.square.get_catalog_object(
                    parent_id
                )


                if parent_item:

                    item_data = parent_item.get(
                        "item_data",
                        {}
                    )


                    item_name = item_data.get(
                        "name"
                    )


            # =================================================
            # جلب المخزون
            # =================================================

            inventory_counts = self.get_inventory(
                catalog_object_id=catalog_object_id,
                location_id=location_id
            )


            # =================================================
            # إنشاء سجل لكل Inventory Count
            # =================================================

            if inventory_counts:

                for count in inventory_counts:

                    quantity = count.get(
                        "quantity"
                    )


                    state = count.get(
                        "state"
                    )


                    calculated_at = count.get(
                        "calculated_at"
                    )


                    record = {

                        "product_id":
                            catalog_object_id,

                        "product_name":
                            item_name,

                        "variation_name":
                            variation_name,

                        "location_id":
                            location_id,

                        "quantity":
                            quantity,

                        "inventory_state":
                            state,

                        "calculated_at":
                            calculated_at
                    }


                    inventory_records.append(
                        record
                    )


            else:

                # في حال لم يكن هناك Inventory Count
                record = {

                    "product_id":
                        catalog_object_id,

                    "product_name":
                        item_name,

                    "variation_name":
                        variation_name,

                    "location_id":
                        location_id,

                    "quantity":
                        0,

                    "inventory_state":
                        None,

                    "calculated_at":
                        None
                }


                inventory_records.append(
                    record
                )


        return inventory_records