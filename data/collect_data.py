# ============================================================
# SMARTSTOCK AI
# المرحلة 2: جمع بيانات الطقس وحفظها
# ============================================================

import requests
import pandas as pd
from pathlib import Path


# ------------------------------------------------------------
# 1. إعدادات الموقع
# ------------------------------------------------------------

latitude = 32.22
longitude = 35.26

# رابط API
url = "https://api.open-meteo.com/v1/forecast"


# ------------------------------------------------------------
# 2. البيانات التي نريد الحصول عليها
# ------------------------------------------------------------

params = {
    "latitude": latitude,
    "longitude": longitude,

    # بيانات الطقس الحالية
    "current": (
        "temperature_2m,"
        "relative_humidity_2m,"
        "precipitation,"
        "wind_speed_10m"
    ),

    "timezone": "auto"
}


# ------------------------------------------------------------
# 3. الاتصال بالـ API
# ------------------------------------------------------------

print("=" * 60)
print("SMARTSTOCK AI - WEATHER DATA COLLECTION")
print("=" * 60)

try:

    response = requests.get(
        url,
        params=params,
        timeout=10
    )

    print("HTTP Status:", response.status_code)

    # التأكد من نجاح الاتصال
    response.raise_for_status()

    # تحويل البيانات إلى JSON
    data = response.json()

    print("API Connection: SUCCESS")


    # --------------------------------------------------------
    # 4. استخراج بيانات الطقس
    # --------------------------------------------------------

    current = data["current"]

    weather_data = {
        "latitude": latitude,
        "longitude": longitude,
        "time": current["time"],
        "temperature": current["temperature_2m"],
        "humidity": current["relative_humidity_2m"],
        "precipitation": current["precipitation"],
        "wind_speed": current["wind_speed_10m"]
    }


    # --------------------------------------------------------
    # 5. تحويل البيانات إلى DataFrame
    # --------------------------------------------------------

    df = pd.DataFrame([weather_data])


    # --------------------------------------------------------
    # 6. إنشاء مجلد البيانات إذا لم يكن موجودًا
    # --------------------------------------------------------

    output_folder = Path("data/raw")
    output_folder.mkdir(
        parents=True,
        exist_ok=True
    )


    # --------------------------------------------------------
    # 7. حفظ البيانات
    # --------------------------------------------------------

    output_file = output_folder / "weather_data.csv"

    df.to_csv(
        output_file,
        index=False
    )


    # --------------------------------------------------------
    # 8. عرض النتيجة
    # --------------------------------------------------------

    print("\nWeather Data:")
    print(df)

    print("\nSaved successfully:")
    print(output_file)

    print("\n" + "=" * 60)
    print("WEATHER DATA COLLECTION COMPLETED")
    print("=" * 60)


except requests.exceptions.RequestException as e:

    print("\nAPI Connection: FAILED")
    print("Error:", e)


except Exception as e:

    print("\nUnexpected Error:")
    print(e)