# ============================================================
# SMARTSTOCK AI - FastAPI Backend
# ============================================================

from pathlib import Path
import json
import os
import traceback

import pandas as pd

from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from square.client import SquareClient


# ============================================================
# 1. إعداد مسارات المشروع
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
# 2. إنشاء FastAPI
# ============================================================

app = FastAPI(
    title="SMARTSTOCK AI API",
    description=(
        "Integrated AI Inventory Management Platform "
        "for clothing, makeup, restaurants and cafes."
    ),
    version="1.0.0"
)


# ============================================================
# 3. CORS
# ============================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# 4. Square Configuration
# ============================================================

try:

    from config.settings import SQUARE_ACCESS_TOKEN

except Exception:

    SQUARE_ACCESS_TOKEN = os.getenv(
        "SQUARE_ACCESS_TOKEN"
    )


try:

    from config.settings import SQUARE_ENVIRONMENT

except Exception:

    SQUARE_ENVIRONMENT = os.getenv(
        "SQUARE_ENVIRONMENT",
        "sandbox"
    )


# ============================================================
# 5. إنشاء Square Client
# ============================================================

square_client = None

try:

    if SQUARE_ACCESS_TOKEN:

        square_client = SquareClient(
            token=SQUARE_ACCESS_TOKEN
        )

        print(
            "Square client initialized successfully."
        )

    else:

        print(
            "WARNING: SQUARE_ACCESS_TOKEN is not configured."
        )

except Exception as e:

    print(
        "WARNING: Could not initialize Square client."
    )

    print(
        "Error:",
        str(e)
    )

    square_client = None


# ============================================================
# 6. Demand Model - Lazy Loading
# ============================================================

demand_model = None


def get_demand_model():
    """
    تحميل نموذج التنبؤ بالطلب عند الحاجة فقط.

    يتم تسجيل جميع تفاصيل الخطأ في Render Logs
    حتى نستطيع معرفة سبب فشل تحميل النموذج.
    """

    global demand_model

    # --------------------------------------------------------
    # إذا كان النموذج محملاً مسبقاً
    # --------------------------------------------------------

    if demand_model is not None:

        return demand_model

    # --------------------------------------------------------
    # بداية تحميل النموذج
    # --------------------------------------------------------

    print("=" * 60)

    print(
        "STARTING DEMAND MODEL LOADING"
    )

    print("=" * 60)

    try:

        # ----------------------------------------------------
        # استيراد DemandModel
        # ----------------------------------------------------

        print(
            "Importing DemandModel..."
        )

        from services.demand_model import DemandModel

        print(
            "DemandModel import: SUCCESS"
        )

        # ----------------------------------------------------
        # إنشاء الكائن
        # ----------------------------------------------------

        print(
            "Creating DemandModel object..."
        )

        demand_model = DemandModel()

        print(
            "DemandModel object created successfully."
        )

        print(
            "DemandModel type:",
            type(demand_model)
        )

        # ----------------------------------------------------
        # معرفة مسار النموذج
        # ----------------------------------------------------

        model_path = getattr(
            demand_model,
            "model_path",
            None
        )

        print(
            "Demand model path:",
            model_path
        )

        # ----------------------------------------------------
        # التحقق من وجود ملف النموذج
        # ----------------------------------------------------

        if model_path is not None:

            model_file = Path(
                model_path
            )

            print(
                "Model file exists:",
                model_file.exists()
            )

            print(
                "Model file:",
                model_file
            )

            if model_file.exists():

                try:

                    print(
                        "Model file size:",
                        model_file.stat().st_size,
                        "bytes"
                    )

                except Exception:

                    pass

        # ----------------------------------------------------
        # ملاحظة:
        # joblib.load() يتم تنفيذه لاحقاً داخل predict()
        # ----------------------------------------------------

        print(
            "DemandModel initialized successfully."
        )

        print("=" * 60)

        return demand_model

    except Exception as e:

        print("=" * 60)

        print(
            "DEMAND MODEL INITIALIZATION ERROR"
        )

        print("=" * 60)

        print(
            "Error type:",
            type(e).__name__
        )

        print(
            "Error:",
            str(e)
        )

        print(
            "Full traceback:"
        )

        traceback.print_exc()

        print("=" * 60)

        demand_model = None

        return None


# ============================================================
# 7. Square Location
# ============================================================

LOCATION_ID = "LCQJDMZ076NK1"


# ============================================================
# 8. Pydantic Models
# ============================================================

class DemandRequest(BaseModel):

    store_id: int

    total_price: float

    base_price: float


class ChatRequest(BaseModel):

    message: str


