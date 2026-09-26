
# ============================================================
# SMARTSTOCK AI
# تحميل Dataset: RealWaste
# المصدر: UCI Machine Learning Repository
# ============================================================

from pathlib import Path
import urllib.request
import zipfile
import shutil
import os


# ------------------------------------------------------------
# 1. تحديد مكان حفظ Dataset
# ------------------------------------------------------------
# نستخدم القرص H لأن Dataset حجمها كبير تقريبًا 656.6 MB،
# وبالتالي لا نريد استهلاك المساحة المحدودة على القرص C.

DATA_DIR = Path(r"H:\SmartStockData\RealWaste")

# إنشاء المجلد إذا لم يكن موجودًا
DATA_DIR.mkdir(parents=True, exist_ok=True)


# ------------------------------------------------------------
# 2. رابط Dataset من UCI
# ------------------------------------------------------------
# هذا هو ملف ZIP الخاص بـ RealWaste.
# يتم تنزيله من مستودع UCI الرسمي.

DOWNLOAD_URL = (
    "https://archive.ics.uci.edu/static/public/908/"
    "realwaste.zip"
)

# اسم الملف المؤقت الذي سيتم تنزيله
ZIP_FILE = DATA_DIR / "realwaste.zip"


# ------------------------------------------------------------
# 3. بدء التحميل
# ------------------------------------------------------------

print("=" * 70)
print("SMARTSTOCK AI - REALWASTE DATASET DOWNLOAD")
print("=" * 70)

print("\n📁 مكان الحفظ:")
print(DATA_DIR)

print("\n🌐 مصدر البيانات:")
print("UCI Machine Learning Repository")

print("\n⬇️ بدء تحميل RealWaste...")
print("قد يستغرق التحميل بعض الوقت لأن حجم البيانات كبير.\n")


# ------------------------------------------------------------
# 4. تحميل الملف
# ------------------------------------------------------------

try:

    # إذا كان الملف موجودًا مسبقًا، لن نعيد تحميله
    if ZIP_FILE.exists():

        print("⚠️ ملف ZIP موجود مسبقًا:")
        print(ZIP_FILE)

        print("\nسيتم استخدام الملف الموجود بدل إعادة تحميله.")

    else:

        # إنشاء اتصال بالملف وتحميله
        urllib.request.urlretrieve(
            DOWNLOAD_URL,
            ZIP_FILE
        )

        print("\n✅ تم تحميل Dataset بنجاح.")
        print("الملف:")
        print(ZIP_FILE)


except Exception as e:

    print("\n❌ حدث خطأ أثناء تحميل Dataset.")
    print("تفاصيل الخطأ:")
    print(e)

    raise SystemExit(1)


# ------------------------------------------------------------
# 5. التحقق من وجود ملف ZIP
# ------------------------------------------------------------

if not ZIP_FILE.exists():

    print("\n❌ لم يتم العثور على ملف ZIP بعد التحميل.")

    raise SystemExit(1)


# الحصول على حجم الملف بالميجابايت
file_size_mb = ZIP_FILE.stat().st_size / (1024 * 1024)

print("\n📦 حجم الملف:")
print(f"{file_size_mb:.2f} MB")


# ------------------------------------------------------------
# 6. استخراج Dataset
# ------------------------------------------------------------

print("\n📂 بدء استخراج الصور...")

try:

    with zipfile.ZipFile(ZIP_FILE, "r") as zip_ref:

        # استخراج جميع الملفات
        zip_ref.extractall(DATA_DIR)

    print("✅ تم استخراج Dataset بنجاح.")


except zipfile.BadZipFile:

    print("\n❌ الملف الذي تم تنزيله ليس ZIP صالحًا.")

    raise SystemExit(1)

except Exception as e:

    print("\n❌ حدث خطأ أثناء استخراج Dataset.")
    print("تفاصيل الخطأ:")
    print(e)

    raise SystemExit(1)


# ------------------------------------------------------------
# 7. البحث عن مجلد RealWaste
# ------------------------------------------------------------

print("\n🔎 البحث عن مجلد الصور...")


# UCI قد تستخرج Dataset داخل مجلد مثل:
# realwaste-main/RealWaste
#
# لذلك نبحث عن مجلد اسمه RealWaste تلقائيًا.

possible_dirs = list(DATA_DIR.rglob("RealWaste"))


if len(possible_dirs) == 0:

    print("\n⚠️ لم يتم العثور على مجلد باسم RealWaste.")

    print("المجلدات الموجودة حاليًا:")

    for item in DATA_DIR.iterdir():
        print(" -", item)

    raise SystemExit(1)


