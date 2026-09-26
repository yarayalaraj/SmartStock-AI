# ============================================================
# SMARTSTOCK AI
# المرحلة 1: اختبار الاتصال بـ Weather API
# ============================================================

import requests

print("=" * 50)
print("SMARTSTOCK AI - API TEST")
print("=" * 50)

# إحداثيات تقريبية لمدينة نابلس
latitude = 32.22
longitude = 35.26

# رابط Open-Meteo
url = "https://api.open-meteo.com/v1/forecast"

# البيانات التي نطلبها من API
params = {
    "latitude": latitude,
    "longitude": longitude,
    "current": "temperature_2m,relative_humidity_2m,precipitation,wind_speed_10m",
    "timezone": "auto"
}

try:

    # إرسال الطلب إلى API
    response = requests.get(url, params=params, timeout=10)

    print("HTTP Status:", response.status_code)

    # التأكد من نجاح الاتصال
    response.raise_for_status()

    # تحويل الاستجابة إلى JSON
    data = response.json()

    print("\nAPI Connection: SUCCESS")

    # استخراج بيانات الطقس الحالية
    current = data["current"]

    print("\nCurrent Weather:")
    print("Temperature:", current["temperature_2m"], "°C")
    print("Humidity:", current["relative_humidity_2m"], "%")
    print("Precipitation:", current["precipitation"], "mm")
    print("Wind Speed:", current["wind_speed_10m"], "km/h")

    print("\n" + "=" * 50)
    print("API TEST COMPLETED SUCCESSFULLY")
    print("=" * 50)

except requests.exceptions.RequestException as e:

    print("\nAPI Connection: FAILED")
    print("Error:", e)