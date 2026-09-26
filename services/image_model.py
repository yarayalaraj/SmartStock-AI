# ============================================================
# SMARTSTOCK AI
# IMAGE AI - REALWASTE WASTE CLASSIFICATION
# MobileNetV2 Transfer Learning + Fine-Tuning
# ============================================================

from pathlib import Path
import json

import numpy as np
import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.utils.class_weight import compute_class_weight
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    classification_report,
    confusion_matrix,
)

# ============================================================
# 1. إعداد المسارات
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Dataset الحقيقي الموجود على القرص H
DATASET_DIR = Path(
    r"H:\SmartStockData\RealWaste\dataset"
)

# مجلد حفظ النموذج
MODEL_DIR = PROJECT_ROOT / "models"

# مجلد حفظ الرسومات
PLOTS_DIR = PROJECT_ROOT / "plots"

# مجلد حفظ النتائج
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"

# إنشاء المجلدات
MODEL_DIR.mkdir(
    parents=True,
    exist_ok=True
)

PLOTS_DIR.mkdir(
    parents=True,
    exist_ok=True
)

PROCESSED_DIR.mkdir(
    parents=True,
    exist_ok=True
)

# ============================================================
# 2. إعدادات Image AI
# ============================================================

IMG_SIZE = (224, 224)

BATCH_SIZE = 32

SEED = 42

TEST_SPLIT = 0.15

VALIDATION_SPLIT = 0.15

INITIAL_EPOCHS = 8

FINE_TUNE_EPOCHS = 20

TOTAL_EPOCHS = (
    INITIAL_EPOCHS
    + FINE_TUNE_EPOCHS
)

FINE_TUNE_LAST_LAYERS = 40

# ============================================================
# Lazy TensorFlow
# ============================================================

# مهم:
# لا نستورد TensorFlow عند تشغيل API.
#
# TensorFlow سيتم تحميله فقط عندما:
# 1. نريد تدريب النموذج
# 2. نريد عمل prediction
#
# هذا يقلل استهلاك RAM عند تشغيل FastAPI.

_tf = None


def get_tensorflow():
    """
    تحميل TensorFlow عند الحاجة فقط.
    """

    global _tf

    if _tf is None:

        print(
            "Loading TensorFlow..."
        )

        import tensorflow as tf

        _tf = tf

        # تثبيت Random Seed
        tf.keras.utils.set_random_seed(
            SEED
        )

        print(
            "TensorFlow loaded successfully."
        )

    return _tf


# ============================================================
# أسماء ملفات النموذج والنتائج
# ============================================================

MODEL_PATH = (
    MODEL_DIR
    / "image_mobilenetv2.keras"
)

BEST_MODEL_PATH = (
    MODEL_DIR
    / "image_mobilenetv2_best.keras"
)

CLASS_NAMES_PATH = (
    MODEL_DIR
    / "image_class_names.json"
)

HISTORY_PATH = (
    PROCESSED_DIR
    / "image_training_history.csv"
)

METRICS_PATH = (
    PROCESSED_DIR
    / "image_model_metrics.csv"
)

REPORT_PATH = (
    PROCESSED_DIR
    / "image_classification_report.csv"
)

SPLIT_SUMMARY_PATH = (
    PROCESSED_DIR
    / "image_dataset_split_summary.csv"
)


# ============================================================
# 3. فحص Dataset
# ============================================================

