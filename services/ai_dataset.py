# ============================================================
# SMARTSTOCK AI
# AI Dataset
# ============================================================

import pandas as pd

from services.sales_dataset import SalesDataset
from services.inventory_dataset import InventoryDataset


class AIDataset:
    """
    طبقة تجمع بيانات المبيعات والمخزون
    في DataFrame واحد لاستخدامها لاحقًا
    في نماذج الذكاء الاصطناعي.
    """

    def __init__(self):
        """
        إنشاء طبقات Sales و Inventory.
        """

        self.sales_dataset = SalesDataset()

        self.inventory_dataset = InventoryDataset()


    # ========================================================
    # جلب بيانات المبيعات والمخزون
    # ========================================================

    def get_combined_dataframe(
        self,
        location_id,
        sales_limit=100
    ):
        """
        جلب بيانات المبيعات والمخزون
        ودمجها في DataFrame واحد.
        """

        # ====================================================
        # جلب المبيعات
        # ====================================================

        sales_df = self.sales_dataset.get_sales_dataframe(
            location_id=location_id,
            limit=sales_limit
        )


        # ====================================================
        # جلب المخزون
        # ====================================================

        inventory_df = self.inventory_dataset.get_inventory_dataframe(
            location_id=location_id
        )


        # ====================================================
        # التحقق من وجود البيانات
        # ====================================================

        if sales_df.empty and inventory_df.empty:

            return pd.DataFrame()


        # ====================================================
        # في حال عدم وجود مبيعات
        # ====================================================

        if sales_df.empty:

            return inventory_df


        # ====================================================
        # في حال عدم وجود مخزون
        # ====================================================

        if inventory_df.empty:

            return sales_df


        # ====================================================
        # دمج المبيعات مع المخزون
        # ====================================================

        combined_df = sales_df.merge(
            inventory_df[
                [
                    "product_id",
                    "location_id",
                    "quantity",
                    "inventory_state",
                    "calculated_at"
                ]
            ],
            on=[
                "product_id",
                "location_id"
            ],
            how="left",
            suffixes=(
                "_sales",
                "_inventory"
            )
        )


        return combined_df