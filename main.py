import sys
from pathlib import Path

_root = Path(__file__).resolve().parent
_backend_dir = _root / "backend"
_scribe2fhir_src = _root / "scribe2fhir" / "python"
sys.path.insert(0, str(_root))
sys.path.insert(0, str(_backend_dir))
if _scribe2fhir_src.is_dir():
    sys.path.insert(0, str(_scribe2fhir_src))

import importlib.util
_spec = importlib.util.spec_from_file_location("_backend_main", _backend_dir / "main.py")
_backend_main = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_backend_main)
app = _backend_main.app
