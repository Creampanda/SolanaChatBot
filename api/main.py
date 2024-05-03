from fastapi import FastAPI
import uvicorn
from app.config import PORT
from app.router import router

# Initialize the FastAPI app
app = FastAPI()

# Include router from the routers module
app.include_router(router)


# Function to run the app
def start():
    uvicorn.run("main:app", host="0.0.0.0", port=PORT)


# Main guard for running the application
if __name__ == "__main__":
    start()
