from fastapi import FastAPI
from routers import slpkRouter  # Import the routers


import argparse


app = FastAPI()
# Include the router
app.include_router(slpkRouter.router)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", help="debug mode",
                        action='store_true', required=False)
    args = parser.parse_args()
    debugger_mode = args.d
    import uvicorn
    uvicorn.run(r"main:app", host="localhost", reload=debugger_mode,
                port=8000, workers=8)
    pass
