#!/usr/bin/env python3
from fastapi import FastAPI
from datetime import datetime
import uvicorn

app = FastAPI()

@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.utcnow()}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)