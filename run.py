"""Portable launcher, including platforms that supply a PORT environment variable."""

import os

import uvicorn

from config import load_settings

if __name__ == "__main__":
    load_settings()
    uvicorn.run("main:app", host="0.0.0.0", port=int(os.getenv("PORT", "8000")), access_log=False)
