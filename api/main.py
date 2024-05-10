from fastapi import FastAPI
import uvicorn
from app.config import PORT
from app.router import router

# Initialize the FastAPI app
app = FastAPI()

# Include router from the routers module
app.include_router(router)


def start():
    """
    Function to start the FastAPI application.

    Notes:
        This function runs the FastAPI application using uvicorn with the specified host and port.
    """
    uvicorn.run("main:app", host="0.0.0.0", port=PORT, reload=True)


if __name__ == "__main__":
    start()
