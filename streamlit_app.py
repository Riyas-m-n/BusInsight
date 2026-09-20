"""
BusInsight Root Application Entry Point for Deployment.
Redirects to the modular App/app.py application shell.
"""
import sys
from pathlib import Path

# Ensure repository root is in sys.path
ROOT_DIR = Path(__file__).resolve().parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from App.app import main

if __name__ == "__main__":
    main()
