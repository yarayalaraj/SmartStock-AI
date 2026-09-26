# ============================================================
# SmartStock AI
# FastAPI Central Backend
# ============================================================
#
# هذا الملف هو الواجهة الخلفية الرئيسية للمشروع.
#
# الوظائف التي يوفرها:
# 1. فحص حالة النظام
# 2. جلب المبيعات من Square
# 3. جلب المخزون من Square
# 4. تحليل مخاطر المخزون ومدة الصلاحية
# 5. التنبؤ بالطلب باستخدام Random Forest
# 6. معلومات نموذج تصنيف الصور MobileNetV2
# 7. تصنيف صورة مرفوعة من المستخدم
# 8. Transformer Chatbot
# 9. ملخص Dashboard
#
# تم استخدام Lazy Loading لنماذج الذكاء الاصطناعي
# لتقليل استهلاك الذاكرة عند تشغيل FastAPI.
# ============================================================


# ============================================================
# 1. استيراد المكتبات الأساسية
# ============================================================

from pathlib import Path
import uuid
import json

import pandas as pd

from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from integrations.square.square_client import SquareClient


# ============================================================
# 2. إعداد مسارات المشروع
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent


RISK_DATA_PATH = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "inventory_expiry_risk_analysis.csv"
)


DEMAND_RESULTS_PATH = (
    PROJECT_ROOT
    / "models"
    / "demand_model_results.csv"
)


IMAGE_CLASSES_PATH = (
    PROJECT_ROOT
    / "models"
    / "image_class_names.json"
)


UPLOAD_DIR = (
    PROJECT_ROOT
    / "data"
    / "uploads"
)


UPLOAD_DIR.mkdir(
    parents=True,
    exist_ok=True
)


# ============================================================
# 3. إنشاء FastAPI Application
# ============================================================

app = FastAPI(
    title="SmartStock AI API",
    description=(
        "Central Backend API for SmartStock AI - "
        "Intelligent Inventory, Demand and Waste Management Platform"
    ),
    version="1.0.0"
)


# ============================================================
# 4. إعداد CORS
# ============================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


# ============================================================
# 5. إنشاء Square Client
# ============================================================

try:

    square_client = SquareClient()

except Exception as e:

    print(
        "Warning: Could not initialize SquareClient."
    )

    print(
        "Error:",
        e
    )

    square_client = None


# ============================================================
# 6. Lazy Loading لنموذج التنبؤ بالطلب
# ============================================================

demand_model = None


def get_demand_model():
    """
    تحميل نموذج التنبؤ بالطلب عند الحاجة فقط.

    بهذه الطريقة لا يتم تحميل نموذج Random Forest
    عند تشغيل FastAPI، وإنما فقط عندما يطلب المستخدم
    endpoint الخاص بالتنبؤ.
    """

    global demand_model

    if demand_model is None:

        try:

            # يتم استيراد النموذج عند الحاجة فقط
            from services.demand_model import DemandModel

            demand_model = DemandModel()

            print(
                "DemandModel loaded successfully."
            )

        except Exception as e:

            print(
                "Warning: Could not initialize DemandModel."
            )

            print(
                "Error:",
                e
            )

            return None

    return demand_model


# ============================================================
# 7. إعداد Square Location
# ============================================================

LOCATION_ID = "LCQJDMZ076NK1"


# ============================================================
# 8. نماذج البيانات Pydantic
# ============================================================


class DemandRequest(BaseModel):
    """
    البيانات المطلوبة للتنبؤ بالطلب.
    """

    store_id: int

    total_price: float

    base_price: float


class ChatRequest(BaseModel):
    """
    السؤال الذي يرسله المستخدم إلى Chatbot.
    """

    question: str


# ============================================================
# 9. الصفحة الرئيسية
# ============================================================

@app.get("/")
def root():

    return {

        "success": True,

        "project":
            "SmartStock AI",

        "description": (
            "Intelligent Inventory, Demand and "
            "Waste Management Platform"
        ),

        "api":
            "FastAPI",

        "status":
            "running",

        "docs":
            "/docs"
    }


# ============================================================
# 10. Health Check
# ============================================================

@app.get("/health")
def health_check():
    """
    فحص حالة المكونات الرئيسية للنظام.

    ملاحظة:
    demand_model يكون False عند بداية التشغيل بشكل طبيعي،
    لأنه يتم تحميله فقط عند أول طلب للتنبؤ.
    """

    return {

        "status":
            "healthy",

        "square_client":
            square_client is not None,

        "demand_model":
            demand_model is not None,

        "chatbot":
            True
    }