def check_dataset():
    """
    التأكد من وجود Dataset وقراءة عدد الصور داخل كل فئة.
    """

    print("=" * 70)
    print("SMARTSTOCK AI - IMAGE DATASET CHECK")
    print("=" * 70)

    print("\nDataset path:")
    print(DATASET_DIR)

    if not DATASET_DIR.exists():

        raise FileNotFoundError(
            f"Dataset غير موجود في المسار:\n"
            f"{DATASET_DIR}"
        )

    class_directories = sorted(
        [
            folder
            for folder in DATASET_DIR.iterdir()
            if folder.is_dir()
        ]
    )

    if not class_directories:

        raise ValueError(
            "لم يتم العثور على مجلدات الفئات داخل Dataset."
        )

    valid_extensions = {
        ".jpg",
        ".jpeg",
        ".png",
        ".webp",
    }

    total_images = 0

    print("\nClasses and image counts:")

    for class_dir in class_directories:

        count = sum(
            1
            for file in class_dir.rglob("*")
            if (
                file.is_file()
                and file.suffix.lower()
                in valid_extensions
            )
        )

        total_images += count

        print(
            f"{class_dir.name:<30}: "
            f"{count:>4} images"
        )

    print(
        f"\nTotal images: {total_images}"
    )

    if total_images == 0:

        raise ValueError(
            "لم يتم العثور على صور داخل Dataset."
        )

    print("\nSUCCESS:")

    print(
        f"تم العثور على {total_images} صورة كاملة."
    )


# ============================================================
# 4. جمع مسارات الصور
# ============================================================

def collect_image_paths():
    """
    جمع مسارات الصور وربط كل صورة بالـclass الخاص بها.
    """

    print("=" * 70)
    print("COLLECTING IMAGE PATHS")
    print("=" * 70)

    valid_extensions = {
        ".jpg",
        ".jpeg",
        ".png",
        ".webp",
    }

    class_names = sorted(
        [
            folder.name
            for folder in DATASET_DIR.iterdir()
            if folder.is_dir()
        ]
    )

    class_to_index = {
        class_name: index
        for index, class_name
        in enumerate(class_names)
    }

    image_paths = []

    labels = []

    for class_name in class_names:

        class_directory = (
            DATASET_DIR / class_name
        )

        for image_path in sorted(
            class_directory.rglob("*")
        ):

            if (
                image_path.is_file()
                and image_path.suffix.lower()
                in valid_extensions
            ):

                image_paths.append(
                    str(image_path)
                )

                labels.append(
                    class_to_index[
                        class_name
                    ]
                )

    image_paths = np.array(
        image_paths
    )

    labels = np.array(
        labels,
        dtype=np.int32
    )

    print(
        f"\nTotal image paths: "
        f"{len(image_paths)}"
    )

    print("\nClass mapping:")

    for class_name, index in (
        class_to_index.items()
    ):

        print(
            f"{index} -> {class_name}"
        )

    with open(
        CLASS_NAMES_PATH,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            class_names,
            file,
            ensure_ascii=False,
            indent=4
        )

    print(
        "\nClass names saved to:"
    )

    print(
        CLASS_NAMES_PATH
    )

    return (
        image_paths,
        labels,
        class_names
    )


# ============================================================
# 5. تقسيم Dataset
# ============================================================

def split_dataset(
    image_paths,
    labels,
    class_names
):
    """
    تقسيم الصور إلى:
    70% Training
    15% Validation
    15% Test
    """

    print("=" * 70)
    print("SPLITTING DATASET")
    print("=" * 70)

    (
        train_paths,
        temp_paths,
        train_labels,
        temp_labels
    ) = train_test_split(
        image_paths,
        labels,
        test_size=(
            TEST_SPLIT
            + VALIDATION_SPLIT
        ),
        stratify=labels,
        random_state=SEED,
    )

    test_ratio_inside_temp = (
        TEST_SPLIT
        / (
            TEST_SPLIT
            + VALIDATION_SPLIT
        )
    )

    (
        val_paths,
        test_paths,
        val_labels,
        test_labels
    ) = train_test_split(
        temp_paths,
        temp_labels,
        test_size=test_ratio_inside_temp,
        stratify=temp_labels,
        random_state=SEED,
    )

    print(
        f"\nTraining images: "
        f"{len(train_paths)}"
    )

    print(
        f"Validation images: "
        f"{len(val_paths)}"
    )

    print(
        f"Test images: "
        f"{len(test_paths)}"
    )

    print(
        f"\nTotal: {len(image_paths)}"
    )

    split_rows = []

    for (
        class_index,
        class_name
    ) in enumerate(class_names):

        train_count = np.sum(
            train_labels == class_index
        )

        val_count = np.sum(
            val_labels == class_index
        )

        test_count = np.sum(
            test_labels == class_index
        )

        split_rows.append(
            {
                "class_name": class_name,
                "train": int(
                    train_count
                ),
                "validation": int(
                    val_count
                ),
                "test": int(
                    test_count
                ),
                "total": int(
                    train_count
                    + val_count
                    + test_count
                ),
            }
        )

    split_df = pd.DataFrame(
        split_rows
    )

    split_df.to_csv(
        SPLIT_SUMMARY_PATH,
        index=False,
        encoding="utf-8-sig",
    )

    print(
        "\nDataset split summary saved to:"
    )

    print(
        SPLIT_SUMMARY_PATH
    )

    return (
        train_paths,
        train_labels,
        val_paths,
        val_labels,
        test_paths,
        test_labels,
    )


