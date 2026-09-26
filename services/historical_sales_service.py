# ============================================================
# SMARTSTOCK AI
# Historical Sales Service
# ============================================================

import os

import pandas as pd

from services.sales_service import SalesService


class HistoricalSalesService:
    """
    خدمة مسؤولة عن جمع المبيعات الحقيقية من Square
    وتخزينها تاريخيًا لاستخدامها لاحقًا في التحليل و ML.
    """

    def __init__(self):
        """
        إنشاء Sales Service وتحديد مكان تخزين البيانات.
        """

        self.sales_service = SalesService()

        # ====================================================
        # تحديد مسار المشروع
        # ====================================================

        project_root = os.path.dirname(
            os.path.dirname(
                os.path.abspath(__file__)
            )
        )

        # ====================================================
        # إنشاء مجلد البيانات المحلية
        # ====================================================

        self.data_directory = os.path.join(
            project_root,
            "data",
            "historical"
        )

        os.makedirs(
            self.data_directory,
            exist_ok=True
        )


    # ========================================================
    # تحديد مسار ملف المبيعات التاريخية
    # ========================================================

    def get_sales_file_path(self):

        return os.path.join(
            self.data_directory,
            "historical_sales.csv"
        )


    # ========================================================
    # جلب المبيعات الحقيقية من Square
    # ========================================================

    def collect_sales(
        self,
        location_id,
        limit=100
    ):
        """
        جلب المبيعات الحقيقية من Square.
        """

        sales = self.sales_service.build_sales_records(
            location_id=location_id,
            limit=limit
        )

        return sales


    # ========================================================
    # حفظ المبيعات التاريخية
    # ========================================================

    def save_sales(
        self,
        location_id,
        limit=100
    ):
        """
        جلب المبيعات من Square وحفظها محليًا.

        يتم منع تكرار sale_id.
        """

        # ====================================================
        # جلب البيانات الحقيقية
        # ====================================================

        sales = self.collect_sales(
            location_id=location_id,
            limit=limit
        )


        # ====================================================
        # في حال عدم وجود مبيعات
        # ====================================================

        if not sales:

            print("No sales data returned from Square.")

            return pd.DataFrame()


        # ====================================================
        # تحويل البيانات إلى DataFrame
        # ====================================================

        new_sales_df = pd.DataFrame(
            sales
        )


        # ====================================================
        # تحديد مسار الملف
        # ====================================================

        file_path = self.get_sales_file_path()


        # ====================================================
        # قراءة البيانات الموجودة مسبقًا
        # ====================================================

        if os.path.exists(file_path):

            existing_df = pd.read_csv(
                file_path
            )

        else:

            existing_df = pd.DataFrame()


        # ====================================================
        # دمج البيانات القديمة والجديدة
        # ====================================================

        if existing_df.empty:

            combined_df = new_sales_df.copy()

        else:

            combined_df = pd.concat(
                [
                    existing_df,
                    new_sales_df
                ],
                ignore_index=True
            )


        # ====================================================
        # إزالة عمليات البيع المكررة
        # ====================================================

        if "sale_id" in combined_df.columns:

            combined_df = combined_df.drop_duplicates(
                subset=["sale_id"],
                keep="last"
            )


        # ====================================================
        # ترتيب المبيعات حسب التاريخ
        # ====================================================

        if "sale_datetime" in combined_df.columns:

            combined_df["sale_datetime"] = pd.to_datetime(
                combined_df["sale_datetime"],
                errors="coerce"
            )

            combined_df = combined_df.sort_values(
                "sale_datetime"
            )


        # ====================================================
        # حفظ البيانات
        # ====================================================

        combined_df.to_csv(
            file_path,
            index=False
        )


        print("=" * 70)
        print("HISTORICAL SALES STORAGE")
        print("=" * 70)

        print("\nSales received from Square:")
        print(len(new_sales_df))

        print("\nTotal unique sales stored:")
        print(len(combined_df))

        print("\nFile:")
        print(file_path)

        print("=" * 70)


        return combined_df