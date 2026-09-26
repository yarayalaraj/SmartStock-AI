
# ============================================================
# SmartStock AI
# Transformer Chatbot Service
#
# وظيفة هذا الملف:
#
# 1. تحميل Transformer Model.
# 2. استقبال سؤال المستخدم.
# 3. تحديد نوع السؤال.
# 4. تشغيل Transformer لمعالجة السؤال وتوليد استجابة أولية.
# 5. استخراج المعلومات الحقيقية من بيانات SmartStock.
# 5. استخراج المعلومات الحقيقيpython -c "from services.models.chatbot_service import detect_question_type; print(detect_question_type('ما مخاطر المخزون؟')ة من بيانات SmartStock.
# 6. بناء إجابة factual دقيقة من بيانات النظام.
# 7. استخدام Transformer للأسئلة العامة عندما يكون ذلك مناسبًا.
#
# النموذج:
# google/flan-t5-small
#
# Image AI النهائي:
# MobileNetV2
#
# ملاحظة مهمة:
# Transformer لا يتم الاعتماد عليه لإنتاج أرقام المخزون أو
# نتائج النماذج، لأن النموذج الصغير قد ينتج إجابة غير دقيقة
# عند التعامل مع الأرقام.
#
# لذلك:
#
# Transformer = NLP / Language Processing
# SmartStock Data = مصدر الحقيقة للأرقام والنتائج
#
# ============================================================


# ============================================================
# 1. IMPORTS
# ============================================================

import os
import re

import pandas as pd


# ============================================================
# 2. PROJECT PATHS
# ============================================================

# استخدام Path بشكل ديناميكي بدل المسار الثابت الخاص بجهاز Windows.
#
# هذا يجعل المشروع يعمل:
# - على Windows
# - على Render Linux
# - داخل PyCharm
# - داخل GitHub
#
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]


# ملف تحليل المخزون والمخاطر
INVENTORY_RISK_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "inventory_expiry_risk_analysis.csv"
)


# ملف نتائج نماذج التنبؤ بالطلب
DEMAND_RESULTS_FILE = (
    PROJECT_ROOT
    / "models"
    / "demand_model_results.csv"
)


# Transformer
MODEL_NAME = "google/flan-t5-small"


# ============================================================
# 3. GLOBAL VARIABLES
# ============================================================

# يتم تحميل Transformer عند أول استخدام فقط.
#
# لا يتم تحميل النموذج عند تشغيل FastAPI.
#
tokenizer = None
model = None


# ============================================================
# 4. LOAD TRANSFORMER MODEL
# ============================================================

def load_chatbot_model():
    """
    تحميل Transformer Model مرة واحدة فقط.

    Lazy Loading:
    لا يتم تحميل النموذج عند تشغيل FastAPI،
    وإنما عند أول استخدام للـ Chatbot.

    PyTorch و Transformers يتم استيرادهما هنا فقط
    حتى لا يستهلك FastAPI الذاكرة عند Startup.
    """

    global tokenizer
    global model

    # إذا كان النموذج محملًا مسبقًا فلا نعيد تحميله.
    if tokenizer is not None and model is not None:
        return

    # ========================================================
    # Lazy Imports
    # ========================================================

    import torch

    from transformers import (
        AutoTokenizer,
        AutoModelForSeq2SeqLM
    )

    print("=" * 70)
    print("LOADING TRANSFORMER CHATBOT")
    print("=" * 70)

    print(f"Model: {MODEL_NAME}")

    # --------------------------------------------------------
    # تحميل Tokenizer
    # --------------------------------------------------------

    tokenizer = AutoTokenizer.from_pretrained(
        MODEL_NAME
    )

    # --------------------------------------------------------
    # تحميل Transformer
    # --------------------------------------------------------

    model = AutoModelForSeq2SeqLM.from_pretrained(
        MODEL_NAME
    )

    # --------------------------------------------------------
    # تشغيل النموذج على CPU
    # --------------------------------------------------------

    model.to(
        torch.device("cpu")
    )

    # --------------------------------------------------------
    # وضع Evaluation
    # --------------------------------------------------------

    model.eval()

    print(
        "Transformer chatbot loaded successfully."
    )


# ============================================================
# 5. LOAD INVENTORY DATA
# ============================================================

