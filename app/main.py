import os
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.agent import run_stock_analysis

load_dotenv()

app = FastAPI(title="NSE AI Stock Agent API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/api/analyze/{symbol}")
def analyze_stock(symbol: str):
  try:
    analysis = run_stock_analysis(symbol)
    return analysis
  except Exception as e:
    raise HTTPException(status_code=400, detail=str(e))


@app.get("/")
def read_root():
  from fastapi.responses import FileResponse

  return FileResponse("static/index.html")