# ============================================================
# 6. قراءة الصور
# ============================================================

def load_image(
    image_path,
    label
):
    """
    قراءة الصورة وتحويلها إلى RGB
    ثم تغيير حجمها.
    """

    tf = get_tensorflow()

    image = tf.io.read_file(
        image_path
    )

    image = tf.image.decode_image(
        image,
        channels=3,
        expand_animations=False,
    )

    image.set_shape(
        [
            None,
            None,
            3,
        ]
    )

    image = tf.image.resize(
        image,
        IMG_SIZE,
    )

    image = tf.cast(
        image,
        tf.float32,
    )

    return image, label


# ============================================================
# 7. إنشاء TensorFlow Dataset
# ============================================================

def create_dataset(
    image_paths,
    labels,
    training=False,
):
    """
    إنشاء tf.data.Dataset بكفاءة.
    """

    tf = get_tensorflow()

    AUTOTUNE = tf.data.AUTOTUNE

    dataset = (
        tf.data.Dataset.from_tensor_slices(
            (
                image_paths,
                labels,
            )
        )
    )

    if training:

        dataset = dataset.shuffle(
            buffer_size=len(image_paths),
            seed=SEED,
            reshuffle_each_iteration=True,
        )

    dataset = dataset.map(
        load_image,
        num_parallel_calls=AUTOTUNE,
    )

    dataset = dataset.batch(
        BATCH_SIZE
    )

    dataset = dataset.prefetch(
        AUTOTUNE
    )

    return dataset


# ============================================================
# 8. حساب Class Weights
# ============================================================

def calculate_class_weights(
    train_labels
):
    """
    حساب أوزان الفئات لمعالجة عدم توازن Dataset.
    """

    classes = np.unique(
        train_labels
    )

    weights = compute_class_weight(
        class_weight="balanced",
        classes=classes,
        y=train_labels,
    )

    class_weights = {
        int(class_id): float(weight)
        for class_id, weight
        in zip(classes, weights)
    }

    print("=" * 70)
    print("CLASS WEIGHTS")
    print("=" * 70)

    for (
        class_id,
        weight
    ) in class_weights.items():

        print(
            f"{class_id}: {weight:.4f}"
        )

    return class_weights


# ============================================================
# 9. بناء نموذج MobileNetV2
# ============================================================

