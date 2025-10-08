import sys
from pathlib import Path

# Añadir la carpeta 'backend' al sys.path para que 'import app' funcione
ROOT = Path(__file__).resolve().parents[1]  # backend/
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