# ============================================================
# 11. جلب المبيعات من Square
# ============================================================

@app.get("/sales")
def get_sales():

    try:

        if square_client is None:

            return {

                "success":
                    False,

                "error":
                    "Square client is not available."
            }


        result = square_client.get_orders(
            location_id=LOCATION_ID
        )


        return {

            "success":
                True,

            "source":
                "Square Sandbox",

            "data":
                result
        }


    except Exception as e:

        return {

            "success":
                False,

            "error":
                str(e)
        }


# ============================================================
# 12. جلب المخزون من Square
# ============================================================

@app.get("/inventory")
def get_inventory():

    try:

        if square_client is None:

            return {

                "success":
                    False,

                "error":
                    "Square client is not available."
            }


        inventory_counts = (
            square_client.get_inventory_count(
                catalog_object_id=None,
                location_id=LOCATION_ID
            )
        )


        if inventory_counts is None:

            inventory_counts = []


        inventory_data = []


        for count in inventory_counts:

            try:

                quantity = float(
                    count.get(
                        "quantity",
                        0
                    )
                )

            except (
                TypeError,
                ValueError
            ):

                quantity = 0.0


            inventory_data.append({

                "catalog_object_id":
                    count.get(
                        "catalog_object_id"
                    ),

                "catalog_object_type":
                    count.get(
                        "catalog_object_type"
                    ),

                "location_id":
                    count.get(
                        "location_id"
                    ),

                "state":
                    count.get(
                        "state"
                    ),

                "quantity":
                    quantity,

                "calculated_at":
                    count.get(
                        "calculated_at"
                    )
            })


        return {

            "success":
                True,

            "source":
                "Square Sandbox",

            "location_id":
                LOCATION_ID,

            "total_items":
                len(inventory_data),

            "data":
                inventory_data
        }


    except Exception as e:

        return {

            "success":
                False,

            "error":
                str(e)
        }


# ============================================================
# 13. جلب تحليل مخاطر المخزون
# ============================================================

@app.get("/inventory/risk")
def get_inventory_risk():

    try:

        if not RISK_DATA_PATH.exists():

            return {

                "success":
                    False,

                "error": (
                    "Risk analysis file was not found: "
                    f"{RISK_DATA_PATH}"
                )
            }


        df = pd.read_csv(
            RISK_DATA_PATH
        )


        df = df.where(
            pd.notnull(df),
            None
        )


        return {

            "success":
                True,

            "total_products":
                len(df),

            "data":
                df.to_dict(
                    orient="records"
                )
        }


    except Exception as e:

        return {

            "success":
                False,

            "error":
                str(e)
        }


# ============================================================
# 14. ملخص مخاطر المخزون
# ============================================================

@app.get("/inventory/risk/summary")
def get_inventory_risk_summary():

    try:

        if not RISK_DATA_PATH.exists():

            return {

                "success":
                    False,

                "error":
                    "Risk analysis file not found."
            }


        df = pd.read_csv(
            RISK_DATA_PATH
        )


        risk_column = (
            "inventory_expiry_risk_level"
        )


        if risk_column not in df.columns:

            return {

                "success":
                    False,

                "error": (
                    f"Column '{risk_column}' "
                    "was not found."
                )
            }


        distribution = (
            df[risk_column]
            .value_counts()
            .to_dict()
        )


        return {

            "success":
                True,

            "total_products":
                len(df),

            "risk_distribution": {

                "Low":
                    int(
                        distribution.get(
                            "Low",
                            0
                        )
                    ),

                "Medium":
                    int(
                        distribution.get(
                            "Medium",
                            0
                        )
                    ),

                "High":
                    int(
                        distribution.get(
                            "High",
                            0
                        )
                    )
            }
        }


    except Exception as e:

        return {

            "success":
                False,

            "error":
                str(e)
        }


# ============================================================
# 15. التنبؤ بالطلب
# ============================================================

@app.post("/demand/predict")
def predict_demand(
    request: DemandRequest
):

    try:

        # ----------------------------------------------------
        # تحميل النموذج عند الحاجة فقط
        # ----------------------------------------------------

        model = get_demand_model()


        if model is None:

            return {

                "success":
                    False,

                "error":
                    "Demand model is not available."
            }


        prediction = (
            model.predict(
                store_id=request.store_id,

                total_price=request.total_price,

                base_price=request.base_price
            )
        )


        return {

            "success":
                True,

            "model":
                "Random Forest Regressor",

            "input": {

                "store_id":
                    request.store_id,

                "total_price":
                    request.total_price,

                "base_price":
                    request.base_price
            },

            "prediction":
                float(prediction),

            "predicted_units_sold":
                round(
                    float(prediction),
                    2
                )
        }


    except Exception as e:

        return {

            "success":
                False,

            "error":
                str(e)
        }


