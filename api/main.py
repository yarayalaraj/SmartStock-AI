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
# الواجهة الأمامية Streamlit ستتصل بهذا الملف عن طريق HTTP API.
# ============================================================


# ============================================================
# 1. استيراد المكتبات
# ============================================================

from pathlib import Path
import uuid
import json

import pandas as pd

from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from integrations.square.square_client import SquareClient
from services.demand_model import DemandModel
from services.models.chatbot_service import generate_response
from services.image_model import predict_image


# ============================================================
# 2. إعداد مسارات المشروع
# ============================================================

# المسار الرئيسي للمشروع
PROJECT_ROOT = Path(__file__).resolve().parent.parent


# ملف تحليل مخاطر المخزون
RISK_DATA_PATH = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "inventory_expiry_risk_analysis.csv"
)


# ملف نتائج نموذج التنبؤ بالطلب
DEMAND_RESULTS_PATH = (
    PROJECT_ROOT
    / "models"
    / "demand_model_results.csv"
)


# ملف أسماء فئات الصور
IMAGE_CLASSES_PATH = (
    PROJECT_ROOT
    / "models"
    / "image_class_names.json"
)


# مجلد الصور المؤقتة التي يرفعها المستخدم
UPLOAD_DIR = (
    PROJECT_ROOT
    / "data"
    / "uploads"
)


# إنشاء مجلد رفع الصور إذا لم يكن موجودًا
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
# 4. السماح لـ Streamlit بالاتصال بالـ API
# ============================================================

app.add_middleware(
    CORSMiddleware,

    allow_origins=["*"],

    allow_credentials=True,

    allow_methods=["*"],

    allow_headers=["*"]
)


# ============================================================
# 5. إنشاء الخدمات الرئيسية
# ============================================================


# ------------------------------------------------------------
# إنشاء عميل Square
# ------------------------------------------------------------

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


# ------------------------------------------------------------
# إنشاء نموذج التنبؤ بالطلب
# ------------------------------------------------------------

try:

    demand_model = DemandModel()

except Exception as e:

    print(
        "Warning: Could not initialize DemandModel."
    )

    print(
        "Error:",
        e
    )

    demand_model = None


# ============================================================
# 6. إعداد Square Location
# ============================================================

# Location ID الخاص بحساب Square Sandbox
LOCATION_ID = "LCQJDMZ076NK1"


# ============================================================
# 7. نماذج البيانات Pydantic
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
# 8. الصفحة الرئيسية
# ============================================================

@app.get("/")
def root():
    """
    الصفحة الرئيسية للـ API.
    """

    return {
        "success": True,

        "project": "SmartStock AI",

        "description": (
            "Intelligent Inventory, Demand and "
            "Waste Management Platform"
        ),

        "api": "FastAPI",

        "status": "running",

        "docs": "/docs"
    }


# ============================================================
# 9. Health Check
# ============================================================

@app.get("/health")
def health_check():
    """
    فحص حالة المكونات الرئيسية للنظام.
    """

    return {

        "status": "healthy",

        # هل Square Client يعمل؟
        "square_client": (
            square_client is not None
        ),

        # هل نموذج الطلب يعمل؟
        "demand_model": (
            demand_model is not None
        ),

        # Chatbot متوفر
        "chatbot": True
    }


# ============================================================
# 10. جلب المبيعات من Square
# ============================================================

@app.get("/sales")
def get_sales():
    """
    جلب المبيعات من Square Sandbox.

    ملاحظة:
    البيانات هنا تأتي من Square Sandbox المستخدم
    لاختبار التكامل البرمجي، وليست بيانات مبيعات
    حقيقية لمتجر فعلي.
    """

    try:

        if square_client is None:

            return {
                "success": False,
                "error": (
                    "Square client is not available."
                )
            }


        result = square_client.get_orders(
            location_id=LOCATION_ID
        )


        return {

            "success": True,

            "source": "Square Sandbox",

            "data": result
        }


    except Exception as e:

        return {

            "success": False,

            "error": str(e)
        }


