from fastapi import FastAPI
from app.routes import estimate, jobs

app = FastAPI(
    title="EasyFind Property Formatter",
    description="API for property normalization, image enhancement, and WhatsApp formatting",
    version="1.0.0"
)

# Include routers
app.include_router(estimate.router, prefix="/api", tags=["estimate"])
app.include_router(jobs.router, prefix="/api", tags=["jobs"])

@app.get("/health")
def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
