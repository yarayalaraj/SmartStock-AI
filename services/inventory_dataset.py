# ============================================================
# SMARTSTOCK AI
# Inventory Dataset
# ============================================================

import pandas as pd

from services.inventory_service import InventoryService


class InventoryDataset:
    """
    طبقة مسؤولة عن تحويل بيانات المخزون
    القادمة من InventoryService إلى Pandas DataFrame.
    """

    def __init__(self):
        """
        إنشاء Inventory Service.
        """

        self.inventory_service = InventoryService()


    # ========================================================
    # جلب بيانات المخزون كـ DataFrame
    # ========================================================

    def get_inventory_dataframe(
        self,
        location_id
    ):
        """
        جلب بيانات المخزون وتحويلها إلى DataFrame.
        """

        inventory = self.inventory_service.build_inventory_records(
            location_id=location_id
        )


        # ====================================================
        # في حال عدم وجود بيانات
        # ====================================================

        if not inventory:

            return pd.DataFrame()


        # ====================================================
        # تحويل البيانات إلى DataFrame
        # ====================================================

        dataframe = pd.DataFrame(
            inventory
        )


        # ====================================================
        # تحويل Quantity إلى رقم
        # ====================================================

        if "quantity" in dataframe.columns:

            dataframe["quantity"] = pd.to_numeric(
                dataframe["quantity"],
                errors="coerce"
            )


        # ====================================================
        # تحويل التاريخ والوقت
        # ====================================================

        if "calculated_at" in dataframe.columns:

            dataframe["calculated_at"] = pd.to_datetime(
                dataframe["calculated_at"],
                errors="coerce"
            )


        return dataframe