def build_model(
    num_classes
):
    """
    بناء نموذج MobileNetV2
    باستخدام Transfer Learning.
    """

    tf = get_tensorflow()

    print("=" * 70)
    print("BUILDING MOBILENETV2 MODEL")
    print("=" * 70)

    data_augmentation = (
        tf.keras.Sequential(
            [
                tf.keras.layers.RandomFlip(
                    "horizontal"
                ),

                tf.keras.layers.RandomRotation(
                    0.15
                ),

                tf.keras.layers.RandomZoom(
                    0.15
                ),

                tf.keras.layers.RandomContrast(
                    0.15
                ),

                tf.keras.layers.RandomTranslation(
                    height_factor=0.05,
                    width_factor=0.05,
                ),
            ],
            name="data_augmentation",
        )
    )

    base_model = (
        tf.keras.applications.MobileNetV2(
            input_shape=(
                IMG_SIZE[0],
                IMG_SIZE[1],
                3,
            ),
            include_top=False,
            weights="imagenet",
        )
    )

    base_model.trainable = False

    inputs = tf.keras.Input(
        shape=(
            IMG_SIZE[0],
            IMG_SIZE[1],
            3,
        ),
        name="input_image",
    )

    x = data_augmentation(
        inputs
    )

    x = (
        tf.keras.applications
        .mobilenet_v2
        .preprocess_input(x)
    )

    x = base_model(
        x,
        training=False,
    )

    x = (
        tf.keras.layers
        .GlobalAveragePooling2D()(x)
    )

    x = tf.keras.layers.Dropout(
        0.35
    )(x)

    outputs = tf.keras.layers.Dense(
        num_classes,
        activation="softmax",
        name="classification",
    )(x)

    model = tf.keras.Model(
        inputs,
        outputs,
    )

    model.compile(
        optimizer=tf.keras.optimizers.Adam(
            learning_rate=1e-4
        ),
        loss=(
            "sparse_categorical_crossentropy"
        ),
        metrics=[
            "accuracy"
        ],
    )

    print(
        "\nInitial model summary:"
    )

    model.summary()

    return (
        model,
        base_model
    )


# ============================================================
# 10. Callbacks
# ============================================================

def create_callbacks():
    """
    إنشاء Callbacks لحفظ أفضل نموذج.
    """

    tf = get_tensorflow()

    checkpoint = (
        tf.keras.callbacks.ModelCheckpoint(
            filepath=str(
                BEST_MODEL_PATH
            ),
            monitor="val_accuracy",
            mode="max",
            save_best_only=True,
            verbose=1,
        )
    )

    early_stopping = (
        tf.keras.callbacks.EarlyStopping(
            monitor="val_accuracy",
            mode="max",
            patience=6,
            restore_best_weights=True,
            verbose=1,
        )
    )

    reduce_lr = (
        tf.keras.callbacks.ReduceLROnPlateau(
            monitor="val_loss",
            factor=0.3,
            patience=2,
            min_lr=1e-7,
            verbose=1,
        )
    )

    return [
        checkpoint,
        early_stopping,
        reduce_lr,
    ]


# ============================================================
# 11. التدريب - المرحلة الأولى
# ============================================================

def train_initial_stage(
    model,
    train_dataset,
    validation_dataset,
    class_weights,
):
    """
    تدريب طبقة التصنيف بينما MobileNetV2 مجمد.
    """

    print("=" * 70)
    print("STAGE 1 - TRANSFER LEARNING")
    print("=" * 70)

    callbacks = create_callbacks()

    history = model.fit(
        train_dataset,
        validation_data=validation_dataset,
        epochs=INITIAL_EPOCHS,
        class_weight=class_weights,
        callbacks=callbacks,
        verbose=1,
    )

    return history


# ============================================================
# 12. Fine-Tuning
# ============================================================

def enable_fine_tuning(
    model,
    base_model
):
    """
    فتح آخر طبقات MobileNetV2 للتدريب الدقيق.
    """

    tf = get_tensorflow()

    print("=" * 70)
    print("STAGE 2 - FINE-TUNING MOBILENETV2")
    print("=" * 70)

    base_model.trainable = True

    for layer in base_model.layers[
        :-FINE_TUNE_LAST_LAYERS
    ]:

        layer.trainable = False

    for layer in base_model.layers:

        if isinstance(
            layer,
            tf.keras.layers.BatchNormalization,
        ):

            layer.trainable = False

    model.compile(
        optimizer=tf.keras.optimizers.Adam(
            learning_rate=1e-5
        ),
        loss=(
            "sparse_categorical_crossentropy"
        ),
        metrics=[
            "accuracy"
        ],
    )

    trainable_count = sum(
        1
        for layer in model.layers
        if layer.trainable
    )

    print(
        f"\nTrainable top-level layers: "
        f"{trainable_count}"
    )

    return model


