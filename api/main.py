# ============================================================
# SMARTSTOCK AI
# FastAPI Backend
# ============================================================

from pathlib import Path
import os
import json
import traceback

import pandas as pd

from fastapi import (
    FastAPI,
    HTTPException,
    UploadFile,
    File
)

from fastapi.middleware.cors import CORSMiddleware

from pydantic import BaseModel

# Square SDK الجديد
from square.client import Square


# ============================================================
# 1. Project Paths
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

MODELS_DIR = PROJECT_ROOT / "models"

DATA_DIR = PROJECT_ROOT / "data"

PROCESSED_DATA_DIR = (
    DATA_DIR / "processed"
)

UPLOAD_DIR = (
    DATA_DIR / "uploads"
)


# ============================================================
# 2. Project Files
# ============================================================

DEMAND_MODEL_PATH = (
    MODELS_DIR / "demand_model.pkl"
)

DEMAND_RESULTS_PATH = (
    MODELS_DIR / "demand_model_results.csv"
)

IMAGE_CLASSES_PATH = (
    MODELS_DIR / "image_class_names.json"
)

RISK_DATA_PATH = (
    PROCESSED_DATA_DIR
    / "inventory_expiry_risk_analysis.csv"
)


# إنشاء مجلد رفع الصور إذا لم يكن موجودًا

UPLOAD_DIR.mkdir(
    parents=True,
    exist_ok=True
)


# ============================================================
# 3. FastAPI Application
# ============================================================

app = FastAPI(
    title="SMARTSTOCK AI API",
    description=(
        "Integrated AI Inventory Management "
        "Platform"
    ),
    version="1.0.0"
)


# ============================================================
# 4. CORS
# ============================================================

app.add_middleware(

    CORSMiddleware,

    allow_origins=["*"],

    allow_credentials=True,

    allow_methods=["*"],

    allow_headers=["*"]
)


# ============================================================
# 5. Square Configuration
# ============================================================

SQUARE_ACCESS_TOKEN = os.getenv(
    "SQUARE_ACCESS_TOKEN"
)

SQUARE_ENVIRONMENT = os.getenv(
    "SQUARE_ENVIRONMENT",
    "sandbox"
)


print("=" * 60)

print(
    "SMARTSTOCK AI CONFIGURATION"
)

print("=" * 60)

print(
    "Square Environment:",
    SQUARE_ENVIRONMENT
)

print(
    "Square Access Token:",
    "SET"
    if SQUARE_ACCESS_TOKEN
    else "NOT SET"
)

print(
    "Project Root:",
    PROJECT_ROOT
)

print("=" * 60)


# ============================================================
# 6. Square Client
# ============================================================

square_client = None


try:

    if SQUARE_ACCESS_TOKEN:

        square_client = Square(
            token=SQUARE_ACCESS_TOKEN
        )

        print(
            "Square client initialized successfully."
        )

    else:

        print(
            "WARNING: "
            "SQUARE_ACCESS_TOKEN is not configured."
        )

except Exception as e:

    print(
        "WARNING: "
        "Could not initialize Square client."
    )

    print(
        "Error type:",
        type(e).__name__
    )

    print(
        "Error:",
        str(e)
    )

    traceback.print_exc()

    square_client = None


# ============================================================
# 7. Demand Model - Lazy Loading
# ============================================================

demand_model = None


