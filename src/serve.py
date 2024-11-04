import os
from pathlib import Path

import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from logger import get_logger

load_dotenv()

# Define base paths
BASE_DIR = Path(__file__).parent
PROJECT_ROOT = BASE_DIR.parent

# Define directory paths
OUTPUT_DIR = Path(os.getenv("CHEATSHEET_OUTPUT_DIR") or PROJECT_ROOT / "output")

logging = get_logger()

app = FastAPI()

logging.info(f"OUTPUT_DIR: {OUTPUT_DIR}")

app.mount("/", StaticFiles(directory=f"{OUTPUT_DIR}", html=True))

if __name__ == "__main__":

    uvicorn.run("serve:app", host="0.0.0.0", port=5000, reload=True)