# ============================================================
# 13. Fine-Tuning Training
# ============================================================

def train_fine_tuning(
    model,
    train_dataset,
    validation_dataset,
    class_weights,
    initial_history,
):
    """
    تنفيذ المرحلة الثانية من التدريب.
    """

    print("=" * 70)
    print("TRAINING FINE-TUNING STAGE")
    print("=" * 70)

    callbacks = create_callbacks()

    history = model.fit(
        train_dataset,
        validation_data=validation_dataset,
        initial_epoch=INITIAL_EPOCHS,
        epochs=TOTAL_EPOCHS,
        class_weight=class_weights,
        callbacks=callbacks,
        verbose=1,
    )

    combined_history = {}

    for key in initial_history.history:

        combined_history[key] = (
            initial_history.history[key]
            + history.history.get(
                key,
                []
            )
        )

    return combined_history


# ============================================================
# 14. حفظ Training History
# ============================================================

def save_training_history(
    history
):
    """
    حفظ نتائج كل Epoch في CSV.
    """

    history_df = pd.DataFrame(
        history
    )

    history_df.insert(
        0,
        "epoch",
        np.arange(
            1,
            len(history_df) + 1
        ),
    )

    history_df.to_csv(
        HISTORY_PATH,
        index=False,
        encoding="utf-8-sig",
    )

    print(
        "\nTraining history saved to:"
    )

    print(
        HISTORY_PATH
    )

    return history_df


# ============================================================
# 15. Training Plots
# ============================================================

def create_training_plots(
    history
):
    """
    إنشاء رسومات Accuracy و Loss.
    """

    import matplotlib.pyplot as plt

    print("=" * 70)
    print("CREATING TRAINING PLOTS")
    print("=" * 70)

    epochs = range(
        1,
        len(history["accuracy"]) + 1,
    )

    # Accuracy
    plt.figure(
        figsize=(10, 6)
    )

    plt.plot(
        epochs,
        history["accuracy"],
        marker="o",
        label="Training Accuracy",
    )

    plt.plot(
        epochs,
        history["val_accuracy"],
        marker="o",
        label="Validation Accuracy",
    )

    plt.axvline(
        x=INITIAL_EPOCHS,
        linestyle="--",
        label="Fine-Tuning Start",
    )

    plt.xlabel("Epoch")

    plt.ylabel("Accuracy")

    plt.title(
        "SmartStock AI - Image Model Accuracy"
    )

    plt.legend()

    plt.grid(
        True,
        alpha=0.3,
    )

    plt.tight_layout()

    plt.savefig(
        PLOTS_DIR
        / "image_training_validation_accuracy.png",
        dpi=150,
    )

    plt.close()

    # Loss
    plt.figure(
        figsize=(10, 6)
    )

    plt.plot(
        epochs,
        history["loss"],
        marker="o",
        label="Training Loss",
    )

    plt.plot(
        epochs,
        history["val_loss"],
        marker="o",
        label="Validation Loss",
    )

    plt.axvline(
        x=INITIAL_EPOCHS,
        linestyle="--",
        label="Fine-Tuning Start",
    )

    plt.xlabel("Epoch")

    plt.ylabel("Loss")

    plt.title(
        "SmartStock AI - Image Model Loss"
    )

    plt.legend()

    plt.grid(
        True,
        alpha=0.3,
    )

    plt.tight_layout()

    plt.savefig(
        PLOTS_DIR
        / "image_training_validation_loss.png",
        dpi=150,
    )

    plt.close()

    print(
        "\nTraining plots saved successfully."
    )


# ============================================================
# 16. تقييم النموذج
# ============================================================

