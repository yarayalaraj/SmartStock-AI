# ============================================================
# SMARTSTOCK AI
# Demand Dataset
# ============================================================

import pandas as pd

from services.sales_dataset import SalesDataset


class DemandDataset:
    """
    طبقة مسؤولة عن تجهيز بيانات المبيعات
    لتصبح مناسبة لتحليل الطلب والتنبؤ به لاحقًا.
    """

    def __init__(self):
        """
        إنشاء Sales Dataset.
        """

        self.sales_dataset = SalesDataset()


    # ========================================================
    # تجهيز بيانات الطلب اليومية
    # ========================================================

    def get_daily_demand_dataframe(
        self,
        location_id,
        sales_limit=100
    ):
        """
        جلب المبيعات الحقيقية من Square
        وتجميعها حسب اليوم والمنتج.
        """

        # ====================================================
        # جلب بيانات المبيعات
        # ====================================================

        sales_df = self.sales_dataset.get_sales_dataframe(
            location_id=location_id,
            limit=sales_limit
        )


        # ====================================================
        # في حال عدم وجود بيانات
        # ====================================================

        if sales_df.empty:

            return pd.DataFrame()


        # ====================================================
        # التأكد من وجود تاريخ البيع
        # ====================================================

        if "sale_datetime" not in sales_df.columns:

            return pd.DataFrame()


        # ====================================================
        # إنشاء عمود التاريخ فقط
        # ====================================================

        sales_df["date"] = (
            sales_df["sale_datetime"]
            .dt.date
        )


        # ====================================================
        # تجميع الطلب حسب:
        # التاريخ + المنتج
        # ====================================================

        daily_demand = (
            sales_df
            .groupby(
                [
                    "date",
                    "product_id",
                    "product_name"
                ],
                as_index=False
            )
            .agg(
                daily_quantity=(
                    "quantity",
                    "sum"
                ),
                daily_revenue=(
                    "total_price",
                    "sum"
                )
            )
        )


        # ====================================================
        # تحويل التاريخ إلى Datetime
        # ====================================================

        daily_demand["date"] = pd.to_datetime(
            daily_demand["date"],
            errors="coerce"
        )


        # ====================================================
        # تحويل الكميات إلى أرقام
        # ====================================================

        daily_demand["daily_quantity"] = pd.to_numeric(
            daily_demand["daily_quantity"],
            errors="coerce"
        )


        daily_demand["daily_revenue"] = pd.to_numeric(
            daily_demand["daily_revenue"],
            errors="coerce"
        )


        # ====================================================
        # ترتيب البيانات
        # ====================================================

        daily_demand = daily_demand.sort_values(
            [
                "product_id",
                "date"
            ]
        ).reset_index(
            drop=True
        )


        return daily_demand