# ============================================================
# 16. نتائج نماذج التنبؤ بالطلب
# ============================================================

@app.get("/demand/results")
def get_demand_results():

    try:

        if not DEMAND_RESULTS_PATH.exists():

            return {

                "success":
                    False,

                "error":
                    "Demand results file not found."
            }


        df = pd.read_csv(
            DEMAND_RESULTS_PATH
        )


        df = df.where(
            pd.notnull(df),
            None
        )


        best_model = None


        if "R2" in df.columns:

            best_row = df.loc[
                df["R2"].idxmax()
            ]


            best_model = {

                "model":
                    str(
                        best_row.iloc[0]
                    ),

                "R2":
                    float(
                        best_row["R2"]
                    )
            }


        return {

            "success":
                True,

            "data":
                df.to_dict(
                    orient="records"
                ),

            "best_model":
                best_model
        }


    except Exception as e:

        return {

            "success":
                False,

            "error":
                str(e)
        }


# ============================================================
# 17. معلومات نموذج الصور
# ============================================================

@app.get("/image/info")
def get_image_model_info():

    try:

        classes = []


        if IMAGE_CLASSES_PATH.exists():

            with open(
                IMAGE_CLASSES_PATH,
                "r",
                encoding="utf-8"
            ) as file:

                classes = json.load(
                    file
                )


        return {

            "success":
                True,

            "model":
                "MobileNetV2",

            "dataset":
                "RealWaste",

            "accuracy":
                0.7882,

            "accuracy_percentage":
                "78.82%",

            "number_of_classes":
                len(classes),

            "classes":
                classes
        }


    except Exception as e:

        return {

            "success":
                False,

            "error":
                str(e)
        }


# ============================================================
# 18. تصنيف صورة مرفوعة
# ============================================================

@app.post("/image/predict")
async def predict_uploaded_image(
    file: UploadFile = File(...)
):

    image_path = None


    try:

        original_filename = (
            file.filename or ""
        )


        extension = Path(
            original_filename
        ).suffix.lower()


        allowed_extensions = {

            ".jpg",

            ".jpeg",

            ".png",

            ".webp"
        }


        if extension not in allowed_extensions:

            return {

                "success":
                    False,

                "error": (
                    "نوع الملف غير مدعوم. "
                    "يرجى رفع JPG أو JPEG "
                    "أو PNG أو WEBP."
                )
            }


        unique_filename = (
            f"{uuid.uuid4().hex}"
            f"{extension}"
        )


        image_path = (
            UPLOAD_DIR
            / unique_filename
        )


        image_bytes = await file.read()


        if not image_bytes:

            return {

                "success":
                    False,

                "error":
                    "الصورة المرفوعة فارغة."
            }


        with open(
            image_path,
            "wb"
        ) as output_file:

            output_file.write(
                image_bytes
            )


        # ----------------------------------------------------
        # Lazy Loading
        # يتم استيراد نموذج الصور عند طلب الصورة فقط.
        # ----------------------------------------------------

        from services.image_model import predict_image


        prediction = predict_image(
            image_path
        )


        return {

            "success":
                True,

            "filename":
                original_filename,

            "model":
                "MobileNetV2",

            "dataset":
                "RealWaste",

            "prediction":
                prediction
        }


    except Exception as e:

        return {

            "success":
                False,

            "error":
                str(e)
        }


    finally:

        if image_path is not None:

            try:

                if image_path.exists():

                    image_path.unlink()

            except Exception:

                pass


# ============================================================
# 19. Transformer Chatbot
# ============================================================

