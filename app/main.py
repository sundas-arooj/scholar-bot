import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from app.routers.router import router

app = FastAPI(title="ScholarBot", description="A Research Paper Query Bot")

# Include the router after the root endpoint
app.include_router(router)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def read_root():
    return FileResponse("static/index.html")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
