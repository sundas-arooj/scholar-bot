import uvicorn
from fastapi import FastAPI
from app.routers.router import router

app = FastAPI(title="ScholarBot", description="A Research Paper Query Bot")

# Include the router after the root endpoint
app.include_router(router)

@app.get("/")
def read_root():
    return {"message": "Welcome to ScholarBot!"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