def load_inventory_data():
    """
    قراءة بيانات المخزون والمخاطر.

    المصدر الأساسي:
    UCI Stock Keeping Units Dataset

    الملف المستخدم بعد المعالجة:
    inventory_expiry_risk_analysis.csv
    """

    if not INVENTORY_RISK_FILE.exists():
        return None

    try:

        df = pd.read_csv(
            INVENTORY_RISK_FILE
        )

        return df

    except Exception as error:

        print(
            "Error loading inventory data:",
            error
        )

        return None


# ============================================================
# 6. LOAD DEMAND RESULTS
# ============================================================

def load_demand_results():
    """
    قراءة نتائج نماذج التنبؤ بالطلب.
    """

    if not DEMAND_RESULTS_FILE.exists():
        return None

    try:

        df = pd.read_csv(
            DEMAND_RESULTS_FILE
        )

        return df

    except Exception as error:

        print(
            "Error loading demand results:",
            error
        )

        return None


# ============================================================
# 7. FIND COLUMN
# ============================================================

def find_column(
    df,
    possible_columns
):
    """
    البحث عن أول عمود موجود من قائمة أسماء محتملة.
    """

    if df is None:
        return None

    for column in possible_columns:

        if column in df.columns:
            return column

    return None


# ============================================================
# 8. GET INVENTORY SUMMARY
# ============================================================

def get_inventory_summary():
    """
    إنشاء ملخص عن المخزون.
    """

    df = load_inventory_data()

    if df is None or df.empty:

        return (
            "No inventory data is currently available."
        )

    summary = []

    # --------------------------------------------------------
    # عدد المنتجات
    # --------------------------------------------------------

    summary.append(
        f"Total products in inventory analysis: {len(df)}"
    )

    # --------------------------------------------------------
    # Risk Level
    # --------------------------------------------------------

    risk_column = find_column(
        df,
        [
            "inventory_expiry_risk_level",
            "Risk_Level",
            "risk_level",
            "Risk Level"
        ]
    )

    if risk_column is not None:

        risk_counts = (
            df[risk_column]
            .value_counts()
            .to_dict()
        )

        summary.append(
            "Risk distribution:"
        )

        for risk_name in [
            "Low",
            "Medium",
            "High"
        ]:

            summary.append(
                f"{risk_name}: "
                f"{risk_counts.get(risk_name, 0)}"
            )

    # --------------------------------------------------------
    # Average Shelf Life
    # --------------------------------------------------------

    shelf_column = find_column(
        df,
        [
            "avg_shelf_life_days",
            "shelf_life_days",
            "Expire date"
        ]
    )

    if shelf_column is not None:

        shelf_values = pd.to_numeric(
            df[shelf_column],
            errors="coerce"
        )

        average_shelf_life = (
            shelf_values.mean()
        )

        if pd.notna(
            average_shelf_life
        ):

            summary.append(
                "Average shelf life: "
                f"{average_shelf_life:.1f} days"
            )

    return "\n".join(
        summary
    )


# ============================================================
# 9. GET RISK SUMMARY
# ============================================================

def get_risk_summary():
    """
    استخراج معلومات المخاطر من البيانات الحقيقية.
    """

    df = load_inventory_data()

    if df is None or df.empty:

        return (
            "No inventory risk data is currently available."
        )

    summary = []

    # --------------------------------------------------------
    # Risk Level
    # --------------------------------------------------------

    risk_column = find_column(
        df,
        [
            "inventory_expiry_risk_level",
            "Risk_Level",
            "risk_level",
            "Risk Level"
        ]
    )

    if risk_column is not None:

        counts = (
            df[risk_column]
            .value_counts()
            .to_dict()
        )

        summary.append(
            "Risk distribution:"
        )

        for risk in [
            "Low",
            "Medium",
            "High"
        ]:

            summary.append(
                f"- {risk}: "
                f"{counts.get(risk, 0)}"
            )

    # --------------------------------------------------------
    # Risk Score
    # --------------------------------------------------------

    score_column = find_column(
        df,
        [
            "inventory_expiry_risk_score",
            "Risk_Score",
            "risk_score"
        ]
    )

    if score_column is not None:

        scores = pd.to_numeric(
            df[score_column],
            errors="coerce"
        ).dropna()

        if not scores.empty:

            summary.append(
                f"Average risk score: "
                f"{scores.mean():.2f}"
            )

            summary.append(
                f"Maximum risk score: "
                f"{scores.max():.2f}"
            )

    return "\n".join(
        summary
    )


# ============================================================
# 10. DETECT QUESTION TYPE
# ============================================================