@app.post("/chat")
def chat(
    request: ChatRequest
):

    try:

        question = (
            request.question.strip()
        )


        if not question:

            return {

                "success":
                    False,

                "error":
                    "Question cannot be empty."
            }


        q = question.lower()


        # ====================================================
        # 1. أسئلة توزيع مخاطر المخزون
        # ====================================================

        risk_distribution_keywords = [

            "توزيع المخاطر",

            "توزيع مخاطر المخزون",

            "ما توزيع مخاطر المخزون",

            "مخاطر المخزون",

            "توزيع المخزون من ناحية المخاطر",

            "risk distribution",

            "inventory risk"
        ]


        if any(
            keyword in q
            for keyword in risk_distribution_keywords
        ):

            risk_response = (
                get_inventory_risk_summary()
            )


            if risk_response.get(
                "success"
            ):

                distribution = (
                    risk_response.get(
                        "risk_distribution",
                        {}
                    )
                )


                low = distribution.get(
                    "Low",
                    0
                )


                medium = distribution.get(
                    "Medium",
                    0
                )


                high = distribution.get(
                    "High",
                    0
                )


                total = (
                    risk_response.get(
                        "total_products",
                        0
                    )
                )


                answer = (

                    "توزيع مخاطر المخزون في "
                    "SmartStock هو: "

                    f"{low} منتج منخفض المخاطر، "

                    f"{medium} منتج متوسط المخاطر، "

                    f"و{high} منتج مرتفع المخاطر، "

                    f"من إجمالي {total} منتجًا."
                )


                return {

                    "success":
                        True,

                    "question":
                        question,

                    "answer":
                        answer
                }


            return {

                "success":
                    False,

                "question":
                    question,

                "error":
                    risk_response.get(
                        "error",
                        "تعذر الحصول على "
                        "بيانات المخاطر."
                    )
            }


        # ====================================================
        # 2. المنتجات عالية المخاطر
        # ====================================================

        high_risk_keywords = [

            "عالية المخاطر",

            "عالي المخاطر",

            "مرتفع المخاطر",

            "المنتجات عالية المخاطر",

            "عدد المنتجات عالية",

            "كم منتج عالي المخاطر",

            "كم عدد المنتجات عالية المخاطر",

            "high risk"
        ]


        if any(
            keyword in q
            for keyword in high_risk_keywords
        ):

            risk_response = (
                get_inventory_risk_summary()
            )


            if risk_response.get(
                "success"
            ):

                distribution = (
                    risk_response.get(
                        "risk_distribution",
                        {}
                    )
                )


                high = distribution.get(
                    "High",
                    0
                )


                answer = (

                    "عدد المنتجات عالية "
                    f"المخاطر هو {high} منتجًا."
                )


                return {

                    "success":
                        True,

                    "question":
                        question,

                    "answer":
                        answer
                }


            return {

                "success":
                    False,

                "question":
                    question,

                "error":
                    risk_response.get(
                        "error",
                        "تعذر الحصول على "
                        "بيانات المخاطر."
                    )
            }


        # ====================================================
        # 3. أسئلة نموذج الصور
        # ====================================================

        image_keywords = [

            "دقة نموذج الصور",

            "دقة نموذج تصنيف الصور",

            "نموذج الصور",

            "تصنيف الصور",

            "دقة الصور",

            "دقة الموديل",

            "image accuracy",

            "image model",

            "mobilenet"
        ]


        if any(
            keyword in q
            for keyword in image_keywords
        ):

            image_info = (
                get_image_model_info()
            )


            if image_info.get(
                "success"
            ):

                model_name = (
                    image_info.get(
                        "model",
                        "MobileNetV2"
                    )
                )


                accuracy = (
                    image_info.get(
                        "accuracy_percentage",
                        "غير متوفر"
                    )
                )


                classes_count = (
                    image_info.get(
                        "number_of_classes",
                        0
                    )
                )


                answer = (

                    "نموذج تصنيف الصور "
                    "المستخدم هو "

                    f"{model_name}، "

                    f"بدقة {accuracy}، "

                    f"ويصنف {classes_count} فئات."
                )


                return {

                    "success":
                        True,

                    "question":
                        question,

                    "answer":
                        answer
                }


            return {

                "success":
                    False,

                "question":
                    question,

                "error":
                    image_info.get(
                        "error",
                        "تعذر الحصول على "
                        "معلومات نموذج الصور."
                    )
            }


        # ====================================================
        # 4. أسئلة المخزون
        # ====================================================

        inventory_keywords = [

            "المخزون المتبقي",

            "كم المخزون",

            "كمية المخزون",

            "كم المتبقي",

            "المتبقي من المخزون",

            "رصيد المخزون",

            "كم وحدة متبقية",

            "كم عدد الوحدات المتبقية",

            "inventory",

            "stock",

            "remaining stock"
        ]


        if any(
            keyword in q
            for keyword in inventory_keywords
        ):

            if square_client is None:

                return {

                    "success":
                        False,

                    "question":
                        question,

                    "error":
                        "Square client is not available."
                }


            inventory_counts = (

                square_client.get_inventory_count(

                    catalog_object_id=None,

                    location_id=LOCATION_ID
                )
            )


            if inventory_counts is None:

                return {

                    "success":
                        True,

                    "question":
                        question,

                    "answer": (
                        "تعذر الحصول على بيانات "
                        "المخزون حاليًا."
                    )
                }


            total_quantity = 0.0


            for count in inventory_counts:

                try:

                    quantity = float(

                        count.get(
                            "quantity",
                            0
                        ) or 0
                    )


                    total_quantity += (
                        quantity
                    )


                except (
                    TypeError,
                    ValueError
                ):

                    continue


            if total_quantity.is_integer():

                quantity_text = str(

                    int(
                        total_quantity
                    )
                )

            else:

                quantity_text = (

                    f"{total_quantity:.2f}"
                )


            answer = (

                "المخزون المتبقي حاليًا في "
                "SmartStock هو "

                f"{quantity_text} وحدة."
            )


            return {

                "success":
                    True,

                "question":
                    question,

                "answer":
                    answer
            }


        # ====================================================
        # 5. الأسئلة العامة
        # ====================================================

        # ----------------------------------------------------
        # Lazy Loading للـ Transformer Chatbot
        # ----------------------------------------------------

        from services.models.chatbot_service import generate_response


        answer = generate_response(
            question
        )


        return {

            "success":
                True,

            "question":
                question,

            "answer":
                answer
        }


    except Exception as e:

        return {

            "success":
                False,

            "question":
                request.question,

            "error":
                str(e)
        }


