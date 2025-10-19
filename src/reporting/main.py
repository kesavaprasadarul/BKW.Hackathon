#!/usr/bin/env python3
"""
Gemini Report Generator - Main Entry Point
"""

import sys
from pathlib import Path


sys.path.insert(0, str(Path(__file__).parent))

from app import main

if __name__ == "__main__":
    sys.exit(main())
