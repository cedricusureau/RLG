# neural_battler/__init__.py
import sys
import os
from pathlib import Path

# Ajouter le chemin racine au PYTHONPATH pour faciliter les imports
package_root = Path(__file__).parent
sys.path.insert(0, str(package_root))

# Version du package
__version__ = "0.1.0"