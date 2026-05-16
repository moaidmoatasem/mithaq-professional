#!/usr/bin/env python3
"""
DEPRECATED — cherenkov_web.py (Flask dashboard)

Flask has been retired. The web dashboard is now served by the FastAPI
server at packages/cherenkov/api/main.py.

To start the dashboard:
    uvicorn cherenkov.api.main:app --host 127.0.0.1 --port 8000

Then open: http://localhost:8000/

This file is kept only to avoid breaking any external references.
It will be removed in v1.2.0.
"""

import sys


def main() -> None:
    print(
        "\n[CHERENKOV] cherenkov_web.py is deprecated.\n"
        "The dashboard is now served by FastAPI:\n\n"
        "  uvicorn cherenkov.api.main:app --host 127.0.0.1 --port 8000\n\n"
        "Then open: http://localhost:8000/\n"
    )
    sys.exit(0)


if __name__ == "__main__":
    main()
