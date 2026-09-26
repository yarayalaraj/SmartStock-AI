import pandas as pd


class DemandTrainingDataset:

    DATA_URL = (
        "https://raw.githubusercontent.com/"
        "amankharwal/Website-data/master/demand.csv"
    )

    def __init__(self):
        self.data = None

    def load_data(self):
        try:
            dataframe = pd.read_csv(self.DATA_URL)

            print("=" * 60)
            print("DEMAND DATA LOADED")
            print("=" * 60)
            print("Rows:", len(dataframe))
            print("Columns:", list(dataframe.columns))

            self.data = dataframe

            return dataframe

        except Exception as error:
            raise ConnectionError(
                f"Could not load demand dataset: {error}"
            )

    def clean_data(self, dataframe):

        dataframe = dataframe.copy()

        required_columns = [
            "ID",
            "Store ID",
            "Total Price",
            "Base Price",
            "Units Sold"
        ]

        missing_columns = [
            column
            for column in required_columns
            if column not in dataframe.columns
        ]

        if missing_columns:
            raise ValueError(
                f"Missing required columns: {missing_columns}"
            )

        numeric_columns = [
            "ID",
            "Store ID",
            "Total Price",
            "Base Price",
            "Units Sold"
        ]

        for column in numeric_columns:

            dataframe[column] = pd.to_numeric(
                dataframe[column],
                errors="coerce"
            )

        # حذف الصفوف التي لا تحتوي على الهدف
        dataframe = dataframe.dropna(
            subset=["Units Sold"]
        )

        # تعويض القيم المفقودة في الأسعار بالوسيط
        dataframe["Total Price"] = dataframe["Total Price"].fillna(
            dataframe["Total Price"].median()
        )

        dataframe["Base Price"] = dataframe["Base Price"].fillna(
            dataframe["Base Price"].median()
        )

        # الاحتفاظ بالقيم المنطقية فقط
        dataframe = dataframe[
            (dataframe["Units Sold"] > 0) &
            (dataframe["Total Price"] > 0) &
            (dataframe["Base Price"] > 0)
        ]

        dataframe = dataframe.reset_index(drop=True)

        print("=" * 60)
        print("DATA CLEANING COMPLETED")
        print("=" * 60)
        print("Clean rows:", len(dataframe))
        print(
            "Remaining missing values:",
            dataframe.isnull().sum().sum()
        )

        return dataframe

    def prepare_training_data(self):

        dataframe = self.load_data()

        dataframe = self.clean_data(dataframe)

        # مقدار الخصم
        dataframe["discount_amount"] = (
            dataframe["Base Price"]
            - dataframe["Total Price"]
        )

        # نسبة الخصم
        dataframe["discount_percentage"] = (
            dataframe["discount_amount"]
            / dataframe["Base Price"]
        ) * 100

        # نسبة السعر إلى السعر الأساسي
        dataframe["price_ratio"] = (
            dataframe["Total Price"]
            / dataframe["Base Price"]
        )

        # معالجة القيم اللانهائية
        dataframe = dataframe.replace(
            [float("inf"), float("-inf")],
            pd.NA
        )

        dataframe = dataframe.dropna()

        dataframe = dataframe.reset_index(drop=True)

        return dataframe

    def get_features_and_target(self):

        dataframe = self.prepare_training_data()

        features = [
            "Store ID",
            "Total Price",
            "Base Price",
            "discount_amount",
            "discount_percentage",
            "price_ratio"
        ]

        target = "Units Sold"

        X = dataframe[features]

        y = dataframe[target]

        return X, y, dataframe