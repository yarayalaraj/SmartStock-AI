# ================================================================
# SMARTSTOCK AI
# نموذج مؤشر مخاطر المخزون والصلاحية
# Inventory & Expiry Risk Indicator
# ================================================================

# ================================================================
# استيراد المكتبات
# ================================================================

import io
import zipfile
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# خوارزمية K-Means للتجميع
from sklearn.cluster import KMeans

# PCA لتقليل الأبعاد
from sklearn.decomposition import PCA

# مقاييس تقييم Clustering
from sklearn.metrics import (
    silhouette_score,
    davies_bouldin_score,
    calinski_harabasz_score
)

# توحيد مقاييس المتغيرات
from sklearn.preprocessing import StandardScaler


# ================================================================
# إنشاء Class خاص بنموذج مخاطر المخزون والصلاحية
# ================================================================

class WasteRiskModel:

    # ------------------------------------------------------------
    # رابط Dataset من UCI
    # ------------------------------------------------------------
    # نستخدم Dataset حقيقية من UCI وليست بيانات مصطنعة.
    # Dataset تحتوي على معلومات عن:
    # - السعر
    # - مدة الصلاحية
    # - عدد عمليات الخروج
    # - إجمالي الكمية الخارجة
    # - وزن البالت
    # - ارتفاع البالت
    # - الوحدات في البالت
    # ------------------------------------------------------------

    DATA_URL = (
        "https://archive.ics.uci.edu/static/public/585/"
        "stock%2Bkeeping%2Bunits.zip"
    )

    # ============================================================
    # Constructor
    # ============================================================

    def __init__(self):

        # تخزين البيانات
        self.data = None

        # StandardScaler
        self.scaler = None

        # نموذج K-Means
        self.kmeans = None

        # PCA المستخدم للرسم ثنائي الأبعاد
        self.pca_2d = None

        # PCA المستخدم للاحتفاظ بـ 90% أو أكثر
        self.pca_90 = None

        # أفضل عدد Clusters
        self.selected_k = None

        # --------------------------------------------------------
        # تحديد مجلد المشروع الرئيسي
        # --------------------------------------------------------

        self.project_root = (
            Path(__file__).resolve().parents[1]
        )

        # --------------------------------------------------------
        # مجلد النماذج
        # --------------------------------------------------------

        self.models_dir = (
            self.project_root / "models"
        )

        # --------------------------------------------------------
        # مجلد البيانات المعالجة
        # --------------------------------------------------------

        self.processed_dir = (
            self.project_root /
            "data" /
            "processed"
        )

        # --------------------------------------------------------
        # مجلد الرسومات
        # --------------------------------------------------------

        self.plots_dir = (
            self.project_root / "plots"
        )

        # إنشاء المجلدات إذا لم تكن موجودة
        self.models_dir.mkdir(
            parents=True,
            exist_ok=True
        )

        self.processed_dir.mkdir(
            parents=True,
            exist_ok=True
        )

        self.plots_dir.mkdir(
            parents=True,
            exist_ok=True
        )

    # ============================================================
    # 1. تحميل البيانات
    # ============================================================

    def load_data(self):

        # requests لتحميل Dataset من الإنترنت
        import requests

        # تحميل ملف ZIP
        response = requests.get(
            self.DATA_URL,
            timeout=60
        )

        # التأكد من نجاح التحميل
        response.raise_for_status()

        # فتح ZIP من الذاكرة مباشرة
        # بدون الحاجة لحفظ الملف المضغوط على القرص
        zip_file = zipfile.ZipFile(
            io.BytesIO(response.content)
        )

        # البحث عن ملف Excel داخل ZIP
        excel_files = [
            name
            for name in zip_file.namelist()
            if name.lower().endswith(".xlsx")
        ]

        # التأكد من وجود ملف Excel
        if not excel_files:

            raise FileNotFoundError(
                "لم يتم العثور على ملف Excel داخل Dataset."
            )

        # قراءة ملف Excel مباشرة
        with zip_file.open(
            excel_files[0]
        ) as file:

            dataframe = pd.read_excel(
                file
            )

        # --------------------------------------------------------
        # طباعة معلومات Dataset
        # --------------------------------------------------------

        print("=" * 60)
        print(
            "تم تحميل بيانات المخزون والصلاحية بنجاح"
        )
        print("=" * 60)

        print(
            "عدد الصفوف:",
            len(dataframe)
        )

        print(
            "الأعمدة:",
            list(dataframe.columns)
        )

        # حفظ البيانات داخل Class
        self.data = dataframe

        return dataframe

    # ============================================================
    # 2. تنظيف البيانات
    # ============================================================

    def clean_data(
        self,
        dataframe
    ):

        # نسخ البيانات حتى لا نغير Dataset الأصلية
        dataframe = dataframe.copy()

        # --------------------------------------------------------
        # الأعمدة الرقمية التي نحتاجها
        # --------------------------------------------------------

        numeric_columns = [

            "ID",

            "Unitprice",

            "Expire date",

            "Outbound number",

            "Total outbound",

            "Pal grossweight",

            "Pal height",

            "Units per pal"
        ]

        # --------------------------------------------------------
        # تحويل الأعمدة إلى أرقام
        # --------------------------------------------------------

        for column in numeric_columns:

            dataframe[column] = pd.to_numeric(
                dataframe[column],
                errors="coerce"
            )

        # --------------------------------------------------------
        # حذف الصفوف التي تحتوي على قيم مفقودة
        # --------------------------------------------------------

        dataframe = dataframe.dropna(
            subset=numeric_columns
        )

        # --------------------------------------------------------
        # إزالة القيم السالبة غير المنطقية
        # --------------------------------------------------------

        dataframe = dataframe[
            dataframe["Unitprice"] >= 0
        ]

        dataframe = dataframe[
            dataframe["Expire date"] >= 0
        ]

        dataframe = dataframe[
            dataframe["Outbound number"] >= 0
        ]

        dataframe = dataframe[
            dataframe["Total outbound"] >= 0
        ]

        dataframe = dataframe[
            dataframe["Pal grossweight"] >= 0
        ]

        dataframe = dataframe[
            dataframe["Pal height"] >= 0
        ]

        dataframe = dataframe[
            dataframe["Units per pal"] >= 0
        ]

        # إعادة ترتيب Index
        dataframe = dataframe.reset_index(
            drop=True
        )

        # --------------------------------------------------------
        # عرض نتائج التنظيف
        # --------------------------------------------------------

        print("=" * 60)
        print(
            "تم تنظيف بيانات المخزون والصلاحية"
        )
        print("=" * 60)

        print(
            "عدد الصفوف بعد التنظيف:",
            len(dataframe)
        )

        print(
            "عدد القيم المفقودة:",
            dataframe.isnull().sum().sum()
        )

        return dataframe

    # ============================================================
    # 3. تجهيز Features
    # ============================================================

    def prepare_features(
        self,
        dataframe
    ):

        # --------------------------------------------------------
        # Features المستخدمة في التحليل
        # --------------------------------------------------------

        features = [

            "Unitprice",

            "Expire date",

            "Outbound number",

            "Total outbound",

            "Pal grossweight",

            "Pal height",

            "Units per pal"
        ]

        # إنشاء DataFrame للـ Features
        X = dataframe[
            features
        ].copy()

        # --------------------------------------------------------
        # Log Transformation
        # --------------------------------------------------------
        # بعض المتغيرات تحتوي على قيم كبيرة جدًا وانحراف كبير.
        # log1p يساعد على تقليل تأثير القيم الكبيرة جدًا.
        # --------------------------------------------------------

        log_columns = [

            "Unitprice",

            "Outbound number",

            "Total outbound",

            "Pal grossweight",

            "Pal height",

            "Units per pal"
        ]

        for column in log_columns:

            X[column] = np.log1p(
                X[column]
            )

        # --------------------------------------------------------
        # StandardScaler
        # --------------------------------------------------------
        # نحول Features إلى مقاييس متقاربة.
        # هذا مهم جدًا لـ K-Means و PCA.
        # --------------------------------------------------------

        self.scaler = StandardScaler()

        X_scaled = self.scaler.fit_transform(
            X
        )

        return X, X_scaled

    # ============================================================
    # 4. تحديد أفضل عدد من Clusters
    # ============================================================

    def evaluate_clusters(
        self,
        X_scaled
    ):

        # قائمة لحفظ النتائج
        results = []

        print("=" * 60)
        print(
            "تقييم عدد الـ Clusters"
        )
        print("=" * 60)

        # تجربة K من 2 إلى 8
        for k in range(2, 9):

            # إنشاء نموذج K-Means
            model = KMeans(

                n_clusters=k,

                random_state=42,

                n_init=20
            )

            # تدريب النموذج والحصول على Cluster لكل منتج
            labels = model.fit_predict(
                X_scaled
            )

            # ----------------------------------------------------
            # Silhouette Score
            # ----------------------------------------------------
            # يقيس مدى جودة فصل الـ Clusters.
            # كلما ارتفع كان الفصل أفضل.
            # ----------------------------------------------------

            silhouette = silhouette_score(
                X_scaled,
                labels
            )

            # ----------------------------------------------------
            # Davies-Bouldin Index
            # ----------------------------------------------------
            # كلما انخفض كان أفضل.
            # ----------------------------------------------------

            davies = davies_bouldin_score(
                X_scaled,
                labels
            )

            # ----------------------------------------------------
            # Calinski-Harabasz
            # ----------------------------------------------------
            # يقيس جودة الفصل بين المجموعات.
            # غالبًا القيمة الأعلى أفضل.
            # ----------------------------------------------------

            calinski = (
                calinski_harabasz_score(
                    X_scaled,
                    labels
                )
            )

            # إضافة النتائج
            results.append({

                "n_clusters": k,

                "inertia":
                    model.inertia_,

                "silhouette_score":
                    silhouette,

                "davies_bouldin_score":
                    davies,

                "calinski_harabasz_score":
                    calinski
            })

        # تحويل النتائج إلى DataFrame
        metrics_df = pd.DataFrame(
            results
        )

        # عرض النتائج
        print(
            metrics_df.to_string(
                index=False
            )
        )

        # --------------------------------------------------------
        # اختيار K الذي يملك أعلى Silhouette Score
        # --------------------------------------------------------

        best_row = metrics_df.loc[
            metrics_df[
                "silhouette_score"
            ].idxmax()
        ]

        self.selected_k = int(
            best_row[
                "n_clusters"
            ]
        )

        print()

        print(
            "أفضل عدد من Clusters:",
            self.selected_k
        )

        print(
            "أفضل Silhouette Score:",
            round(
                best_row[
                    "silhouette_score"
                ],
                4
            )
        )

        # --------------------------------------------------------
        # حفظ نتائج Clustering
        # --------------------------------------------------------

        metrics_df.to_csv(

            self.processed_dir /
            "inventory_expiry_clustering_metrics.csv",

            index=False
        )

        return metrics_df

    # ============================================================
    # 5. تدريب K-Means النهائي
    # ============================================================

    def train_kmeans(
        self,
        X_scaled
    ):

        # إنشاء K-Means باستخدام أفضل K
        self.kmeans = KMeans(

            n_clusters=self.selected_k,

            random_state=42,

            n_init=20
        )

        # تدريب النموذج
        labels = self.kmeans.fit_predict(
            X_scaled
        )

        return labels

    # ============================================================
    # 6. PCA ثنائي الأبعاد للرسم
    # ============================================================

    def create_pca_2d(
        self,
        X_scaled,
        labels
    ):

        # --------------------------------------------------------
        # نستخدم Componentين فقط للرسم
        # --------------------------------------------------------

        self.pca_2d = PCA(

            n_components=2,

            random_state=42
        )

        # تحويل البيانات إلى بعدين
        components = (
            self.pca_2d.fit_transform(
                X_scaled
            )
        )

        # نسبة التباين التي يفسرها كل Component
        explained = (
            self.pca_2d
            .explained_variance_ratio_
        )

        print("=" * 60)
        print(
            "PCA ثنائي الأبعاد"
        )
        print("=" * 60)

        print(
            f"PC1: "
            f"{explained[0] * 100:.2f}%"
        )

        print(
            f"PC2: "
            f"{explained[1] * 100:.2f}%"
        )

        print(
            f"PC1 + PC2: "
            f"{explained.sum() * 100:.2f}%"
        )

        # إنشاء DataFrame للـ PCA
        pca_df = pd.DataFrame(

            components,

            columns=[
                "PC1",
                "PC2"
            ]
        )

        # إضافة Cluster
        pca_df["cluster"] = labels

        # --------------------------------------------------------
        # رسم Clusters
        # --------------------------------------------------------

        plt.figure(
            figsize=(10, 7)
        )

        # رسم كل Cluster بشكل منفصل
        for cluster in sorted(
            pca_df[
                "cluster"
            ].unique()
        ):

            cluster_data = (
                pca_df[
                    pca_df[
                        "cluster"
                    ] == cluster
                ]
            )

            plt.scatter(

                cluster_data["PC1"],

                cluster_data["PC2"],

                label=f"Cluster {cluster}",

                alpha=0.6
            )

        plt.xlabel(
            "Principal Component 1"
        )

        plt.ylabel(
            "Principal Component 2"
        )

        plt.title(
            "PCA 2D - Inventory Clusters"
        )

        plt.legend()

        plt.grid(
            alpha=0.3
        )

        plt.tight_layout()

        # حفظ الرسم
        plt.savefig(

            self.plots_dir /
            "inventory_expiry_pca_clusters.png",

            dpi=300
        )

        plt.close()

        return components

    # ============================================================
    # 7. PCA مع الاحتفاظ بـ 90% أو أكثر من المعلومات
    # ============================================================

    def create_pca_90(
        self,
        X_scaled
    ):

        # --------------------------------------------------------
        # أولًا نحسب جميع Components
        # --------------------------------------------------------

        pca_full = PCA(
            n_components=None,
            random_state=42
        )

        pca_full.fit(
            X_scaled
        )

        # نسبة التباين لكل Component
        explained = (
            pca_full
            .explained_variance_ratio_
        )

        # النسبة التراكمية
        cumulative = np.cumsum(
            explained
        )

        # --------------------------------------------------------
        # البحث عن أقل عدد Components
        # يحافظ على 90% على الأقل من التباين
        # --------------------------------------------------------

        n_components_90 = (

            np.argmax(
                cumulative >= 0.90
            )

            + 1
        )

        # --------------------------------------------------------
        # إنشاء PCA النهائي
        # --------------------------------------------------------

        self.pca_90 = PCA(

            n_components=
                n_components_90,

            random_state=42
        )

        # تحويل البيانات
        transformed = (
            self.pca_90.fit_transform(
                X_scaled
            )
        )

        # النسبة النهائية
        achieved_variance = (

            self.pca_90
            .explained_variance_ratio_
            .sum()
        )

        print("=" * 60)
        print(
            "PCA - الاحتفاظ بـ 90% أو أكثر"
        )
        print("=" * 60)

        print(
            "عدد Features الأصلية:",
            X_scaled.shape[1]
        )

        print(
            "عدد Components المختارة:",
            n_components_90
        )

        print(
            "نسبة التباين المحفوظة:",
            f"{achieved_variance * 100:.2f}%"
        )

        print()

        # --------------------------------------------------------
        # طباعة نتيجة كل Component
        # --------------------------------------------------------

        for index, value in enumerate(

            explained,

            start=1
        ):

            print(

                f"PC{index}: "
                f"{value * 100:.2f}% | "
                f"التراكمي: "
                f"{cumulative[index - 1] * 100:.2f}%"
            )

        # ========================================================
        # الرسم الأول:
        # Explained Variance لكل Component
        # ========================================================

        components = np.arange(

            1,

            len(explained) + 1
        )

        plt.figure(
            figsize=(10, 6)
        )

        plt.plot(

            components,

            explained * 100,

            marker="o"
        )

        plt.xlabel(
            "Principal Component"
        )

        plt.ylabel(
            "Explained Variance (%)"
        )

        plt.title(
            "PCA Explained Variance"
        )

        plt.xticks(
            components
        )

        plt.grid(
            alpha=0.3
        )

        plt.tight_layout()

        plt.savefig(

            self.plots_dir /
            "inventory_expiry_pca_explained_variance.png",

            dpi=300
        )

        plt.close()

        # ========================================================
        # الرسم الثاني:
        # Cumulative Explained Variance
        # ========================================================

        plt.figure(
            figsize=(10, 6)
        )

        plt.plot(

            components,

            cumulative * 100,

            marker="o"
        )

        # خط 90%
        plt.axhline(

            y=90,

            linestyle="--",

            label="90% threshold"
        )

        # خط عند عدد Components المختارة
        plt.axvline(

            x=n_components_90,

            linestyle="--",

            label=(
                f"{n_components_90} components"
            )
        )

        plt.xlabel(
            "Number of Principal Components"
        )

        plt.ylabel(
            "Cumulative Explained Variance (%)"
        )

        plt.title(
            "PCA Cumulative Explained Variance"
        )

        plt.xticks(
            components
        )

        plt.legend()

        plt.grid(
            alpha=0.3
        )

        plt.tight_layout()

        plt.savefig(

            self.plots_dir /
            "inventory_expiry_pca_cumulative_variance.png",

            dpi=300
        )

        plt.close()

        # ========================================================
        # حفظ معلومات PCA
        # ========================================================

        pca_variance_df = pd.DataFrame({

            "component":
                components,

            "explained_variance":
                explained,

            "explained_variance_percent":
                explained * 100,

            "cumulative_variance":
                cumulative,

            "cumulative_variance_percent":
                cumulative * 100
        })

        pca_variance_df.to_csv(

            self.processed_dir /
            "inventory_expiry_pca_variance.csv",

            index=False
        )

        return transformed

    # ============================================================
    # 8. حساب مؤشر مخاطر المخزون والصلاحية
    # ============================================================

    def calculate_risk_score(
        self,
        dataframe
    ):

        dataframe = dataframe.copy()

        # --------------------------------------------------------
        # الجزء الأول من المخاطر:
        # مدة الصلاحية
        # --------------------------------------------------------
        #
        # مدة صلاحية أقصر = مؤشر خطر أعلى.
        #
        # ملاحظة:
        # هذا ليس تنبؤًا فعليًا بانتهاء المنتج.
        # إنه Risk Indicator تحليلي.
        # --------------------------------------------------------

        max_expire = dataframe[
            "Expire date"
        ].max()

        if max_expire > 0:

            shelf_life_risk = (

                1 -

                dataframe[
                    "Expire date"
                ] /

                max_expire
            )

        else:

            shelf_life_risk = pd.Series(

                0,

                index=dataframe.index
            )

        # --------------------------------------------------------
        # الجزء الثاني:
        # انخفاض إجمالي Outbound
        #
        # منتج ذو حركة منخفضة قد يحمل خطر مخزون أعلى.
        # --------------------------------------------------------

        max_total_outbound = (
            dataframe[
                "Total outbound"
            ].max()
        )

        if max_total_outbound > 0:

            demand_risk = (

                1 -

                dataframe[
                    "Total outbound"
                ] /

                max_total_outbound
            )

        else:

            demand_risk = pd.Series(

                0,

                index=dataframe.index
            )

        # --------------------------------------------------------
        # الجزء الثالث:
        # انخفاض عدد عمليات Outbound
        # --------------------------------------------------------

        max_outbound_number = (
            dataframe[
                "Outbound number"
            ].max()
        )

        if max_outbound_number > 0:

            activity_risk = (

                1 -

                dataframe[
                    "Outbound number"
                ] /

                max_outbound_number
            )

        else:

            activity_risk = pd.Series(

                0,

                index=dataframe.index
            )

        # ========================================================
        # حساب Risk Score النهائي
        # ========================================================
        #
        # 50% مدة الصلاحية
        # 30% إجمالي الحركة
        # 20% تكرار الحركة
        # ========================================================

        dataframe[
            "inventory_expiry_risk_score"
        ] = (

            0.50 * shelf_life_risk

            +

            0.30 * demand_risk

            +

            0.20 * activity_risk

        ) * 100

        # --------------------------------------------------------
        # تحويل الدرجة إلى مستويات
        # --------------------------------------------------------

        dataframe[
            "inventory_expiry_risk_level"
        ] = pd.cut(

            dataframe[
                "inventory_expiry_risk_score"
            ],

            bins=[

                -np.inf,

                40,

                70,

                np.inf
            ],

            labels=[

                "Low",

                "Medium",

                "High"
            ]
        )

        return dataframe

    # ============================================================
    # 9. إنشاء الرسومات الخاصة بالمخاطر
    # ============================================================

    def create_risk_plots(
        self,
        dataframe,
        labels
    ):

        dataframe = dataframe.copy()

        # إضافة Cluster
        dataframe[
            "cluster"
        ] = labels

        # ========================================================
        # الرسم الأول:
        # توزيع Risk Score
        # ========================================================

        plt.figure(
            figsize=(10, 6)
        )

        plt.hist(

            dataframe[
                "inventory_expiry_risk_score"
            ],

            bins=30
        )

        plt.xlabel(
            "Inventory / Expiry Risk Score"
        )

        plt.ylabel(
            "Number of Products"
        )

        plt.title(
            "Inventory / Expiry Risk Score Distribution"
        )

        plt.grid(
            alpha=0.3
        )

        plt.tight_layout()

        plt.savefig(

            self.plots_dir /
            "inventory_expiry_risk_score_distribution.png",

            dpi=300
        )

        plt.close()

        # ========================================================
        # الرسم الثاني:
        # توزيع Low / Medium / High
        # ========================================================

        counts = (

            dataframe[
                "inventory_expiry_risk_level"
            ]

            .value_counts()

            .reindex(

                [
                    "Low",
                    "Medium",
                    "High"
                ],

                fill_value=0
            )
        )

        plt.figure(
            figsize=(8, 6)
        )

        plt.bar(

            counts.index,

            counts.values
        )

        plt.xlabel(
            "Inventory / Expiry Risk Level"
        )

        plt.ylabel(
            "Number of Products"
        )

        plt.title(
            "Inventory / Expiry Risk Level Distribution"
        )

        plt.grid(
            axis="y",

            alpha=0.3
        )

        plt.tight_layout()

        plt.savefig(

            self.plots_dir /
            "inventory_expiry_risk_level_distribution.png",

            dpi=300
        )

        plt.close()

        # ========================================================
        # الرسم الثالث:
        # متوسط المخاطر حسب Cluster
        # ========================================================

        cluster_risk = (

            dataframe

            .groupby(
                "cluster",
                observed=False
            )

            [
                "inventory_expiry_risk_score"
            ]

            .mean()
        )

        plt.figure(
            figsize=(9, 6)
        )

        plt.bar(

            cluster_risk.index.astype(
                str
            ),

            cluster_risk.values
        )

        plt.xlabel(
            "Cluster"
        )

        plt.ylabel(
            "Average Inventory / Expiry Risk Score"
        )

        plt.title(
            "Average Inventory / Expiry Risk by Cluster"
        )

        plt.grid(
            axis="y",

            alpha=0.3
        )

        plt.tight_layout()

        plt.savefig(

            self.plots_dir /
            "inventory_expiry_cluster_risk.png",

            dpi=300
        )

        plt.close()

        # ========================================================
        # الرسم الرابع:
        # Shelf Life مقابل Total Outbound
        # ========================================================

        plt.figure(
            figsize=(10, 7)
        )

        scatter = plt.scatter(

            dataframe[
                "Expire date"
            ],

            dataframe[
                "Total outbound"
            ],

            c=dataframe[
                "inventory_expiry_risk_score"
            ],

            alpha=0.65
        )

        plt.xlabel(
            "Shelf Life (days)"
        )

        plt.ylabel(
            "Total Outbound"
        )

        plt.title(
            "Shelf Life vs Total Outbound"
        )

        plt.colorbar(

            scatter,

            label=(
                "Inventory / Expiry Risk Score"
            )
        )

        plt.grid(
            alpha=0.3
        )

        plt.tight_layout()

        plt.savefig(

            self.plots_dir /
            "inventory_expiry_shelf_life_vs_outbound.png",

            dpi=300
        )

        plt.close()

        # ========================================================
        # الرسم الخامس:
        # Outbound Number مقابل Total Outbound
        # ========================================================

        plt.figure(
            figsize=(10, 7)
        )

        plt.scatter(

            dataframe[
                "Outbound number"
            ],

            dataframe[
                "Total outbound"
            ],

            c=dataframe[
                "inventory_expiry_risk_score"
            ],

            alpha=0.65
        )

        plt.xlabel(
            "Outbound Number"
        )

        plt.ylabel(
            "Total Outbound"
        )

        plt.title(
            "Outbound Number vs Total Outbound"
        )

        plt.grid(
            alpha=0.3
        )

        plt.tight_layout()

        plt.savefig(

            self.plots_dir /
            "inventory_expiry_outbound_relationship.png",

            dpi=300
        )

        plt.close()

    # ============================================================
    # 10. إنشاء Cluster Profiles
    # ============================================================

    def create_cluster_profiles(
        self,
        dataframe,
        labels
    ):

        dataframe = dataframe.copy()

        # إضافة Cluster لكل منتج
        dataframe[
            "cluster"
        ] = labels

        # حساب Risk Indicator
        risk_dataframe = (
            self.calculate_risk_score(
                dataframe
            )
        )

        # نسخ Risk Score
        dataframe[
            "inventory_expiry_risk_score"
        ] = (

            risk_dataframe[
                "inventory_expiry_risk_score"
            ]
        )

        # نسخ Risk Level
        dataframe[
            "inventory_expiry_risk_level"
        ] = (

            risk_dataframe[
                "inventory_expiry_risk_level"
            ]
        )

        # --------------------------------------------------------
        # حساب متوسط خصائص كل Cluster
        # --------------------------------------------------------

        profile = (

            dataframe

            .groupby(
                "cluster",
                observed=False
            )

            .agg(

                products=(
                    "ID",
                    "count"
                ),

                avg_unit_price=(
                    "Unitprice",
                    "mean"
                ),

                avg_shelf_life_days=(
                    "Expire date",
                    "mean"
                ),

                avg_outbound_number=(
                    "Outbound number",
                    "mean"
                ),

                avg_total_outbound=(
                    "Total outbound",
                    "mean"
                ),

                avg_units_per_pal=(
                    "Units per pal",
                    "mean"
                ),

                avg_inventory_expiry_risk_score=(
                    "inventory_expiry_risk_score",
                    "mean"
                )
            )

            .reset_index()
        )

        # --------------------------------------------------------
        # تحديد مستوى الخطر لكل Cluster
        # --------------------------------------------------------

        profile[
            "inventory_expiry_risk_level"
        ] = pd.cut(

            profile[
                "avg_inventory_expiry_risk_score"
            ],

            bins=[

                -np.inf,

                40,

                70,

                np.inf
            ],

            labels=[

                "Low",

                "Medium",

                "High"
            ]
        )

        print("=" * 60)
        print(
            "INVENTORY & EXPIRY CLUSTER PROFILES"
        )
        print("=" * 60)

        print(
            profile.to_string(
                index=False
            )
        )

        # حفظ Cluster Profiles
        profile.to_csv(

            self.processed_dir /
            "inventory_expiry_cluster_profiles.csv",

            index=False
        )

        return profile

    # ============================================================
    # 11. تشغيل النموذج بالكامل
    # ============================================================

    def run(self):

        # --------------------------------------------------------
        # الخطوة 1: تحميل البيانات
        # --------------------------------------------------------

        dataframe = self.load_data()

        # --------------------------------------------------------
        # الخطوة 2: تنظيف البيانات
        # --------------------------------------------------------

        dataframe = self.clean_data(
            dataframe
        )

        # --------------------------------------------------------
        # الخطوة 3: تجهيز Features
        # --------------------------------------------------------

        _, X_scaled = (
            self.prepare_features(
                dataframe
            )
        )

        # --------------------------------------------------------
        # الخطوة 4: اختيار أفضل K
        # --------------------------------------------------------

        self.evaluate_clusters(
            X_scaled
        )

        # --------------------------------------------------------
        # الخطوة 5: تدريب K-Means النهائي
        # --------------------------------------------------------

        labels = self.train_kmeans(
            X_scaled
        )

        # --------------------------------------------------------
        # الخطوة 6: PCA ثنائي الأبعاد
        # للرسم فقط
        # --------------------------------------------------------

        self.create_pca_2d(

            X_scaled,

            labels
        )

        # --------------------------------------------------------
        # الخطوة 7: PCA للحفاظ على ≥90%
        # --------------------------------------------------------

        self.create_pca_90(
            X_scaled
        )

        # --------------------------------------------------------
        # الخطوة 8: حساب Risk Indicator
        # --------------------------------------------------------

        dataframe = (
            self.calculate_risk_score(
                dataframe
            )
        )

        # إضافة Cluster
        dataframe[
            "cluster"
        ] = labels

        # --------------------------------------------------------
        # الخطوة 9: إنشاء Cluster Profiles
        # --------------------------------------------------------

        self.create_cluster_profiles(

            dataframe,

            labels
        )

        # --------------------------------------------------------
        # الخطوة 10: إنشاء الرسومات
        # --------------------------------------------------------

        self.create_risk_plots(

            dataframe,

            labels
        )

        # ========================================================
        # تقييم K-Means النهائي
        # ========================================================

        final_silhouette = (
            silhouette_score(

                X_scaled,

                labels
            )
        )

        final_davies = (
            davies_bouldin_score(

                X_scaled,

                labels
            )
        )

        final_calinski = (
            calinski_harabasz_score(

                X_scaled,

                labels
            )
        )

        print("=" * 60)
        print(
            "FINAL CLUSTERING METRICS"
        )
        print("=" * 60)

        print(

            f"Silhouette Score: "
            f"{final_silhouette:.4f}"
        )

        print(

            f"Davies-Bouldin Index: "
            f"{final_davies:.4f}"
        )

        print(

            f"Calinski-Harabasz Score: "
            f"{final_calinski:.4f}"
        )

        # ========================================================
        # توزيع مستويات المخاطر
        # ========================================================

        print("=" * 60)
        print(
            "INVENTORY & EXPIRY RISK DISTRIBUTION"
        )
        print("=" * 60)

        print(

            dataframe[
                "inventory_expiry_risk_level"
            ]

            .value_counts()

            .reindex(

                [
                    "Low",
                    "Medium",
                    "High"
                ],

                fill_value=0
            )
        )

        # ========================================================
        # حفظ التحليل النهائي
        # ========================================================

        dataframe.to_csv(

            self.processed_dir /
            "inventory_expiry_risk_analysis.csv",

            index=False
        )

        # ========================================================
        # حفظ النموذج
        # ========================================================

        import joblib

        model_data = {

            # StandardScaler
            "scaler":
                self.scaler,

            # K-Means
            "kmeans":
                self.kmeans,

            # PCA للرسم
            "pca_2d":
                self.pca_2d,

            # PCA الذي يحتفظ بـ 90%+
            "pca_90":
                self.pca_90,

            # أفضل K
            "selected_k":
                self.selected_k
        }

        # --------------------------------------------------------
        # حفظ النموذج بصيغة PKL
        # --------------------------------------------------------

        joblib.dump(

            model_data,

            self.models_dir /
            "waste_risk_model.pkl"
        )

        # ========================================================
        # رسالة النهاية
        # ========================================================

        print("=" * 60)
        print(
            "INVENTORY & EXPIRY RISK MODEL COMPLETED"
        )
        print("=" * 60)

        print(

            "تم حفظ النموذج في:",

            self.models_dir /
            "waste_risk_model.pkl"
        )

        print(

            "تم حفظ التحليل في:",

            self.processed_dir /
            "inventory_expiry_risk_analysis.csv"
        )

        print(

            "تم حفظ نتائج PCA في:",

            self.processed_dir /
            "inventory_expiry_pca_variance.csv"
        )


# ================================================================
# تشغيل البرنامج
# ================================================================

if __name__ == "__main__":

    # إنشاء النموذج
    model = WasteRiskModel()

    # تشغيل جميع المراحل
    model.run()