# أول مجلد RealWaste يتم العثور عليه
SOURCE_DIR = possible_dirs[0]

print("\n✅ تم العثور على Dataset هنا:")
print(SOURCE_DIR)


# ------------------------------------------------------------
# 8. الفئات التسع في RealWaste
# ------------------------------------------------------------

EXPECTED_CLASSES = [
    "Cardboard",
    "Food Organics",
    "Glass",
    "Metal",
    "Miscellaneous Trash",
    "Paper",
    "Plastic",
    "Textile Trash",
    "Vegetation"
]


# ------------------------------------------------------------
# 9. التحقق من وجود الفئات
# ------------------------------------------------------------

print("\n🔎 التحقق من Classes...")

found_classes = []

for class_name in EXPECTED_CLASSES:

    class_path = SOURCE_DIR / class_name

    if class_path.exists() and class_path.is_dir():

        found_classes.append(class_name)

        # حساب عدد الصور داخل الفئة
        image_count = len(
            list(class_path.glob("*.jpg"))
        )

        print(
            f"✅ {class_name}: "
            f"{image_count} images"
        )

    else:

        print(
            f"❌ لم يتم العثور على: "
            f"{class_name}"
        )


# ------------------------------------------------------------
# 10. التأكد من اكتمال Dataset
# ------------------------------------------------------------

if len(found_classes) != len(EXPECTED_CLASSES):

    print("\n⚠️ Dataset لم يتم العثور عليها بالشكل المتوقع.")

    print(
        f"عدد الفئات الموجودة: "
        f"{len(found_classes)} / "
        f"{len(EXPECTED_CLASSES)}"
    )

else:

    print("\n✅ جميع الفئات التسع موجودة.")


# ------------------------------------------------------------
# 11. نقل Dataset إلى المسار النهائي
# ------------------------------------------------------------
# نريد أن يكون المسار النهائي:
#
# H:\SmartStockData\RealWaste
#
# وليس:
#
# H:\SmartStockData\RealWaste\realwaste-main\RealWaste
#
# لذلك إذا كانت Dataset داخل مجلد فرعي،
# سننسخ الفئات إلى المسار الرئيسي.

if SOURCE_DIR.resolve() != DATA_DIR.resolve():

    print("\n📦 تجهيز المسار النهائي للبيانات...")

    for class_name in EXPECTED_CLASSES:

        source_class = SOURCE_DIR / class_name
        target_class = DATA_DIR / class_name

        # إذا كانت الفئة موجودة بالفعل في المكان النهائي
        # فلن نقوم بنسخها مرة أخرى.
        if target_class.exists():

            print(
                f"⚠️ موجودة مسبقًا: "
                f"{class_name}"
            )

            continue

        if source_class.exists():

            shutil.copytree(
                source_class,
                target_class
            )

            print(
                f"✅ تم نقل: "
                f"{class_name}"
            )


# ------------------------------------------------------------
# 12. التحقق النهائي من المسار
# ------------------------------------------------------------

print("\n" + "=" * 70)
print("FINAL DATASET CHECK")
print("=" * 70)

total_images = 0

for class_name in EXPECTED_CLASSES:

    class_path = DATA_DIR / class_name

    if class_path.exists():

        count = len(
            list(class_path.glob("*.jpg"))
        )

        total_images += count

        print(
            f"{class_name:25s} : "
            f"{count:4d} images"
        )

    else:

        print(
            f"{class_name:25s} : NOT FOUND"
        )


print("\n" + "-" * 70)

print(
    f"إجمالي الصور التي تم العثور عليها: "
    f"{total_images}"
)


# ------------------------------------------------------------
# 13. حذف الملف المضغوط لتوفير مساحة
# ------------------------------------------------------------
# بعد نجاح استخراج الصور، يمكن حذف ZIP.
#
# هذا مهم لأن الملف المضغوط حجمه كبير،
# ولا نحتاج إلى الاحتفاظ بنسختين من Dataset.

if total_images > 0:

    try:

        ZIP_FILE.unlink()

        print("\n🗑️ تم حذف ملف ZIP لتوفير مساحة التخزين.")

    except Exception as e:

        print(
            "\n⚠️ لم يتم حذف ملف ZIP:"
        )

        print(e)


# ------------------------------------------------------------
# 14. النتيجة النهائية
# ------------------------------------------------------------

print("\n" + "=" * 70)
print("✅ REALWASTE DATASET IS READY")
print("=" * 70)

print("\nالمسار النهائي:")

print(DATA_DIR)

print("\nيمكن الآن تشغيل Image AI باستخدام MobileNetV2.")
print("=" * 70)

