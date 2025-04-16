from fastapi import FastAPI
from routers import slpkRouter  # Import the routers
app = FastAPI()
# Include the router
app.include_router(slpkRouter.router)


if __name__ == '__main__':
    import uvicorn

    uvicorn.run(r"main:app", host="localhost", port=8000, workers=8)