# ============================================================
# 11. جلب المخزون من Square
# ============================================================

@app.get("/inventory")
def get_inventory():
    """
    جلب المخزون الحالي من Square وعرضه
    بطريقة مناسبة لواجهة SmartStock AI.
    """

    try:

        if square_client is None:

            return {

                "success": False,

                "error": (
                    "Square client is not available."
                )
            }


        # ----------------------------------------------------
        # جلب جميع كميات المخزون من Square
        # ----------------------------------------------------

        inventory_counts = (
            square_client.get_inventory_count(
                catalog_object_id=None,
                location_id=LOCATION_ID
            )
        )


        if inventory_counts is None:

            inventory_counts = []


        # ----------------------------------------------------
        # تحويل بيانات Square إلى بيانات بسيطة
        # ----------------------------------------------------

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

            "success": True,

            "source": "Square Sandbox",

            "location_id": LOCATION_ID,

            "total_items":
                len(inventory_data),

            "data":
                inventory_data
        }


    except Exception as e:

        return {

            "success": False,

            "error": str(e)
        }


# ============================================================
# 12. جلب تحليل مخاطر المخزون
# ============================================================

@app.get("/inventory/risk")
def get_inventory_risk():
    """
    إرجاع تحليل مخاطر المخزون لجميع المنتجات.

    البيانات مبنية على UCI Stock Keeping Units Dataset
    مع نموذج K-Means وتحليل Risk Score.
    """

    try:

        # ----------------------------------------------------
        # التأكد من وجود الملف
        # ----------------------------------------------------

        if not RISK_DATA_PATH.exists():

            return {

                "success": False,

                "error": (
                    "Risk analysis file was not found: "
                    f"{RISK_DATA_PATH}"
                )
            }


        # ----------------------------------------------------
        # قراءة البيانات
        # ----------------------------------------------------

        df = pd.read_csv(
            RISK_DATA_PATH
        )


        # تحويل NaN إلى None
        df = df.where(
            pd.notnull(df),
            None
        )


        return {

            "success": True,

            "total_products":
                len(df),

            "data":
                df.to_dict(
                    orient="records"
                )
        }


    except Exception as e:

        return {

            "success": False,

            "error": str(e)
        }


# ============================================================
# 13. ملخص مخاطر المخزون
# ============================================================

@app.get("/inventory/risk/summary")
def get_inventory_risk_summary():
    """
    إرجاع ملخص توزيع مستويات المخاطر.
    """

    try:

        if not RISK_DATA_PATH.exists():

            return {

                "success": False,

                "error":
                    "Risk analysis file not found."
            }


        df = pd.read_csv(
            RISK_DATA_PATH
        )


        # اسم عمود مستوى المخاطر
        risk_column = (
            "inventory_expiry_risk_level"
        )


        if risk_column not in df.columns:

            return {

                "success": False,

                "error": (
                    f"Column '{risk_column}' "
                    "was not found."
                )
            }


        # حساب عدد المنتجات في كل مستوى
        distribution = (
            df[risk_column]
            .value_counts()
            .to_dict()
        )


        return {

            "success": True,

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

            "success": False,

            "error": str(e)
        }


# ============================================================
# 14. التنبؤ بالطلب
# ============================================================

@app.post("/demand/predict")
def predict_demand(
    request: DemandRequest
):
    """
    التنبؤ بعدد الوحدات المتوقع بيعها.

    النموذج المستخدم:
    Random Forest Regressor
    """

    try:

        if demand_model is None:

            return {

                "success": False,

                "error":
                    "Demand model is not available."
            }


        # ----------------------------------------------------
        # تنفيذ التنبؤ
        # ----------------------------------------------------

        prediction = (
            demand_model.predict(
                store_id=request.store_id,

                total_price=request.total_price,

                base_price=request.base_price
            )
        )


        return {

            "success": True,

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

            "success": False,

            "error": str(e)
        }