def get_demand_model():

    global demand_model

    # --------------------------------------------------------
    # إذا كان النموذج محملاً مسبقًا
    # --------------------------------------------------------

    if demand_model is not None:

        return demand_model

    print("=" * 60)

    print(
        "STARTING DEMAND MODEL LOADING"
    )

    print("=" * 60)

    try:

        # ----------------------------------------------------
        # استيراد النموذج
        # ----------------------------------------------------

        print(
            "Importing DemandModel..."
        )

        from services.demand_model import (
            DemandModel
        )

        print(
            "DemandModel import: SUCCESS"
        )

        # ----------------------------------------------------
        # إنشاء النموذج
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
        # التحقق من وجود الملف
        # ----------------------------------------------------

        if model_path:

            model_file = Path(
                model_path
            )

            print(
                "Model file exists:",
                model_file.exists()
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
        # التحقق من وجود ملف النموذج المتوقع
        # ----------------------------------------------------

        print(
            "Expected model path:",
            DEMAND_MODEL_PATH
        )

        print(
            "Expected model exists:",
            DEMAND_MODEL_PATH.exists()
        )

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
# 8. Square Location
# ============================================================

LOCATION_ID = "LCQJDMZ076NK1"


# ============================================================
# 9. Request Models
# ============================================================

class DemandRequest(BaseModel):

    store_id: int

    total_price: float

    base_price: float


class ChatRequest(BaseModel):

    message: str


# ============================================================
# 10. Root
# ============================================================

@app.get("/")
def root():

    return {

        "success": True,

        "message":
            "SMARTSTOCK AI API is running.",

        "version":
            "1.0.0",

        "docs":
            "/docs",

        "health":
            "/health"
    }


# ============================================================
# 11. Health Check
# ============================================================

@app.get("/health")
def health():

    return {

        "status":
            "healthy",

        "square_client":
            square_client is not None,

        "demand_model":
            demand_model is not None,

        "demand_model_file":
            DEMAND_MODEL_PATH.exists(),

        "chatbot":
            True
    }


# ============================================================
# 12. Demand Prediction
# ============================================================

@app.post("/demand/predict")
def predict_demand(
    request: DemandRequest
):

    try:

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
        # التأكد من توفر النموذج
        # ----------------------------------------------------

        if model is None:

            return {

                "success": False,

                "error":
                    "Demand model is not available.",

                "model_file":
                    str(DEMAND_MODEL_PATH),

                "model_file_exists":
                    DEMAND_MODEL_PATH.exists()
            }

        # ----------------------------------------------------
        # تشغيل النموذج
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
            "Prediction result:",
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
# 13. Demand Model Results
# ============================================================

@app.get("/demand/results")
def demand_results():

    try:

        if not DEMAND_RESULTS_PATH.exists():

            return {

                "success": False,

                "error":
                    "Demand model results file not found.",

                "path":
                    str(DEMAND_RESULTS_PATH)
            }

        df = pd.read_csv(
            DEMAND_RESULTS_PATH
        )

        records = df.to_dict(
            orient="records"
        )

        best_model = None

        # ----------------------------------------------------
        # البحث عن أفضل R2
        # ----------------------------------------------------

        if (
            not df.empty
            and "R2" in df.columns
        ):

            best_row = df.loc[
                df["R2"].idxmax()
            ]

            model_name = "Unknown"

            if "Model" in df.columns:

                model_name = (
                    best_row["Model"]
                )

            elif "model" in df.columns:

                model_name = (
                    best_row["model"]
                )

            best_model = {

                "model":
                    model_name,

                "R2":
                    float(
                        best_row["R2"]
                    )
            }

        return {

            "success": True,

            "results":
                records,

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
# 14. Dashboard Summary
# ============================================================

@app.get("/dashboard/summary")
def dashboard_summary():

    result = {

        "success": True,

        "inventory": {

            "status":
                "available",

            "rows":
                0
        },

        "demand": {

            "status":
                "available",

            "models_tested":
                0,

            "prediction_endpoint":
                "/demand/predict"
        },

        "image_ai": {

            "status":
                "available",

            "classes":
                []
        },

        "integration": {

            "square":
                square_client is not None
        }
    }

    # --------------------------------------------------------
    # Inventory / Risk
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
                "status"
            ] = "data file not found"

    except Exception as e:

        result["inventory"][
            "error"
        ] = str(e)

    # --------------------------------------------------------
    # Demand Results
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
                "status"
            ] = "results file not found"

    except Exception as e:

        result["demand"][
            "error"
        ] = str(e)

    # --------------------------------------------------------
    # Image Classes
    # --------------------------------------------------------

    try:

        if IMAGE_CLASSES_PATH.exists():

            with open(
                IMAGE_CLASSES_PATH,
                "r",
                encoding="utf-8"
            ) as f:

                classes = json.load(f)

            # بعض الملفات قد تكون dict
            if isinstance(
                classes,
                dict
            ):

                classes = list(
                    classes.values()
                )

            result["image_ai"][
                "classes"
            ] = classes

        else:

            result["image_ai"][
                "status"
            ] = "class file not found"

    except Exception as e:

        result["image_ai"][
            "error"
        ] = str(e)

    return result


# ============================================================
# 15. Image AI Information
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

            if isinstance(
                classes,
                dict
            ):

                classes = list(
                    classes.values()
                )

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
# 16. Image Upload
# ============================================================

@app.post("/image/upload")
async def upload_image(
    file: UploadFile = File(...)
):

    try:

        allowed_extensions = {

            ".jpg",
            ".jpeg",
            ".png",
            ".webp"
        }

        filename = (
            file.filename
            or "uploaded_image"
        )

        extension = (
            Path(filename)
            .suffix
            .lower()
        )

        if extension not in allowed_extensions:

            raise HTTPException(

                status_code=400,

                detail=(
                    "Unsupported image format. "
                    "Use JPG, JPEG, PNG or WEBP."
                )
            )

        safe_filename = (
            Path(filename).name
        )

        file_path = (
            UPLOAD_DIR
            / safe_filename
        )

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
# 17. Chatbot
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
        # البحث عن أي Chatbot موجود فعليًا
        # ----------------------------------------------------

        chatbot_response = None

        try:

            import services

            # ------------------------------------------------
            # لا نفترض وجود services.chatbot
            # ------------------------------------------------

            if hasattr(
                services,
                "chat"
            ):

                chatbot_response = (
                    services.chat(
                        message
                    )
                )

        except Exception as chatbot_error:

            print(
                "Optional chatbot service error:",
                str(chatbot_error)
            )

        # ----------------------------------------------------
        # الرد الاحتياطي
        # ----------------------------------------------------

        if chatbot_response is None:

            chatbot_response = (

                "مرحباً بك في SMARTSTOCK AI. "

                "يمكنني مساعدتك في إدارة المخزون، "

                "التنبؤ بالطلب، "

                "تحليل المنتجات، "

                "المبيعات والمخاطر."
            )

        return {

            "success": True,

            "message":
                message,

            "response":
                chatbot_response
        }

    except Exception as e:

        print(
            "CHATBOT ERROR"
        )

        print(
            "Error:",
            str(e)
        )

        traceback.print_exc()

        return {

            "success": False,

            "error":
                str(e),

            "error_type":
                type(e).__name__
        }


