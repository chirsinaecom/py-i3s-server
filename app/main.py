from fastapi import FastAPI
from routers import slpkRouter  # Import the routers

if __name__ == '__main__':
    import uvicorn
    app = FastAPI()
    # Include the router
    app.include_router(slpkRouter.router)
    uvicorn.run(app, host="localhost", port=8000)