# ============================================================
# 15. نتائج نماذج التنبؤ بالطلب
# ============================================================

@app.get("/demand/results")
def get_demand_results():
    """
    إرجاع نتائج مقارنة نماذج التنبؤ بالطلب.
    """

    try:

        if not DEMAND_RESULTS_PATH.exists():

            return {

                "success": False,

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


        # ----------------------------------------------------
        # تحديد أفضل نموذج بناءً على R2
        # ----------------------------------------------------

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

            "success": True,

            "data":
                df.to_dict(
                    orient="records"
                ),

            "best_model":
                best_model
        }


    except Exception as e:

        return {

            "success": False,

            "error": str(e)
        }


# ============================================================
# 16. معلومات نموذج الصور
# ============================================================

@app.get("/image/info")
def get_image_model_info():
    """
    إرجاع معلومات نموذج تصنيف الصور.
    """

    try:

        classes = []


        # ----------------------------------------------------
        # قراءة أسماء الفئات
        # ----------------------------------------------------

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

            "success": True,

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

            "success": False,

            "error": str(e)
        }


# ============================================================
# 17. تصنيف صورة مرفوعة
# ============================================================

@app.post("/image/predict")
async def predict_uploaded_image(
    file: UploadFile = File(...)
):
    """
    استقبال صورة من المستخدم وتصنيفها باستخدام
    نموذج MobileNetV2 المدرب على RealWaste.

    أنواع الصور المدعومة:
    JPG
    JPEG
    PNG
    WEBP
    """

    image_path = None


    try:

        # ----------------------------------------------------
        # التأكد من اسم الملف
        # ----------------------------------------------------

        original_filename = (
            file.filename or ""
        )


        # استخراج امتداد الصورة
        extension = Path(
            original_filename
        ).suffix.lower()


        # ----------------------------------------------------
        # أنواع الملفات المسموح بها
        # ----------------------------------------------------

        allowed_extensions = {

            ".jpg",

            ".jpeg",

            ".png",

            ".webp"
        }


        if extension not in allowed_extensions:

            return {

                "success": False,

                "error": (
                    "نوع الملف غير مدعوم. "
                    "يرجى رفع JPG أو JPEG "
                    "أو PNG أو WEBP."
                )
            }


        # ----------------------------------------------------
        # إنشاء اسم آمن وفريد للصورة
        # ----------------------------------------------------

        unique_filename = (
            f"{uuid.uuid4().hex}"
            f"{extension}"
        )


        image_path = (
            UPLOAD_DIR
            / unique_filename
        )


        # ----------------------------------------------------
        # قراءة الصورة
        # ----------------------------------------------------

        image_bytes = await file.read()


        if not image_bytes:

            return {

                "success": False,

                "error":
                    "الصورة المرفوعة فارغة."
            }


        # ----------------------------------------------------
        # حفظ الصورة مؤقتًا
        # ----------------------------------------------------

        with open(
            image_path,
            "wb"
        ) as output_file:

            output_file.write(
                image_bytes
            )


        # ----------------------------------------------------
        # تشغيل نموذج MobileNetV2
        # ----------------------------------------------------

        prediction = predict_image(
            image_path
        )


        # ----------------------------------------------------
        # إرجاع النتيجة
        # ----------------------------------------------------

        return {

            "success": True,

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

            "success": False,

            "error": str(e)
        }


    finally:

        # ----------------------------------------------------
        # حذف الصورة المؤقتة
        # ----------------------------------------------------

        if image_path is not None:

            try:

                if image_path.exists():

                    image_path.unlink()

            except Exception:

                # عدم إيقاف البرنامج إذا فشل حذف الملف
                pass


# ============================================================
# 18. Transformer Chatbot
# ============================================================