class InventoryRequest(BaseModel):

    catalog_object_id: str

    quantity: float


# ============================================================
# 9. Root Endpoint
# ============================================================

@app.get("/")
def root():

    return {
        "success": True,
        "message": "SMARTSTOCK AI API is running.",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }


# ============================================================
# 10. Health Check
# ============================================================

@app.get("/health")
def health():

    return {

        "status": "healthy",

        "square_client":
            square_client is not None,

        "demand_model":
            demand_model is not None,

        "chatbot":
            True
    }


# ============================================================
# 11. Demand Prediction
# ============================================================

@app.post("/demand/predict")
def predict_demand(
    request: DemandRequest
):

    try:

        # ----------------------------------------------------
        # بداية الطلب
        # ----------------------------------------------------

        print("=" * 60)

        print(
            "DEMAND PREDICTION REQUEST"
        )

        print("=" * 60)

        print(
            "Store ID:",
            request.store_id
        )

        print(
            "Total Price:",
            request.total_price
        )

        print(
            "Base Price:",
            request.base_price
        )

        # ----------------------------------------------------
        # تحميل النموذج
        # ----------------------------------------------------

        print(
            "Loading DemandModel..."
        )

        model = get_demand_model()

        print(
            "DemandModel object:",
            model
        )

        print(
            "DemandModel type:",
            type(model)
        )

        # ----------------------------------------------------
        # التحقق من النموذج
        # ----------------------------------------------------

        if model is None:

            print(
                "ERROR: Demand model is not available."
            )

            return {

                "success": False,

                "error":
                    "Demand model is not available."
            }

        # ----------------------------------------------------
        # تشغيل التنبؤ
        # ----------------------------------------------------

        print(
            "Calling model.predict()..."
        )

        prediction = model.predict(

            store_id=request.store_id,

            total_price=request.total_price,

            base_price=request.base_price
        )

        print(
            "Prediction:",
            prediction
        )

        print(
            "Prediction type:",
            type(prediction)
        )

        # ----------------------------------------------------
        # النتيجة
        # ----------------------------------------------------

        result = {

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

        print(
            "Demand prediction result:",
            result
        )

        print("=" * 60)

        return result

    except Exception as e:

        print("=" * 60)

        print(
            "DEMAND PREDICTION ERROR"
        )

        print("=" * 60)

        print(
            "Error type:",
            type(e).__name__
        )

        print(
            "Error:",
            str(e)
        )

        print(
            "Full traceback:"
        )

        traceback.print_exc()

        print("=" * 60)

        return {

            "success": False,

            "error":
                str(e),

            "error_type":
                type(e).__name__
        }


# ============================================================
# 12. Demand Model Results
# ============================================================

@app.get("/demand/results")
def demand_results():

    try:

        # ----------------------------------------------------
        # التحقق من وجود الملف
        # ----------------------------------------------------

        if not DEMAND_RESULTS_PATH.exists():

            return {

                "success": False,

                "error":
                    "Demand model results file not found.",

                "path":
                    str(DEMAND_RESULTS_PATH)
            }

        # ----------------------------------------------------
        # قراءة النتائج
        # ----------------------------------------------------

        df = pd.read_csv(
            DEMAND_RESULTS_PATH
        )

        # ----------------------------------------------------
        # تحويل البيانات إلى JSON
        # ----------------------------------------------------

        records = df.to_dict(
            orient="records"
        )

        # ----------------------------------------------------
        # محاولة تحديد أفضل نموذج
        # ----------------------------------------------------

        best_model = None

        if "R2" in df.columns:

            best_row = df.loc[
                df["R2"].idxmax()
            ]

            best_model = {

                "model":
                    best_row.get(
                        "Model",
                        best_row.get(
                            "model",
                            "Unknown"
                        )
                    ),

                "R2":
                    float(
                        best_row["R2"]
                    )
            }

        return {

            "success": True,

            "results": records,

            "best_model":
                best_model
        }

    except Exception as e:

        return {

            "success": False,

            "error":
                str(e),

            "error_type":
                type(e).__name__
        }


# ============================================================
# 13. Dashboard Summary
# ============================================================

@app.get("/dashboard/summary")
def dashboard_summary():

    result = {

        "success": True,

        "inventory": {

            "status":
                "available"
        },

        "demand": {

            "status":
                "available",

            "results_endpoint":
                "/demand/results",

            "prediction_endpoint":
                "/demand/predict"
        },

        "image_ai": {

            "status":
                "available"
        },

        "integration": {

            "square":
                square_client is not None
        }
    }

    # --------------------------------------------------------
    # قراءة بيانات المخاطر إذا كانت موجودة
    # --------------------------------------------------------

    try:

        if RISK_DATA_PATH.exists():

            df = pd.read_csv(
                RISK_DATA_PATH
            )

            result["inventory"][
                "rows"
            ] = len(df)

            result["inventory"][
                "columns"
            ] = list(df.columns)

        else:

            result["inventory"][
                "rows"
            ] = 0

    except Exception as e:

        result["inventory"][
            "error"
        ] = str(e)

    # --------------------------------------------------------
    # قراءة نتائج نموذج الطلب
    # --------------------------------------------------------

    try:

        if DEMAND_RESULTS_PATH.exists():

            df = pd.read_csv(
                DEMAND_RESULTS_PATH
            )

            result["demand"][
                "models_tested"
            ] = len(df)

        else:

            result["demand"][
                "models_tested"
            ] = 0

    except Exception as e:

        result["demand"][
            "error"
        ] = str(e)

    # --------------------------------------------------------
    # Image AI
    # --------------------------------------------------------

    try:

        if IMAGE_CLASSES_PATH.exists():

            with open(
                IMAGE_CLASSES_PATH,
                "r",
                encoding="utf-8"
            ) as f:

                classes = json.load(f)

            result["image_ai"][
                "classes"
            ] = classes

        else:

            result["image_ai"][
                "classes"
            ] = []

    except Exception as e:

        result["image_ai"][
            "error"
        ] = str(e)

    return result


# ============================================================
# 14. Image AI Information
# ============================================================

@app.get("/image/info")
def image_info():

    try:

        classes = []

        if IMAGE_CLASSES_PATH.exists():

            with open(
                IMAGE_CLASSES_PATH,
                "r",
                encoding="utf-8"
            ) as f:

                classes = json.load(f)

        return {

            "success": True,

            "model":
                "MobileNetV2",

            "classes":
                classes,

            "classes_count":
                len(classes)
        }

    except Exception as e:

        return {

            "success": False,

            "error":
                str(e),

            "error_type":
                type(e).__name__
        }


# ============================================================
# 15. Image Upload
# ============================================================

@app.post("/image/upload")
async def upload_image(
    file: UploadFile = File(...)
):

    try:

        # ----------------------------------------------------
        # التحقق من نوع الملف
        # ----------------------------------------------------

        allowed_extensions = {

            ".jpg",
            ".jpeg",
            ".png",
            ".webp"
        }

        filename = file.filename or "uploaded_image"

        extension = Path(
            filename
        ).suffix.lower()

        if extension not in allowed_extensions:

            raise HTTPException(

                status_code=400,

                detail=(
                    "Unsupported image format. "
                    "Use JPG, JPEG, PNG or WEBP."
                )
            )

        # ----------------------------------------------------
        # اسم آمن للملف
        # ----------------------------------------------------

        safe_filename = (
            Path(filename).name
        )

        file_path = (
            UPLOAD_DIR
            / safe_filename
        )

        # ----------------------------------------------------
        # حفظ الصورة
        # ----------------------------------------------------

        contents = await file.read()

        with open(
            file_path,
            "wb"
        ) as f:

            f.write(contents)

        return {

            "success": True,

            "filename":
                safe_filename,

            "path":
                str(file_path),

            "size":
                len(contents)
        }

    except HTTPException:

        raise

    except Exception as e:

        return {

            "success": False,

            "error":
                str(e),

            "error_type":
                type(e).__name__
        }


# ============================================================
# 16. Chatbot
# ============================================================

@app.post("/chat")
def chat(
    request: ChatRequest
):

    try:

        message = (
            request.message
            .strip()
        )

        if not message:

            return {

                "success": False,

                "error":
                    "Message cannot be empty."
            }

        # ----------------------------------------------------
        # محاولة استخدام Chatbot الموجود في المشروع
        # ----------------------------------------------------

        try:

            from services.chatbot import Chatbot

            chatbot = Chatbot()

            response = chatbot.chat(
                message
            )

            return {

                "success": True,

                "message":
                    message,

                "response":
                    response
            }

        except Exception as chatbot_error:

            print(
                "Chatbot service error:",
                str(chatbot_error)
            )

            # ------------------------------------------------
            # رد احتياطي
            # ------------------------------------------------

            return {

                "success": True,

                "message":
                    message,

                "response":
                    (
                        "مرحباً بك في SMARTSTOCK AI. "
                        "يمكنني مساعدتك في تحليل المخزون، "
                        "التنبؤ بالطلب، المنتجات، "
                        "المبيعات والمخاطر."
                    ),

                "fallback":
                    True
            }

    except Exception as e:

        return {

            "success": False,

            "error":
                str(e),

            "error_type":
                type(e).__name__
        }


# ============================================================
# 17. Square - Test Connection
# ============================================================

@app.get("/square/test")
def square_test():

    if square_client is None:

        return {

            "success": False,

            "connected": False,

            "error":
                "Square client is not configured."
        }

    try:

        response = (
            square_client.locations.list()
        )

        locations = []

        if hasattr(
            response,
            "locations"
        ):

            locations = [

                {

                    "id":
                        location.id,

                    "name":
                        location.name,

                    "status":
                        location.status,

                    "country":
                        location.country,

                    "currency":
                        location.currency
                }

                for location
                in response.locations
            ]

        return {

            "success": True,

            "connected": True,

            "locations":
                locations
        }

    except Exception as e:

        return {

            "success": False,

            "connected": False,

            "error":
                str(e),

            "error_type":
                type(e).__name__
        }


# ============================================================
# 18. Square - Locations
# ============================================================

@app.get("/square/locations")
def square_locations():

    if square_client is None:

        return {

            "success": False,

            "error":
                "Square client is not configured."
        }

    try:

        response = (
            square_client.locations.list()
        )

        locations = []

        if hasattr(
            response,
            "locations"
        ):

            for location in response.locations:

                locations.append({

                    "id":
                        location.id,

                    "name":
                        location.name,

                    "status":
                        location.status,

                    "country":
                        location.country,

                    "currency":
                        location.currency
                })

        return {

            "success": True,

            "count":
                len(locations),

            "locations":
                locations
        }

    except Exception as e:

        return {

            "success": False,

            "error":
                str(e),

            "error_type":
                type(e).__name__
        }


# ============================================================
# 19. Square - Catalog
# ============================================================

@app.get("/square/catalog")
def square_catalog():

    if square_client is None:

        return {

            "success": False,

            "error":
                "Square client is not configured."
        }

    try:

        response = (
            square_client.catalog.list()
        )

        objects = []

        if hasattr(
            response,
            "objects"
        ):

            for obj in response.objects:

                item = {

                    "id":
                        obj.id,

                    "type":
                        obj.type
                }

                if hasattr(
                    obj,
                    "item_data"
                ):

                    item[
                        "item_data"
                    ] = str(
                        obj.item_data
                    )

                if hasattr(
                    obj,
                    "item_variation_data"
                ):

                    item[
                        "item_variation_data"
                    ] = str(
                        obj.item_variation_data
                    )

                objects.append(
                    item
                )

        return {

            "success": True,

            "count":
                len(objects),

            "objects":
                objects
        }

    except Exception as e:

        return {

            "success": False,

            "error":
                str(e),

            "error_type":
                type(e).__name__
        }


# ============================================================
# 20. Square - Inventory
# ============================================================

@app.get("/square/inventory")
def square_inventory():

    if square_client is None:

        return {

            "success": False,

            "error":
                "Square client is not configured."
        }

    try:

        response = (
            square_client.inventory.batch_retrieve_inventory_counts(
                body={
                    "catalog_object_ids": []
                }
            )
        )

        counts = []

        if hasattr(
            response,
            "counts"
        ):

            for count in response.counts:

                counts.append({

                    "catalog_object_id":
                        count.catalog_object_id,

                    "state":
                        count.state,

                    "quantity":
                        count.quantity,

                    "location_id":
                        getattr(
                            count,
                            "location_id",
                            None
                        )
                })

        return {

            "success": True,

            "count":
                len(counts),

            "inventory":
                counts
        }

    except Exception as e:

        return {

            "success": False,

            "error":
                str(e),

            "error_type":
                type(e).__name__
        }


# ============================================================
# 21. Global Exception Handler
# ============================================================

@app.exception_handler(Exception)
async def global_exception_handler(
    request,
    exc
):

    print("=" * 60)

    print(
        "GLOBAL API ERROR"
    )

    print("=" * 60)

    print(
        "Path:",
        request.url.path
    )

    print(
        "Method:",
        request.method
    )

    print(
        "Error type:",
        type(exc).__name__
    )

    print(
        "Error:",
        str(exc)
    )

    traceback.print_exc()

    print("=" * 60)

    return {

        "success": False,

        "error":
            str(exc),

        "error_type":
            type(exc).__name__,

        "path":
            request.url.path
    }


# ============================================================
# 22. تشغيل مباشر
# ============================================================

if __name__ == "__main__":

    import uvicorn

    uvicorn.run(

        "api.main:app",

        host="0.0.0.0",

        port=int(
            os.getenv(
                "PORT",
                "8000"
            )
        ),

        reload=False
    )