def detect_question_type(question):
    """
    تحديد نوع السؤال.

    الأنواع:

    inventory
    risk
    demand
    image
    general

    يتم إعطاء risk أولوية على inventory،
    لأن السؤال قد يحتوي كلمة "مخزون" وكلمة "مخاطر"
    في نفس الوقت.
    """

    question_lower = str(
        question
    ).lower()

    # ========================================================
    # Risk
    # ========================================================

    risk_keywords = [
        "خطر",
        "مخاطر",
        "risk",
        "risk level",
        "risk score",
        "expiry risk",
        "expiration risk",
        "expired",
        "انتهاء المخاطر",
        "مخاطر الصلاحية",
        "عالية المخاطر",
        "مرتفع المخاطر",
        "متوسطة المخاطر",
        "متوسط المخاطر",
        "منخفضة المخاطر",
        "منخفض المخاطر",
        "low risk",
        "medium risk",
        "high risk"
    ]

    if any(
        keyword in question_lower
        for keyword in risk_keywords
    ):

        return "risk"

    # ========================================================
    # Demand / Sales
    # ========================================================

    demand_keywords = [
        "طلب",
        "التنبؤ بالطلب",
        "المبيعات",
        "مبيعات",
        "demand",
        "sales",
        "بيع",
        "sold",
        "units sold",
        "random forest",
        "mae",
        "rmse",
        "r2",
        "r²"
    ]

    if any(
        keyword in question_lower
        for keyword in demand_keywords
    ):

        return "demand"

    # ========================================================
    # Image / Waste Classification
    # ========================================================

    image_keywords = [
        "صورة",
        "تصنيف الصور",
        "تصنيف",
        "نفايات",
        "image",
        "classification",
        "waste",
        "mobilenet",
        "realwaste",
        "صور"
    ]

    if any(
        keyword in question_lower
        for keyword in image_keywords
    ):

        return "image"

    # ========================================================
    # Inventory
    # ========================================================

    inventory_keywords = [
        "مخزون",
        "المخزون",
        "inventory",
        "stock",
        "products",
        "products in inventory",
        "عدد المنتجات",
        "صلاحية",
        "مدة الصلاحية",
        "shelf life",
        "shelf",
        "expire",
        "expiration date"
    ]

    if any(
        keyword in question_lower
        for keyword in inventory_keywords
    ):

        return "inventory"

    return "general"


# ============================================================
# 11. BUILD COMPACT CONTEXT
# ============================================================

def build_system_context(question):
    """
    بناء Context صغير ومحدد.

    لا نرسل كامل ملفات CSV إلى Transformer.
    """

    question_type = detect_question_type(
        question
    )

    context_parts = []

    # ========================================================
    # Inventory
    # ========================================================

    if question_type in [
        "inventory",
        "general"
    ]:

        context_parts.append(
            "INVENTORY INFORMATION:\n"
            + get_inventory_summary()
        )

    # ========================================================
    # Risk
    # ========================================================

    if question_type in [
        "risk",
        "inventory",
        "general"
    ]:

        context_parts.append(
            "RISK INFORMATION:\n"
            + get_risk_summary()
        )

    # ========================================================
    # Demand
    # ========================================================

    if question_type in [
        "demand",
        "general"
    ]:

        demand_df = load_demand_results()

        if (
            demand_df is not None
            and not demand_df.empty
        ):

            # نرسل عددًا محدودًا من المعلومات.
            #
            # لا نرسل DataFrame ضخم إلى Transformer.
            limited_demand = demand_df.head(10)

            context_parts.append(
                "DEMAND MODEL INFORMATION:\n"
                + limited_demand.to_string(
                    index=False
                )
            )

        else:

            context_parts.append(
                "No demand model results are available."
            )

    # ========================================================
    # Image
    # ========================================================

    if question_type == "image":

        context_parts.append(
            "IMAGE AI INFORMATION:\n"
            "Model: MobileNetV2\n"
            "Dataset: RealWaste\n"
            "Number of classes: 9\n"
            "Test accuracy: 78.82%\n"
            "Classes: Cardboard, Food Organics, Glass, "
            "Metal, Miscellaneous Trash, Paper, Plastic, "
            "Textile Trash, Vegetation."
        )

    return "\n\n".join(
        context_parts
    )


# ============================================================
# 12. GET DEMAND MODEL FACTS
# ============================================================

