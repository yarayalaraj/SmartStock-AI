import sys

LIBRARIES = r"C:\Users\yara\py y\proj12\.venv\Lib\site-packages"

if LIBRARIES not in sys.path:
    sys.path.insert(0, LIBRARIES)