@app.post("/chat")
def chat(
    request: ChatRequest
):
    """
    SmartStock AI Chatbot.

    ترتيب معالجة الأسئلة:

    1. أسئلة توزيع المخاطر.
    2. أسئلة المنتجات عالية المخاطر.
    3. أسئلة نموذج الصور.
    4. أسئلة المخزون.
    5. الأسئلة العامة باستخدام Transformer.

    الأسئلة المتعلقة ببيانات SmartStock
    تعتمد على البيانات الفعلية للنظام.
    """

    try:

        # ====================================================
        # 1. الحصول على السؤال
        # ====================================================

        question = (
            request.question.strip()
        )


        if not question:

            return {

                "success": False,

                "error":
                    "Question cannot be empty."
            }


        # lowercase للأسئلة الإنجليزية
        q = question.lower()


        # ====================================================
        # 2. أسئلة توزيع مخاطر المخزون
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

                    "success": True,

                    "question":
                        question,

                    "answer":
                        answer
                }


            return {

                "success": False,

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
        # 3. عدد المنتجات عالية المخاطر
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

                    "success": True,

                    "question":
                        question,

                    "answer":
                        answer
                }


            return {

                "success": False,

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
        # 4. أسئلة نموذج تصنيف الصور
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

                    "success": True,

                    "question":
                        question,

                    "answer":
                        answer
                }


            return {

                "success": False,

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
        # 5. أسئلة المخزون
        # ====================================================

        # مهم جدًا:
        #
        # لا نستخدم كلمة "المخزون" وحدها هنا.
        #
        # السبب:
        # السؤال:
        #
        # "ما توزيع مخاطر المخزون؟"
        #
        # يحتوي على كلمة "المخزون".
        #
        # لذلك يجب معالجة أسئلة المخاطر أولًا.


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


            # التأكد من توفر Square
            if square_client is None:

                return {

                    "success": False,

                    "question":
                        question,

                    "error":
                        "Square client is not available."
                }


            # ------------------------------------------------
            # جلب المخزون الحالي
            # ------------------------------------------------

            inventory_counts = (

                square_client.get_inventory_count(

                    catalog_object_id=None,

                    location_id=LOCATION_ID
                )
            )


            if inventory_counts is None:

                return {

                    "success": True,

                    "question":
                        question,

                    "answer": (
                        "تعذر الحصول على بيانات "
                        "المخزون حاليًا."
                    )
                }


            # ------------------------------------------------
            # حساب إجمالي الوحدات
            # ------------------------------------------------

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


            # ------------------------------------------------
            # تنسيق الرقم
            # ------------------------------------------------

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


            # ------------------------------------------------
            # صياغة الإجابة
            # ------------------------------------------------

            answer = (

                "المخزون المتبقي حاليًا في "
                "SmartStock هو "

                f"{quantity_text} وحدة."
            )


            return {

                "success": True,

                "question":
                    question,

                "answer":
                    answer
            }


        # ====================================================
        # 6. الأسئلة العامة
        # ====================================================

        # إذا لم يكن السؤال متعلقًا
        # ببيانات SmartStock،
        # يتم استخدام Transformer.


        answer = generate_response(
            question
        )


        return {

            "success": True,

            "question":
                question,

            "answer":
                answer
        }


    except Exception as e:

        return {

            "success": False,

            "question":
                request.question,

            "error":
                str(e)
        }


# ============================================================
# 19. Dashboard Summary
# ============================================================

@app.get("/dashboard/summary")
def dashboard_summary():
    """
    إرجاع البيانات الأساسية التي تحتاجها واجهة Streamlit.
    """

    try:

        # ====================================================
        # 1. بيانات المخاطر
        # ====================================================

        risk_distribution = {

            "Low": 0,

            "Medium": 0,

            "High": 0
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

                # استخدام النتائج المثبتة
                # في حال حدوث خطأ في قراءة الملف
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

            "success": True,

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

            "success": False,

            "error": str(e)
        }