def get_demand_facts():
    """
    استخراج الحقائق الفعلية من ملف نتائج نماذج الطلب.
    """

    df = load_demand_results()

    if df is None or df.empty:

        return None

    facts = {}

    # --------------------------------------------------------
    # البحث عن أسماء الأعمدة
    # --------------------------------------------------------

    model_column = find_column(
        df,
        [
            "Model",
            "model",
            "Model Name",
            "model_name"
        ]
    )

    r2_column = find_column(
        df,
        [
            "R2",
            "R²",
            "r2",
            "R-squared"
        ]
    )

    mae_column = find_column(
        df,
        [
            "MAE",
            "mae"
        ]
    )

    rmse_column = find_column(
        df,
        [
            "RMSE",
            "rmse"
        ]
    )

    # --------------------------------------------------------
    # استخراج معلومات Random Forest
    # --------------------------------------------------------

    if model_column is not None:

        models = (
            df[model_column]
            .astype(str)
            .tolist()
        )

        facts["models"] = models

        for index, model_name in enumerate(
            models
        ):

            if "random forest" in model_name.lower():

                row = df.iloc[index]

                if r2_column is not None:

                    try:

                        facts["random_forest_r2"] = float(
                            row[r2_column]
                        )

                    except (
                        ValueError,
                        TypeError
                    ):

                        pass

                if mae_column is not None:

                    try:

                        facts["random_forest_mae"] = float(
                            row[mae_column]
                        )

                    except (
                        ValueError,
                        TypeError
                    ):

                        pass

                if rmse_column is not None:

                    try:

                        facts["random_forest_rmse"] = float(
                            row[rmse_column]
                        )

                    except (
                        ValueError,
                        TypeError
                    ):

                        pass

                break

    return facts


# ============================================================
# 13. CREATE FACTUAL RESPONSE
# ============================================================