def evaluate_model(
    model,
    test_dataset,
    test_labels,
    class_names,
):
    """
    تقييم النموذج على Test Set مستقلة.
    """

    import matplotlib.pyplot as plt
    import seaborn as sns

    print("=" * 70)
    print("EVALUATING IMAGE MODEL")
    print("=" * 70)

    probabilities = model.predict(
        test_dataset,
        verbose=1,
    )

    predictions = np.argmax(
        probabilities,
        axis=1,
    )

    accuracy = accuracy_score(
        test_labels,
        predictions,
    )

    precision = precision_score(
        test_labels,
        predictions,
        average="weighted",
        zero_division=0,
    )

    recall = recall_score(
        test_labels,
        predictions,
        average="weighted",
        zero_division=0,
    )

    f1 = f1_score(
        test_labels,
        predictions,
        average="weighted",
        zero_division=0,
    )

    print("\nIMAGE MODEL RESULTS")

    print(
        f"Accuracy : {accuracy:.4f}"
    )

    print(
        f"Precision: {precision:.4f}"
    )

    print(
        f"Recall   : {recall:.4f}"
    )

    print(
        f"F1 Score : {f1:.4f}"
    )

    report = classification_report(
        test_labels,
        predictions,
        labels=np.arange(
            len(class_names)
        ),
        target_names=class_names,
        output_dict=True,
        zero_division=0,
    )

    report_df = pd.DataFrame(
        report
    ).transpose()

    report_df.to_csv(
        REPORT_PATH,
        encoding="utf-8-sig",
    )

    print(
        "\nCLASSIFICATION REPORT"
    )

    print(
        classification_report(
            test_labels,
            predictions,
            labels=np.arange(
                len(class_names)
            ),
            target_names=class_names,
            zero_division=0,
        )
    )

    cm = confusion_matrix(
        test_labels,
        predictions,
    )

    plt.figure(
        figsize=(12, 10)
    )

    sns.heatmap(
        cm,
        annot=True,
        fmt="d",
        cmap="Blues",
        xticklabels=class_names,
        yticklabels=class_names,
    )

    plt.xlabel(
        "Predicted Class"
    )

    plt.ylabel(
        "True Class"
    )

    plt.title(
        "SmartStock AI - Image Classification Confusion Matrix"
    )

    plt.xticks(
        rotation=45,
        ha="right",
    )

    plt.yticks(
        rotation=0
    )

    plt.tight_layout()

    plt.savefig(
        PLOTS_DIR
        / "image_confusion_matrix.png",
        dpi=150,
    )

    plt.close()

    print(
        "\nConfusion Matrix saved successfully."
    )

    metrics_df = pd.DataFrame(
        [
            {
                "accuracy": accuracy,
                "precision": precision,
                "recall": recall,
                "f1_score": f1,
            }
        ]
    )

    metrics_df.to_csv(
        METRICS_PATH,
        index=False,
        encoding="utf-8-sig",
    )

    return {
        "accuracy": accuracy,
        "precision": precision,
        "recall": recall,
        "f1_score": f1,
    }


# ============================================================
# 17. حفظ النموذج
# ============================================================

def save_model(
    model
):
    """
    حفظ النموذج النهائي.
    """

    model.save(
        MODEL_PATH
    )

    print("=" * 70)
    print("IMAGE MODEL SAVED")
    print("=" * 70)

    print(
        MODEL_PATH
    )


# ============================================================
# 18. Prediction لصورة واحدة
# ============================================================