# ============================================================
# 20. Dashboard Summary
# ============================================================

@app.get("/dashboard/summary")
def dashboard_summary():

    try:

        # ====================================================
        # 1. بيانات المخاطر
        # ====================================================

        risk_distribution = {

            "Low":
                0,

            "Medium":
                0,

            "High":
                0
        }


        total_products = 0


        if RISK_DATA_PATH.exists():

            risk_df = pd.read_csv(
                RISK_DATA_PATH
            )


            total_products = len(
                risk_df
            )


            if (
                "inventory_expiry_risk_level"
                in risk_df.columns
            ):

                counts = (

                    risk_df[
                        "inventory_expiry_risk_level"
                    ]

                    .value_counts()

                    .to_dict()
                )


                risk_distribution = {

                    "Low":
                        int(
                            counts.get(
                                "Low",
                                0
                            )
                        ),

                    "Medium":
                        int(
                            counts.get(
                                "Medium",
                                0
                            )
                        ),

                    "High":
                        int(
                            counts.get(
                                "High",
                                0
                            )
                        )
                }


        # ====================================================
        # 2. نتائج Demand Model
        # ====================================================

        demand_info = {

            "model":
                "Random Forest Regressor",

            "R2":
                0.6092,

            "MAE":
                19.1346,

            "RMSE":
                35.8088
        }


        if DEMAND_RESULTS_PATH.exists():

            try:

                demand_df = pd.read_csv(
                    DEMAND_RESULTS_PATH
                )


                if "R2" in demand_df.columns:

                    best_row = demand_df.loc[
                        demand_df["R2"].idxmax()
                    ]


                    demand_info = {

                        "model":
                            str(
                                best_row.iloc[0]
                            ),

                        "R2":
                            float(
                                best_row["R2"]
                            ),

                        "MAE":
                            float(
                                best_row["MAE"]
                            )
                            if "MAE"
                            in demand_df.columns
                            else None,

                        "RMSE":
                            float(
                                best_row["RMSE"]
                            )
                            if "RMSE"
                            in demand_df.columns
                            else None
                    }


            except Exception:

                pass


        # ====================================================
        # 3. معلومات Image AI
        # ====================================================

        image_info = {

            "model":
                "MobileNetV2",

            "dataset":
                "RealWaste",

            "accuracy":
                0.7882,

            "accuracy_percentage":
                "78.82%"
        }


        # ====================================================
        # 4. النتيجة النهائية
        # ====================================================

        return {

            "success":
                True,

            "inventory": {

                "total_products":
                    total_products,

                "risk_distribution":
                    risk_distribution
            },

            "demand":
                demand_info,

            "image":
                image_info,

            "integrations": {

                "square":
                    square_client is not None,

                "chatbot":
                    True,

                "fastapi":
                    True
            }
        }


    except Exception as e:

        return {

            "success":
                False,

            "error":
                str(e)
        }