def create_factual_fallback(question):
    """
    إنشاء إجابة مباشرة من بيانات SmartStock.

    هذه الدالة هي مصدر الحقيقة للأرقام.
    """

    question_lower = str(
        question
    ).lower()

    question_type = detect_question_type(
        question
    )

    df = load_inventory_data()

    # ========================================================
    # RISK
    # ========================================================

    if question_type == "risk":

        if df is None or df.empty:

            return (
                "لا توجد بيانات المخاطر متاحة حاليًا."
            )

        risk_column = find_column(
            df,
            [
                "inventory_expiry_risk_level",
                "Risk_Level",
                "risk_level",
                "Risk Level"
            ]
        )

        if risk_column is None:

            return (
                "بيانات مستويات المخاطر غير متاحة حاليًا."
            )

        counts = (
            df[risk_column]
            .value_counts()
            .to_dict()
        )

        low = counts.get(
            "Low",
            0
        )

        medium = counts.get(
            "Medium",
            0
        )

        high = counts.get(
            "High",
            0
        )

        total = len(df)

        # ----------------------------------------------------
        # سؤال عن فئة معينة
        # ----------------------------------------------------

        if (
            "high risk" in question_lower
            or "عالية المخاطر" in question_lower
            or "مرتفع المخاطر" in question_lower
            or "مرتفع" in question_lower
        ):

            return (
                f"يوجد {high} منتجًا ضمن فئة "
                f"المخاطر المرتفعة من أصل {total} منتجًا."
            )

        if (
            "medium risk" in question_lower
            or "متوسطة المخاطر" in question_lower
            or "متوسط المخاطر" in question_lower
        ):

            return (
                f"يوجد {medium} منتجًا ضمن فئة "
                f"المخاطر المتوسطة من أصل {total} منتجًا."
            )

        if (
            "low risk" in question_lower
            or "منخفضة المخاطر" in question_lower
            or "منخفض المخاطر" in question_lower
        ):

            return (
                f"يوجد {low} منتجًا ضمن فئة "
                f"المخاطر المنخفضة من أصل {total} منتجًا."
            )

        # ----------------------------------------------------
        # التوزيع الكامل
        # ----------------------------------------------------

        return (
            f"توزيع مخاطر المخزون في SmartStock: "
            f"{low} منتج منخفض المخاطر، "
            f"{medium} منتج متوسط المخاطر، "
            f"و{high} منتج مرتفع المخاطر، "
            f"من إجمالي {total} منتجًا."
        )

    # ========================================================
    # INVENTORY
    # ========================================================

    if question_type == "inventory":

        if df is None or df.empty:

            return (
                "لا توجد بيانات مخزون متاحة حاليًا."
            )

        total_products = len(df)

        # ----------------------------------------------------
        # Shelf life
        # ----------------------------------------------------

        shelf_column = find_column(
            df,
            [
                "avg_shelf_life_days",
                "shelf_life_days",
                "Expire date"
            ]
        )

        if (
            "shelf" in question_lower
            or "shelf life" in question_lower
            or "صلاحية" in question_lower
            or "مدة الصلاحية" in question_lower
            or "expire" in question_lower
        ):

            if shelf_column is not None:

                values = pd.to_numeric(
                    df[shelf_column],
                    errors="coerce"
                )

                average = values.mean()

                if pd.notna(average):

                    return (
                        f"متوسط مدة الصلاحية في بيانات "
                        f"SmartStock هو {average:.1f} يومًا."
                    )

        return (
            f"يحتوي تحليل المخزون في SmartStock "
            f"على {total_products} منتجًا."
        )

    # ========================================================
    # DEMAND
    # ========================================================

    if question_type == "demand":

        facts = get_demand_facts()

        if facts is None:

            return (
                "لا توجد نتائج متاحة لنموذج التنبؤ بالطلب حاليًا."
            )

        # ----------------------------------------------------
        # السؤال عن Random Forest
        # ----------------------------------------------------

        if (
            "random forest" in question_lower
            or "أفضل نموذج" in question_lower
            or "best model" in question_lower
            or "النموذج المستخدم" in question_lower
        ):

            answer = (
                "النموذج المختار للتنبؤ بالطلب في SmartStock "
                "هو Random Forest Regressor."
            )

            if "random_forest_r2" in facts:

                answer += (
                    f" قيمة R² هي "
                    f"{facts['random_forest_r2']:.4f}."
                )

            if "random_forest_mae" in facts:

                answer += (
                    f" وقيمة MAE هي "
                    f"{facts['random_forest_mae']:.4f}."
                )

            if "random_forest_rmse" in facts:

                answer += (
                    f" وقيمة RMSE هي "
                    f"{facts['random_forest_rmse']:.4f}."
                )

            return answer

        return (
            "نموذج التنبؤ بالطلب في SmartStock "
            "هو Random Forest Regressor، "
            "ويستخدم لتقدير Units Sold اعتمادًا "
            "على بيانات السعر والمتجر والخصم."
        )

    # ========================================================
    # IMAGE AI
    # ========================================================

    if question_type == "image":

        return (
            "نموذج تصنيف الصور النهائي في SmartStock "
            "هو MobileNetV2. تم تدريبه على مجموعة RealWaste "
            "التي تحتوي على 9 فئات، وحقق دقة اختبار قدرها "
            "78.82%."
        )

    # ========================================================
    # GENERAL
    # ========================================================

    if df is not None and not df.empty:

        return (
            f"SmartStock AI يحتوي على "
            f"{len(df)} منتجًا في بيانات تحليل المخزون. "
            f"يمكنني مساعدتك في المخزون، المخاطر، "
            f"التنبؤ بالطلب، وتصنيف الصور."
        )

    return (
        "لا تتوفر معلومات كافية للإجابة عن السؤال حاليًا."
    )


# ============================================================
# 14. CLEAN RESPONSE
# ============================================================

def clean_response(response):
    """
    تنظيف النص الناتج من Transformer.
    """

    if response is None:
        return ""

    response = str(
        response
    ).strip()

    response = re.sub(
        r"\s+",
        " ",
        response
    )

    return response


# ============================================================
# 15. CHECK RESPONSE
# ============================================================

def is_useful_response(response):
    """
    فحص إجابة Transformer.

    هذه الدالة تمنع استخدام الإجابات الواضحة
    بأنها غير مفيدة.
    """

    if not response:
        return False

    normalized = response.strip()

    # --------------------------------------------------------
    # رقم فقط
    # --------------------------------------------------------

    if re.fullmatch(
        r"[\d.,%]+",
        normalized
    ):
        return False

    # --------------------------------------------------------
    # إجابات عامة جدًا
    # --------------------------------------------------------

    useless_answers = [
        "yes",
        "no",
        "نعم",
        "لا",
        "low risk",
        "medium risk",
        "high risk",
        "inventory",
        "risk",
        "expenses"
    ]

    if normalized.lower() in useless_answers:
        return False

    # --------------------------------------------------------
    # إجابة قصيرة جدًا
    # --------------------------------------------------------

    if len(normalized) < 8:
        return False

    return True