def predict_image(
    image_path
):
    """
    تصنيف صورة واحدة.

    TensorFlow والنموذج يتم تحميلهما
    فقط عند استدعاء هذه الدالة.
    """

    # TensorFlow لا يتم تحميله إلا هنا
    tf = get_tensorflow()

    image_path = Path(
        image_path
    )

    if not image_path.exists():

        raise FileNotFoundError(
            f"الصورة غير موجودة:\n"
            f"{image_path}"
        )

    # --------------------------------------------------------
    # تحميل النموذج
    # --------------------------------------------------------

    model = tf.keras.models.load_model(
        MODEL_PATH
    )

    # --------------------------------------------------------
    # قراءة أسماء الفئات
    # --------------------------------------------------------

    if not CLASS_NAMES_PATH.exists():

        raise FileNotFoundError(
            "ملف أسماء الفئات غير موجود."
        )

    with open(
        CLASS_NAMES_PATH,
        "r",
        encoding="utf-8",
    ) as file:

        class_names = json.load(
            file
        )

    # --------------------------------------------------------
    # قراءة الصورة
    # --------------------------------------------------------

    image = tf.io.read_file(
        str(image_path)
    )

    image = tf.image.decode_image(
        image,
        channels=3,
        expand_animations=False,
    )

    image.set_shape(
        [
            None,
            None,
            3,
        ]
    )

    image = tf.image.resize(
        image,
        IMG_SIZE,
    )

    image = tf.cast(
        image,
        tf.float32,
    )

    image = tf.expand_dims(
        image,
        axis=0,
    )

    # --------------------------------------------------------
    # Prediction
    # --------------------------------------------------------

    probabilities = model.predict(
        image,
        verbose=0,
    )[0]

    predicted_index = int(
        np.argmax(
            probabilities
        )
    )

    predicted_class = (
        class_names[
            predicted_index
        ]
    )

    confidence = float(
        probabilities[
            predicted_index
        ]
    )

    return {
        "predicted_class": (
            predicted_class
        ),
        "confidence": confidence,
        "confidence_percentage": (
            confidence * 100
        ),
    }


# ============================================================
# 19. Main
# ============================================================

def main():

    print("=" * 70)
    print("SMARTSTOCK AI - IMAGE AI")
    print("=" * 70)

    check_dataset()

    (
        image_paths,
        labels,
        class_names,
    ) = collect_image_paths()

    (
        train_paths,
        train_labels,
        val_paths,
        val_labels,
        test_paths,
        test_labels,
    ) = split_dataset(
        image_paths,
        labels,
        class_names,
    )

    print("=" * 70)
    print("PREPARING TENSORFLOW DATASETS")
    print("=" * 70)

    train_dataset = create_dataset(
        train_paths,
        train_labels,
        training=True,
    )

    validation_dataset = create_dataset(
        val_paths,
        val_labels,
        training=False,
    )

    test_dataset = create_dataset(
        test_paths,
        test_labels,
        training=False,
    )

    class_weights = calculate_class_weights(
        train_labels
    )

    model, base_model = build_model(
        num_classes=len(
            class_names
        )
    )

    initial_history = train_initial_stage(
        model,
        train_dataset,
        validation_dataset,
        class_weights,
    )

    model = enable_fine_tuning(
        model,
        base_model,
    )

    combined_history = train_fine_tuning(
        model,
        train_dataset,
        validation_dataset,
        class_weights,
        initial_history,
    )

    save_training_history(
        combined_history
    )

    create_training_plots(
        combined_history
    )

    if BEST_MODEL_PATH.exists():

        print("=" * 70)
        print("LOADING BEST VALIDATION MODEL")
        print("=" * 70)

        tf = get_tensorflow()

        model = tf.keras.models.load_model(
            BEST_MODEL_PATH
        )

    metrics = evaluate_model(
        model,
        test_dataset,
        test_labels,
        class_names,
    )

    save_model(
        model
    )

    print("\n")
    print("=" * 70)
    print("IMAGE AI COMPLETED")
    print("=" * 70)

    print(
        f"Accuracy : "
        f"{metrics['accuracy']:.4f}"
    )

    print(
        f"Precision: "
        f"{metrics['precision']:.4f}"
    )

    print(
        f"Recall   : "
        f"{metrics['recall']:.4f}"
    )

    print(
        f"F1 Score : "
        f"{metrics['f1_score']:.4f}"
    )

    print("\nModel:")

    print(
        MODEL_PATH
    )

    print("\nClass names:")

    print(
        CLASS_NAMES_PATH
    )

    print(
        "\nImage AI is ready."
    )


# ============================================================
# تشغيل البرنامج
# ============================================================

if __name__ == "__main__":

    main()