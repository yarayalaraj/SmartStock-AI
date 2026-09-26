# ============================================================
# SMARTSTOCK AI
# Demand Forecasting Model
# ============================================================

import os
import joblib
import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline

from sklearn.linear_model import LinearRegression

from sklearn.ensemble import (
    RandomForestRegressor,
    GradientBoostingRegressor
)

from sklearn.metrics import (
    mean_absolute_error,
    mean_squared_error,
    r2_score
)

from services.demand_training_dataset import DemandTrainingDataset


class DemandModel:

    def __init__(self, load_for_training=False):

        # ====================================================
        # Paths
        # ====================================================

        project_root = os.path.dirname(
            os.path.dirname(
                os.path.abspath(__file__)
            )
        )

        self.model_directory = os.path.join(
            project_root,
            "models"
        )

        os.makedirs(
            self.model_directory,
            exist_ok=True
        )

        self.model_path = os.path.join(
            self.model_directory,
            "demand_model.pkl"
        )

        self.results_path = os.path.join(
            self.model_directory,
            "demand_model_results.csv"
        )

        # ====================================================
        # Features
        # ====================================================

        self.features = [
            "Store ID",
            "Total Price",
            "Base Price",
            "discount_amount",
            "discount_percentage",
            "price_ratio"
        ]

        self.target = "Units Sold"

        # ====================================================
        # Runtime variables
        # ====================================================

        self.results = {}

        self.best_model_name = None

        self.best_model = None

        # ====================================================
        # Training mode
        # ====================================================

        # لا ننشئ نماذج التدريب عند تشغيل API.
        # يتم إنشاؤها فقط إذا طلبنا التدريب صراحةً.
        self.models = {}

        if load_for_training:

            self._initialize_training_models()

            self.dataset = DemandTrainingDataset()

    # ========================================================
    # Initialize Training Models
    # ========================================================

    def _initialize_training_models(self):

        self.models = {

            "Linear Regression": Pipeline([
                (
                    "scaler",
                    StandardScaler()
                ),
                (
                    "model",
                    LinearRegression()
                )
            ]),

            "Random Forest": RandomForestRegressor(
                n_estimators=100,
                random_state=42,
                n_jobs=-1
            ),

            "Gradient Boosting": GradientBoostingRegressor(
                n_estimators=100,
                learning_rate=0.05,
                max_depth=3,
                random_state=42
            )
        }

    # ========================================================
    # Prepare Data
    # ========================================================

    def prepare_data(self):

        if not hasattr(self, "dataset"):

            self.dataset = DemandTrainingDataset()

        X, y, dataframe = (
            self.dataset.get_features_and_target()
        )

        X = X[self.features]

        y = y.astype(float)

        return X, y, dataframe

    # ========================================================
    # Train Models
    # ========================================================

    def train(self):

        # إذا لم تكن نماذج التدريب موجودة،
        # نقوم بإنشائها فقط عند طلب التدريب.
        if not self.models:

            self._initialize_training_models()

        X, y, dataframe = (
            self.prepare_data()
        )

        print()
        print("=" * 70)
        print("SMARTSTOCK AI - DEMAND FORECASTING")
        print("=" * 70)

        print(
            "Training records:",
            len(X)
        )

        print(
            "Number of features:",
            len(self.features)
        )

        print(
            "Features:",
            self.features
        )

        # ====================================================
        # Train / Test Split
        # ====================================================

        X_train, X_test, y_train, y_test = (
            train_test_split(
                X,
                y,
                test_size=0.20,
                random_state=42
            )
        )

        print()
        print(
            "Training records:",
            len(X_train)
        )

        print(
            "Testing records:",
            len(X_test)
        )

        # ====================================================
        # Model Comparison
        # ====================================================

        print()
        print("=" * 70)
        print("MODEL COMPARISON")
        print("=" * 70)

        self.results = {}

        for model_name, model in self.models.items():

            print()
            print("-" * 70)

            print(
                "Training:",
                model_name
            )

            # Train
            model.fit(
                X_train,
                y_train
            )

            # Predict
            predictions = model.predict(
                X_test
            )

            # Metrics
            mae = mean_absolute_error(
                y_test,
                predictions
            )

            mse = mean_squared_error(
                y_test,
                predictions
            )

            rmse = mse ** 0.5

            r2 = r2_score(
                y_test,
                predictions
            )

            self.results[model_name] = {

                "MAE": mae,

                "MSE": mse,

                "RMSE": rmse,

                "R2": r2
            }

            print(
                "MAE :",
                round(mae, 4)
            )

            print(
                "MSE :",
                round(mse, 4)
            )

            print(
                "RMSE:",
                round(rmse, 4)
            )

            print(
                "R2  :",
                round(r2, 4)
            )

        # ====================================================
        # Select Best Model
        # ====================================================

        self.best_model_name = min(
            self.results,
            key=lambda name:
            self.results[name]["RMSE"]
        )

        self.best_model = self.models[
            self.best_model_name
        ]

        print()
        print("=" * 70)
        print("BEST MODEL")
        print("=" * 70)

        print(
            "Selected model:",
            self.best_model_name
        )

        print(
            "Best RMSE:",
            round(
                self.results[
                    self.best_model_name
                ]["RMSE"],
                4
            )
        )

        print(
            "Best R2:",
            round(
                self.results[
                    self.best_model_name
                ]["R2"],
                4
            )
        )

        # ====================================================
        # Save Best Model
        # ====================================================

        joblib.dump(
            self.best_model,
            self.model_path
        )

        print()
        print(
            "Model saved to:"
        )

        print(
            self.model_path
        )

        # ====================================================
        # Save Results
        # ====================================================

        results_dataframe = (
            pd.DataFrame(
                self.results
            ).T
        )

        results_dataframe.index.name = (
            "Model"
        )

        results_dataframe.to_csv(
            self.results_path
        )

        print()
        print(
            "Comparison results saved to:"
        )

        print(
            self.results_path
        )

        print()
        print("=" * 70)
        print("DEMAND MODEL TRAINING COMPLETED")
        print("=" * 70)

        return self.results

    # ========================================================
    # Load Model
    # ========================================================

    def load_model(self):

        if self.best_model is not None:

            return self.best_model

        if not os.path.exists(
            self.model_path
        ):

            raise FileNotFoundError(
                "Demand model has not been trained yet."
            )

        print(
            "Loading demand model..."
        )

        self.best_model = joblib.load(
            self.model_path
        )

        print(
            "Demand model loaded successfully."
        )

        return self.best_model

    # ========================================================
    # Predict Demand
    # ========================================================

    def predict(
        self,
        store_id,
        total_price,
        base_price
    ):

        # تحميل النموذج فقط عند الحاجة
        if self.best_model is None:

            self.load_model()

        # ----------------------------------------------------
        # Calculate discount
        # ----------------------------------------------------

        discount_amount = (
            base_price -
            total_price
        )

        # ----------------------------------------------------
        # Calculate discount percentage
        # ----------------------------------------------------

        if base_price != 0:

            discount_percentage = (
                discount_amount /
                base_price
            ) * 100

            price_ratio = (
                total_price /
                base_price
            )

        else:

            discount_percentage = 0

            price_ratio = 0

        # ----------------------------------------------------
        # Create prediction dataframe
        # ----------------------------------------------------

        prediction_data = pd.DataFrame([{

            "Store ID": store_id,

            "Total Price": total_price,

            "Base Price": base_price,

            "discount_amount": (
                discount_amount
            ),

            "discount_percentage": (
                discount_percentage
            ),

            "price_ratio": (
                price_ratio
            )
        }])

        # ----------------------------------------------------
        # Prediction
        # ----------------------------------------------------

        prediction = (
            self.best_model.predict(
                prediction_data[
                    self.features
                ]
            )
        )

        predicted_demand = float(
            prediction[0]
        )

        # منع القيم السالبة
        predicted_demand = max(
            0,
            predicted_demand
        )

        return predicted_demand

    # ========================================================
    # Get Results
    # ========================================================

    def get_results(self):

        return self.results

    # ========================================================
    # Get Best Model Name
    # ========================================================

    def get_best_model_name(self):

        return self.best_model_name