# ============================================================
# 16. RUN TRANSFORMER
# ============================================================

def run_transformer(
    question,
    context,
    max_new_tokens=80
):
    """
    تشغيل Transformer وإرجاع الإجابة الأولية.

    هذه الدالة موجودة للحفاظ على دور Transformer
    داخل النظام.

    لا نعتبر الناتج مصدرًا موثوقًا للأرقام.

    PyTorch يتم تحميله هنا فقط عند استخدام Transformer.
    """

    # ========================================================
    # Lazy Import
    # ========================================================

    import torch

    # تحميل النموذج عند أول استخدام
    load_chatbot_model()

    # ========================================================
    # بناء Prompt
    # ========================================================

    prompt = f"""
You are an assistant for SmartStock AI.

Use the provided context to understand the question.
Do not invent facts.

Context:
{context}

Question:
{question}

Give a short answer.
"""

    # ========================================================
    # Tokenization
    # ========================================================

    inputs = tokenizer(
        prompt,
        return_tensors="pt",
        truncation=True,
        max_length=768
    )

    # ========================================================
    # Generate
    # ========================================================

    with torch.no_grad():

        outputs = model.generate(
            **inputs,
            max_new_tokens=max_new_tokens,
            num_beams=4,
            early_stopping=True,
            no_repeat_ngram_size=2
        )

    # ========================================================
    # Decode
    # ========================================================

    response = tokenizer.decode(
        outputs[0],
        skip_special_tokens=True
    )

    return clean_response(
        response
    )


# ============================================================
# 17. GENERATE RESPONSE
# ============================================================

def generate_response(
    question,
    max_new_tokens=80
):
    """
    الدالة الرئيسية للـ Chatbot.

    Architecture:

    User Question
          ↓
    Question Detection
          ↓
    Transformer
          ↓
    SmartStock Data
          ↓
    Factual Answer
    """

    # ========================================================
    # تنظيف السؤال
    # ========================================================

    if question is None:

        return (
            "من فضلك اكتب سؤالك."
        )

    question = str(
        question
    ).strip()

    if not question:

        return (
            "من فضلك اكتب سؤالك."
        )

    # ========================================================
    # تحديد نوع السؤال
    # ========================================================

    question_type = detect_question_type(
        question
    )

    # ========================================================
    # Context
    # ========================================================

    context = build_system_context(
        question
    )

    # ========================================================
    # تشغيل Transformer
    # ========================================================

    try:

        transformer_response = run_transformer(
            question,
            context,
            max_new_tokens=max_new_tokens
        )

        print(
            "Transformer raw response:",
            transformer_response
        )

    except Exception as error:

        print(
            "Transformer generation error:",
            error
        )

        transformer_response = ""

    # ========================================================
    # أسئلة SmartStock
    #
    # نستخدم الإجابة factual المباشرة من البيانات.
    #
    # FLAN-T5-small ليس مصدرًا موثوقًا للأرقام.
    # ========================================================

    if question_type in [
        "inventory",
        "risk",
        "demand",
        "image"
    ]:

        return create_factual_fallback(
            question
        )

    # ========================================================
    # الأسئلة العامة
    #
    # إذا كانت إجابة Transformer مفيدة نستخدمها.
    # وإلا نستخدم fallback.
    # ========================================================

    if is_useful_response(
        transformer_response
    ):

        return transformer_response

    return create_factual_fallback(
        question
    )


# ============================================================
# 18. TEST CHATBOT
# ============================================================

if __name__ == "__main__":

    print("\n")
    print("=" * 70)
    print("SMARTSTOCK AI - TRANSFORMER CHATBOT TEST")
    print("=" * 70)

    test_questions = [
        "What is the current inventory risk distribution?",
        "كم عدد المنتجات عالية المخاطر؟",
        "ما متوسط مدة الصلاحية؟",
        "ما أفضل نموذج للتنبؤ بالطلب؟",
        "ما دقة نموذج تصنيف الصور؟"
    ]

    for question in test_questions:

        print("\n")
        print("-" * 70)

        print("User:")
        print(question)

        print("\nAssistant:")

        answer = generate_response(
            question
        )

        print(answer)

    print("\n")
    print("=" * 70)
    print("CHATBOT TEST COMPLETED")
    print("=" * 70)