# ============================================================
# 18. Square Test
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

            "connected": True,

            "locations":
                locations,

            "count":
                len(locations)
        }

    except Exception as e:

        print(
            "SQUARE TEST ERROR"
        )

        traceback.print_exc()

        return {

            "success": False,

            "connected": False,

            "error":
                str(e),

            "error_type":
                type(e).__name__
        }


# ============================================================
# 19. Square Locations
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

        print(
            "SQUARE LOCATIONS ERROR"
        )

        traceback.print_exc()

        return {

            "success": False,

            "error":
                str(e),

            "error_type":
                type(e).__name__
        }


# ============================================================
# 20. Square Catalog
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
                        getattr(
                            obj,
                            "id",
                            None
                        ),

                    "type":
                        getattr(
                            obj,
                            "type",
                            None
                        )
                }

                # --------------------------------------------
                # Item data
                # --------------------------------------------

                if hasattr(
                    obj,
                    "item_data"
                ):

                    item[
                        "item_data"
                    ] = str(
                        obj.item_data
                    )

                # --------------------------------------------
                # Variation data
                # --------------------------------------------

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

        print(
            "SQUARE CATALOG ERROR"
        )

        traceback.print_exc()

        return {

            "success": False,

            "error":
                str(e),

            "error_type":
                type(e).__name__
        }


# ============================================================
# 21. Square Inventory
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

        # ----------------------------------------------------
        # جلب عناصر الكتالوج أولاً
        # ----------------------------------------------------

        catalog_response = (
            square_client.catalog.list()
        )

        catalog_ids = []

        if hasattr(
            catalog_response,
            "objects"
        ):

            for obj in catalog_response.objects:

                if getattr(
                    obj,
                    "type",
                    None
                ) == "ITEM_VARIATION":

                    catalog_ids.append(
                        obj.id
                    )

        # ----------------------------------------------------
        # إذا لم توجد منتجات
        # ----------------------------------------------------

        if not catalog_ids:

            return {

                "success": True,

                "count": 0,

                "inventory": []
            }

        # ----------------------------------------------------
        # جلب المخزون
        # ----------------------------------------------------

        response = (
            square_client.inventory
            .batch_retrieve_inventory_counts(
                catalog_object_ids=
                    catalog_ids
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
                        getattr(
                            count,
                            "catalog_object_id",
                            None
                        ),

                    "state":
                        getattr(
                            count,
                            "state",
                            None
                        ),

                    "quantity":
                        getattr(
                            count,
                            "quantity",
                            None
                        ),

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

        print(
            "SQUARE INVENTORY ERROR"
        )

        traceback.print_exc()

        return {

            "success": False,

            "error":
                str(e),

            "error_type":
                type(e).__name__
        }


# ============================================================
# 22. Square Orders
# ============================================================

@app.get("/square/orders")
def square_orders():

    if square_client is None:

        return {

            "success": False,

            "error":
                "Square client is not configured."
        }

    try:

        response = (
            square_client.orders.search(
                body={
                    "location_ids": [
                        LOCATION_ID
                    ]
                }
            )
        )

        orders = []

        if hasattr(
            response,
            "orders"
        ):

            for order in response.orders:

                orders.append({

                    "id":
                        getattr(
                            order,
                            "id",
                            None
                        ),

                    "state":
                        getattr(
                            order,
                            "state",
                            None
                        ),

                    "created_at":
                        getattr(
                            order,
                            "created_at",
                            None
                        ),

                    "updated_at":
                        getattr(
                            order,
                            "updated_at",
                            None
                        )
                })

        return {

            "success": True,

            "count":
                len(orders),

            "orders":
                orders
        }

    except Exception as e:

        print(
            "SQUARE ORDERS ERROR"
        )

        traceback.print_exc()

        return {

            "success": False,

            "error":
                str(e),

            "error_type":
                type(e).__name__
        }


# ============================================================
# 23. API Information
# ============================================================

@app.get("/api/info")
def api_info():

    return {

        "name":
            "SMARTSTOCK AI",

        "version":
            "1.0.0",

        "status":
            "running",

        "endpoints": {

            "health":
                "/health",

            "dashboard":
                "/dashboard/summary",

            "demand_predict":
                "/demand/predict",

            "demand_results":
                "/demand/results",

            "image_info":
                "/image/info",

            "image_upload":
                "/image/upload",

            "chat":
                "/chat",

            "square_test":
                "/square/test",

            "square_locations":
                "/square/locations",

            "square_catalog":
                "/square/catalog",

            "square_inventory":
                "/square/inventory",

            "square_orders":
                "/square/orders"
        }
    }


# ============================================================
# 24. Global Exception Handler
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
# 25. Local Run
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