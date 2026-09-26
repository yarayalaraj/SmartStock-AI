# ============================================================
# SmartStock AI
# واجهة احترافية باستخدام Streamlit فقط
# بدون HTML مخصص حتى لا يظهر أي كود للمستخدم
# ============================================================

import requests
import pandas as pd
import streamlit as st


# ============================================================
# 1. إعداد الصفحة
# ============================================================

st.set_page_config(
    page_title="SmartStock AI",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# 2. إعدادات النظام
# ============================================================

import os

API_BASE_URL = os.getenv(
    "API_BASE_URL",
    "http://127.0.0.1:8000"
)


# ============================================================
# 3. Session State
# ============================================================

if "theme" not in st.session_state:
    st.session_state.theme = "light"

if "page" not in st.session_state:
    st.session_state.page = "الرئيسية"

if "chat_messages" not in st.session_state:
    st.session_state.chat_messages = []


# ============================================================
# 4. CSS بسيط وآمن
# ============================================================
# نستخدم CSS فقط للتنسيق، ولا نستخدم HTML داخل محتوى الصفحة.
# ============================================================

if st.session_state.theme == "dark":

    background = "#0E1525"
    card = "#172033"
    text = "#F8FAFC"
    muted = "#A7B1C2"
    border = "#28364D"

else:

    background = "#F5F7FB"
    card = "#FFFFFF"
    text = "#172033"
    muted = "#667085"
    border = "#E4E8EF"


st.markdown(
    f"""
    <style>

    .stApp {{
        background-color: {background};
    }}

    [data-testid="stSidebar"] {{
        background-color: #0B1728;
    }}

    [data-testid="stSidebar"] * {{
        color: #E8EEF7;
    }}

    .block-container {{
        max-width: 1450px;
        padding-top: 2rem;
        padding-bottom: 3rem;
    }}

    div[data-testid="stMetric"] {{
        background-color: {card};
        border: 1px solid {border};
        border-radius: 16px;
        padding: 18px;
    }}

    div[data-testid="stMetric"] label {{
        color: {muted};
    }}

    div[data-testid="stMetricValue"] {{
        color: {text};
    }}

    .stDataFrame {{
        border-radius: 12px;
    }}

    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# 5. الاتصال بالـBackend
# ============================================================

def get_api(endpoint, params=None):

    try:

        response = requests.get(
            f"{API_BASE_URL}{endpoint}",
            params=params,
            timeout=15,
        )

        if response.status_code == 200:

            return response.json()

        return {
            "success": False,
            "error": f"HTTP {response.status_code}",
        }

    except requests.exceptions.RequestException as error:

        return {
            "success": False,
            "error": str(error),
        }


def post_api(endpoint, json_data=None, files=None):

    try:

        response = requests.post(
            f"{API_BASE_URL}{endpoint}",
            json=json_data,
            files=files,
            timeout=120,
        )

        if response.status_code == 200:

            return response.json()

        return {
            "success": False,
            "error": f"HTTP {response.status_code}",
        }

    except requests.exceptions.RequestException as error:

        return {
            "success": False,
            "error": str(error),
        }


# ============================================================
# 6. اختبار Backend
# ============================================================

health = get_api("/health")

# مهم:
# /health عندك يرجع:
#
# {
#     "status": "healthy",
#     ...
# }
#
# وليس:
#
# {
#     "success": true
# }
#
# لذلك لا نستخدم health.get("success").

backend_connected = (
    health.get("status") == "healthy"
)


# ============================================================
# 7. Sidebar
# ============================================================

with st.sidebar:

    st.markdown("## 📦 SmartStock AI")

    st.caption(
        "Intelligent Inventory Platform"
    )

    st.divider()

    st.markdown("### WORKSPACE")

    page_options = [
        "🏠 الرئيسية",
        "📦 إدارة المخزون",
        "📈 تحليل الطلب",
        "⚠️ مخاطر المخزون",
        "🖼️ تحليل الصور",
        "🧾 المبيعات",
        "🤖 المساعد الذكي",
        "ℹ️ حول النظام",
    ]

    selected_page = st.radio(
        "التنقل",
        page_options,
        label_visibility="collapsed",
    )

    st.divider()

    st.markdown("### APPEARANCE")

    dark_mode = st.toggle(
        "🌙 الوضع الداكن",
        value=(
            st.session_state.theme == "dark"
        ),
    )

    if dark_mode:
        st.session_state.theme = "dark"
    else:
        st.session_state.theme = "light"

    st.divider()

    if backend_connected:

        st.success(
            "Backend متصل"
        )

        st.caption(
            "FastAPI يعمل بشكل صحيح"
        )

    else:

        st.error(
            "Backend غير متصل"
        )

        st.caption(
            "تأكد من تشغيل FastAPI"
        )


# ============================================================
# 8. عنوان الصفحة
# ============================================================

page_titles = {

    "🏠 الرئيسية": (
        "لوحة التحكم",
        "نظرة شاملة على SmartStock AI",
    ),

    "📦 إدارة المخزون": (
        "إدارة المخزون",
        "متابعة المخزون الحالي من Square",
    ),

    "📈 تحليل الطلب": (
        "تحليل الطلب",
        "التنبؤ بالطلب باستخدام الذكاء الاصطناعي",
    ),

    "⚠️ مخاطر المخزون": (
        "مخاطر المخزون",
        "تحليل مخاطر المخزون ومدة الصلاحية",
    ),

    "🖼️ تحليل الصور": (
        "تحليل الصور",
        "تصنيف الصور باستخدام MobileNetV2",
    ),

    "🧾 المبيعات": (
        "المبيعات",
        "متابعة الطلبات من Square",
    ),

    "🤖 المساعد الذكي": (
        "المساعد الذكي",
        "مساعد SmartStock AI",
    ),

    "ℹ️ حول النظام": (
        "حول النظام",
        "معلومات عن المشروع والنماذج المستخدمة",
    ),
}


title, subtitle = page_titles[
    selected_page
]


st.title(title)
st.caption(subtitle)

if backend_connected:

    st.success(
        "● النظام متصل وجاهز للعمل",
        icon="🟢",
    )

else:

    st.error(
        "● تعذر الاتصال بالـBackend. شغّل FastAPI أولًا.",
        icon="🔴",
    )


# ============================================================
# 9. الرئيسية
# ============================================================

if selected_page == "🏠 الرئيسية":

    st.header(
        "إدارة المخزون الذكية"
    )

    st.write(
        """
        SmartStock AI هي منصة متكاملة تجمع إدارة المخزون،
        التنبؤ بالطلب، تحليل المخاطر، تحليل الصور والمساعد
        الذكي في نظام واحد.
        """
    )

    st.divider()

    # --------------------------------------------------------
    # الحصول على المخزون
    # --------------------------------------------------------

    inventory_response = get_api(
        "/inventory"
    )

    inventory_items = []

    total_units = 0

    if inventory_response.get("success"):

        inventory_items = (
            inventory_response.get(
                "data",
                [],
            )
        )

        for item in inventory_items:

            try:

                total_units += float(
                    item.get(
                        "quantity",
                        0,
                    )
                )

            except (
                TypeError,
                ValueError,
            ):

                pass

    # --------------------------------------------------------
    # الحصول على المخاطر
    # --------------------------------------------------------

    risk_response = get_api(
        "/inventory/risk/summary"
    )

    total_products = 0
    low_risk = 0
    medium_risk = 0
    high_risk = 0

    if risk_response.get("success"):

        total_products = risk_response.get(
            "total_products",
            0,
        )

        distribution = risk_response.get(
            "risk_distribution",
            {},
        )

        low_risk = distribution.get(
            "Low",
            0,
        )

        medium_risk = distribution.get(
            "Medium",
            0,
        )

        high_risk = distribution.get(
            "High",
            0,
        )

    # --------------------------------------------------------
    # KPI
    # --------------------------------------------------------

    c1, c2, c3, c4 = st.columns(4)

    with c1:

        st.metric(
            "📦 المنتجات المحللة",
            f"{total_products:,}",
        )

    with c2:

        st.metric(
            "🔢 الوحدات المتاحة",
            f"{total_units:g}",
        )

    with c3:

        st.metric(
            "🟠 مخاطر متوسطة",
            f"{medium_risk:,}",
        )

    with c4:

        st.metric(
            "🔴 مخاطر مرتفعة",
            f"{high_risk:,}",
        )

    st.divider()

    # --------------------------------------------------------
    # قسم المخزون
    # --------------------------------------------------------

    left, right = st.columns(
        [1.2, 1]
    )

    with left:

        st.subheader(
            "📦 المخزون الحالي"
        )

        st.caption(
            "بيانات مباشرة من Square"
        )

        if inventory_items:

            inventory_rows = []

            for item in inventory_items:

                quantity = item.get(
                    "quantity",
                    0,
                )

                state = item.get(
                    "state",
                    "",
                )

                object_id = item.get(
                    "catalog_object_id"
                )

                # المنتج الذي أنشأناه في Square
                if (
                    object_id
                    == "CHI74NB3HRW3WABQQJ2RUX42"
                ):

                    product_name = (
                        "SmartStock Coffee"
                    )

                else:

                    product_name = (
                        "منتج Square"
                    )

                if state == "IN_STOCK":

                    status = "متوفر"

                elif state == "OUT_OF_STOCK":

                    status = "غير متوفر"

                else:

                    status = (
                        state
                        or "غير محدد"
                    )

                inventory_rows.append(
                    {
                        "المنتج": product_name,
                        "الكمية": (
                            f"{quantity:g}"
                        ),
                        "الحالة": status,
                    }
                )

            inventory_df = pd.DataFrame(
                inventory_rows
            )

            st.dataframe(
                inventory_df,
                use_container_width=True,
                hide_index=True,
            )

        else:

            st.info(
                "لا توجد بيانات مخزون."
            )

    # --------------------------------------------------------
    # المخاطر
    # --------------------------------------------------------

    with right:

        st.subheader(
            "⚠️ توزيع المخاطر"
        )

        if total_products > 0:

            chart_df = pd.DataFrame(
                {
                    "المستوى": [
                        "منخفض",
                        "متوسط",
                        "مرتفع",
                    ],
                    "العدد": [
                        low_risk,
                        medium_risk,
                        high_risk,
                    ],
                }
            )

            st.bar_chart(
                chart_df.set_index(
                    "المستوى"
                )
            )

        else:

            st.info(
                "لا توجد بيانات مخاطر."
            )

    st.divider()

    st.subheader(
        "🧠 مكونات الذكاء الاصطناعي"
    )

    a, b, c, d = st.columns(4)

    with a:

        st.info(
            """
            ### 📈 تحليل الطلب

            **Random Forest**

            توقع الوحدات المتوقع بيعها.
            """
        )

    with b:

        st.warning(
            """
            ### ⚠️ المخاطر

            **K-Means**

            تحليل مخاطر المخزون.
            """
        )

    with c:

        st.info(
            """
            ### 🖼️ الصور

            **MobileNetV2**

            تصنيف الصور.
            """
        )

    with d:

        st.success(
            """
            ### 🤖 المساعد

            **Transformer**

            مساعد ذكي للمستخدم.
            """
        )

    with st.expander(
        "ⓘ كيف تعمل المنصة؟"
    ):

        st.write(
            """
            يتم دمج جميع مكونات النظام من خلال FastAPI.

            Square يوفر بيانات المخزون والمبيعات.

            نموذج Random Forest يستخدم للتنبؤ بالطلب.

            K-Means يستخدم لتحليل مجموعات المنتجات
            ومستويات المخاطر.

            MobileNetV2 يستخدم لتحليل الصور.

            Transformer يستخدم كمكون لغوي للمساعد الذكي.
            """
        )


# ============================================================
# 10. إدارة المخزون
# ============================================================

elif selected_page == "📦 إدارة المخزون":

    st.header(
        "📦 إدارة المخزون"
    )

    st.write(
        "عرض المخزون الحالي من Square Inventory API."
    )

    with st.expander(
        "ⓘ معلومات عن المخزون"
    ):

        st.write(
            """
            هذه الصفحة لا تستخدم كمية ثابتة.

            كل مرة يتم فتح الصفحة يتم طلب البيانات
            من FastAPI، وFastAPI يحصل عليها من
            Square Sandbox.
            """
        )

    response = get_api(
        "/inventory"
    )

    if response.get("success"):

        data = response.get(
            "data",
            [],
        )

        total_units = 0

        for item in data:

            try:

                total_units += float(
                    item.get(
                        "quantity",
                        0,
                    )
                )

            except (
                TypeError,
                ValueError,
            ):

                pass

        c1, c2, c3 = st.columns(3)

        with c1:

            st.metric(
                "عدد المنتجات",
                len(data),
            )

        with c2:

            st.metric(
                "إجمالي الوحدات",
                f"{total_units:g}",
            )

        with c3:

            st.metric(
                "المصدر",
                "Square",
            )

        st.divider()

        if data:

            rows = []

            for item in data:

                object_id = item.get(
                    "catalog_object_id"
                )

                if (
                    object_id
                    == "CHI74NB3HRW3WABQQJ2RUX42"
                ):

                    name = "SmartStock Coffee"

                else:

                    name = "منتج Square"

                quantity = item.get(
                    "quantity",
                    0,
                )

                state = item.get(
                    "state",
                    "",
                )

                if state == "IN_STOCK":

                    status = "متوفر"

                elif state == "OUT_OF_STOCK":

                    status = "غير متوفر"

                else:

                    status = (
                        state
                        or "غير محدد"
                    )

                rows.append(
                    {
                        "المنتج": name,
                        "الكمية": f"{quantity:g}",
                        "الحالة": status,
                    }
                )

            st.dataframe(
                pd.DataFrame(rows),
                use_container_width=True,
                hide_index=True,
            )

        else:

            st.info(
                "المخزون فارغ حاليًا."
            )

    else:

        st.error(
            response.get(
                "error",
                "تعذر جلب المخزون.",
            )
        )


# ============================================================
# 11. تحليل الطلب
# ============================================================

elif selected_page == "📈 تحليل الطلب":

    st.header(
        "📈 تحليل الطلب"
    )

    st.write(
        """
        توقع عدد الوحدات المتوقع بيعها باستخدام
        Random Forest Regressor.
        """
    )

    with st.expander(
        "ⓘ معلومات النموذج"
    ):

        st.write(
            """
            النموذج المختار: Random Forest Regressor

            R² = 0.6092

            MAE = 19.1346

            RMSE = 35.8088
            """
        )

    st.divider()

    c1, c2, c3 = st.columns(3)

    with c1:

        store_id = st.number_input(
            "رقم المتجر",
            min_value=1,
            value=1,
            step=1,
        )

    with c2:

        total_price = st.number_input(
            "السعر الحالي",
            min_value=0.0,
            value=350.0,
        )

    with c3:

        base_price = st.number_input(
            "السعر الأساسي",
            min_value=0.0,
            value=400.0,
        )

    if st.button(
        "🔮 توقع الطلب",
        type="primary",
        use_container_width=True,
    ):

        response = post_api(
            "/demand/predict",
            {
                "store_id": int(store_id),
                "total_price": float(
                    total_price
                ),
                "base_price": float(
                    base_price
                ),
            },
        )

        if response.get("success"):

            prediction = response.get(
                "prediction",
                0,
            )

            try:

                predicted_units = float(
                    prediction
                )

            except (
                TypeError,
                ValueError,
            ):

                predicted_units = 0.0

            st.success(
                "تم تنفيذ التنبؤ بنجاح."
            )

            c1, c2 = st.columns(2)

            with c1:

                st.metric(
                    "الطلب المتوقع",
                    f"{predicted_units:.2f} وحدة",
                )

            with c2:

                if predicted_units >= 100:

                    level = "مرتفع"

                elif predicted_units >= 30:

                    level = "متوسط"

                else:

                    level = "منخفض"

                st.metric(
                    "مستوى الطلب",
                    level,
                )

        else:

            st.error(
                response.get(
                    "error",
                    "حدث خطأ أثناء التنبؤ.",
                )
            )


# ============================================================
# 12. مخاطر المخزون
# ============================================================

elif selected_page == "⚠️ مخاطر المخزون":

    st.header(
        "⚠️ مخاطر المخزون"
    )

    st.write(
        """
        تحليل خصائص المنتجات باستخدام K-Means
        ودرجة مخاطر تحليلية.
        """
    )

    with st.expander(
        "ⓘ كيف يتم حساب المخاطر؟"
    ):

        st.write(
            """
            النظام يستخدم K-Means لتجميع المنتجات
            بناءً على خصائصها.

            ثم يتم حساب Risk Score شفاف يعتمد
            على مدة الصلاحية وحركة المنتج.

            هذه النتيجة ليست إثباتًا بأن المنتج
            تالف أو منتهي الصلاحية.
            """
        )

    response = get_api(
        "/inventory/risk/summary"
    )

    if response.get("success"):

        distribution = response.get(
            "risk_distribution",
            {},
        )

        total = response.get(
            "total_products",
            0,
        )

        c1, c2, c3, c4 = st.columns(4)

        with c1:

            st.metric(
                "إجمالي المنتجات",
                f"{total:,}",
            )

        with c2:

            st.metric(
                "🟢 منخفض",
                f"{distribution.get('Low', 0):,}",
            )

        with c3:

            st.metric(
                "🟠 متوسط",
                f"{distribution.get('Medium', 0):,}",
            )

        with c4:

            st.metric(
                "🔴 مرتفع",
                f"{distribution.get('High', 0):,}",
            )

    st.divider()

    risk_data = get_api(
        "/inventory/risk"
    )

    if risk_data.get("success"):

        data = risk_data.get(
            "data",
            [],
        )

        if data:

            df = pd.DataFrame(
                data
            )

            columns = {
                "ID": "رقم المنتج",
                "Unitprice": "سعر الوحدة",
                "Expire date": "مدة الصلاحية",
                "Outbound number": "عدد مرات الخروج",
                "Total outbound": "إجمالي الخروج",
                "inventory_expiry_risk_score": "درجة المخاطر",
                "inventory_expiry_risk_level": "مستوى المخاطر",
                "cluster": "المجموعة",
            }

            available_columns = [
                column
                for column in columns
                if column in df.columns
            ]

            df = df[
                available_columns
            ].rename(
                columns=columns
            )

            st.dataframe(
                df,
                use_container_width=True,
                hide_index=True,
            )


# ============================================================
# 13. تحليل الصور
# ============================================================

elif selected_page == "🖼️ تحليل الصور":

    st.header(
        "🖼️ تحليل الصور"
    )

    st.write(
        """
        تحليل وتصنيف الصور باستخدام MobileNetV2
        المدرب على RealWaste.
        """
    )

    info = get_api(
        "/image/info"
    )

    if info.get("success"):

        c1, c2, c3 = st.columns(3)

        with c1:

            st.metric(
                "دقة النموذج",
                info.get(
                    "accuracy_percentage",
                    "78.82%",
                ),
            )

        with c2:

            st.metric(
                "النموذج",
                info.get(
                    "model",
                    "MobileNetV2",
                ),
            )

        with c3:

            st.metric(
                "عدد الفئات",
                info.get(
                    "number_of_classes",
                    9,
                ),
            )

    with st.expander(
        "ⓘ معلومات عن النموذج"
    ):

        st.write(
            """
            النموذج النهائي هو MobileNetV2.

            Dataset: RealWaste

            عدد الفئات: 9

            Test Accuracy: 78.82%
            """
        )

    st.divider()

    uploaded_file = st.file_uploader(
        "اختر صورة للتحليل",
        type=[
            "jpg",
            "jpeg",
            "png",
            "webp",
        ],
    )

    if uploaded_file:

        st.image(
            uploaded_file,
            caption="الصورة المختارة",
            width=450,
        )

        if st.button(
            "🔍 تحليل الصورة",
            type="primary",
        ):

            files = {
                "file": (
                    uploaded_file.name,
                    uploaded_file.getvalue(),
                    uploaded_file.type,
                )
            }

            response = post_api(
                "/image/predict",
                files=files,
            )

            if response.get("success"):

                prediction = response.get(
                    "prediction",
                    {},
                )

                predicted_class = prediction.get(
                    "predicted_class",
                    "غير معروف",
                )

                confidence = prediction.get(
                    "confidence_percentage",
                    0,
                )

                st.success(
                    f"الفئة: {predicted_class}"
                )

                st.metric(
                    "درجة الثقة",
                    f"{float(confidence):.2f}%",
                )

            else:

                st.error(
                    response.get(
                        "error",
                        "تعذر تحليل الصورة.",
                    )
                )


# ============================================================
# 14. المبيعات
# ============================================================

elif selected_page == "🧾 المبيعات":

    st.header(
        "🧾 المبيعات"
    )

    st.write(
        "الطلبات الموجودة في Square Sandbox."
    )

    with st.expander(
        "ⓘ ملاحظة"
    ):

        st.write(
            """
            المشروع حاليًا يستخدم Square Sandbox
            لاختبار التكامل.

            لذلك هذه البيانات هي بيانات اختبار
            وليست مبيعات حقيقية لمتجر.
            """
        )

    response = get_api(
        "/sales"
    )

    if response.get("success"):

        data = response.get(
            "data",
            [],
        )

        if data:

            df = pd.DataFrame(
                data
            )

            st.dataframe(
                df,
                use_container_width=True,
                hide_index=True,
            )

        else:

            st.info(
                "لا توجد طلبات حاليًا."
            )

    else:

        st.error(
            response.get(
                "error",
                "تعذر تحميل المبيعات.",
            )
        )


# ============================================================
# 15. المساعد الذكي
# ============================================================

elif selected_page == "🤖 المساعد الذكي":

    st.header(
        "🤖 المساعد الذكي"
    )

    st.write(
        """
        اسأل SmartStock AI عن المخزون والطلب والمخاطر
        ونماذج الذكاء الاصطناعي.
        """
    )

    with st.expander(
        "ⓘ أمثلة على الأسئلة"
    ):

        st.write(
            """
            يمكنك السؤال مثلًا:

            • كم المخزون المتبقي؟

            • ما توزيع مخاطر المخزون؟

            • كم عدد المنتجات عالية المخاطر؟

            • ما أفضل نموذج للتنبؤ بالطلب؟

            • ما دقة نموذج تصنيف الصور؟
            """
        )

    st.divider()

    st.subheader(
        "أسئلة سريعة"
    )

    q1, q2, q3, q4 = st.columns(4)

    questions = [
        "كم المخزون المتبقي؟",
        "ما توزيع مخاطر المخزون؟",
        "كم عدد المنتجات عالية المخاطر؟",
        "ما دقة نموذج تصنيف الصور؟",
    ]

    columns = [
        q1,
        q2,
        q3,
        q4,
    ]

    for column, question in zip(
        columns,
        questions,
    ):

        with column:

            if st.button(
                question,
                use_container_width=True,
            ):

                st.session_state.chat_messages.append(
                    (
                        "user",
                        question,
                    )
                )

                response = post_api(
                    "/chat",
                    {
                        "question": question
                    },
                )

                if response.get("success"):

                    answer = response.get(
                        "answer",
                        "لا توجد إجابة.",
                    )

                else:

                    answer = (
                        "حدث خطأ: "
                        + response.get(
                            "error",
                            "غير معروف",
                        )
                    )

                st.session_state.chat_messages.append(
                    (
                        "assistant",
                        answer,
                    )
                )

    st.divider()

    for role, message in (
        st.session_state.chat_messages
    ):

        with st.chat_message(role):

            st.write(message)

    user_question = st.chat_input(
        "اكتب سؤالك هنا..."
    )

    if user_question:

        st.session_state.chat_messages.append(
            (
                "user",
                user_question,
            )
        )

        response = post_api(
            "/chat",
            {
                "question": user_question
            },
        )

        if response.get("success"):

            answer = response.get(
                "answer",
                "لا توجد إجابة.",
            )

        else:

            answer = (
                "تعذر الاتصال بالمساعد."
            )

        st.session_state.chat_messages.append(
            (
                "assistant",
                answer,
            )
        )

        st.rerun()

    if st.session_state.chat_messages:

        if st.button(
            "🗑️ مسح المحادثة"
        ):

            st.session_state.chat_messages = []

            st.rerun()


# ============================================================
# 16. حول النظام
# ============================================================

elif selected_page == "ℹ️ حول النظام":

    st.header(
        "ℹ️ حول SmartStock AI"
    )

    st.write(
        """
        SmartStock AI هو نظام متكامل لإدارة المخزون
        باستخدام الذكاء الاصطناعي.
        """
    )

    st.divider()

    c1, c2, c3, c4 = st.columns(4)

    with c1:

        st.info(
            """
            ### 📈 Demand AI

            Random Forest Regressor

            **R² = 0.6092**
            """
        )

    with c2:

        st.warning(
            """
            ### ⚠️ Risk AI

            K-Means

            **K = 4**
            """
        )

    with c3:

        st.info(
            """
            ### 🖼️ Vision AI

            MobileNetV2

            **Accuracy = 78.82%**
            """
        )

    with c4:

        st.success(
            """
            ### 🤖 Chatbot

            Transformer

            **FLAN-T5-small**
            """
        )

    st.divider()

    st.subheader(
        "🏗️ بنية النظام"
    )

    st.write(
        """
        Streamlit
        ↓
        FastAPI
        ↓
        ├── Square API
        ├── Demand Model
        ├── Risk Model
        ├── Image AI
        └── Transformer Chatbot
        """
    )

    st.divider()

    st.caption(
        "SmartStock AI © 2026"
    )