# ============================================================
# SMARTSTOCK AI
# Sales Dataset
# ============================================================

import pandas as pd

from services.sales_service import SalesService


class SalesDataset:
    """
    تحويل بيانات المبيعات المنظمة إلى
    Pandas DataFrame لاستخدامها في التحليل و ML.
    """

    def __init__(self):

        # إنشاء Sales Service
        self.sales_service = SalesService()


    # ========================================================
    # جلب بيانات المبيعات كـ DataFrame
    # ========================================================

    def get_sales_dataframe(
        self,
        location_id,
        limit=100
    ):
        """
        جلب المبيعات من Square وتحويلها
        إلى Pandas DataFrame.
        """

        # جلب سجلات المبيعات
        sales = (
            self.sales_service.build_sales_records(
                location_id=location_id,
                limit=limit
            )
        )


        # إذا لم توجد بيانات
        if not sales:

            return pd.DataFrame()


        # تحويل السجلات إلى DataFrame
        dataframe = pd.DataFrame(
            sales
        )


        # ====================================================
        # تحويل التاريخ إلى Datetime
        # ====================================================

        if "sale_datetime" in dataframe.columns:

            dataframe["sale_datetime"] = (
                pd.to_datetime(
                    dataframe["sale_datetime"],
                    errors="coerce"
                )
            )


        # ====================================================
        # تحويل Quantity إلى رقم
        # ====================================================

        if "quantity" in dataframe.columns:

            dataframe["quantity"] = (
                pd.to_numeric(
                    dataframe["quantity"],
                    errors="coerce"
                )
            )


        # ====================================================
        # تحويل الأسعار إلى أرقام
        # ====================================================

        numeric_columns = [

            "unit_price",

            "total_price"

        ]


        for column in numeric_columns:

            if column in dataframe.columns:

                dataframe[column] = (
                    pd.to_numeric(
                        dataframe[column],
                        errors="coerce"
                    )
                )


        return dataframe