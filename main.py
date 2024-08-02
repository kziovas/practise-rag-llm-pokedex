from fastapi import FastAPI
from app.api.routers import router
from app.services.core_services import init_core_services
from fastapi.staticfiles import StaticFiles


app = FastAPI()
init_core_services()


# Include the router from api.py
app.include_router(router)

# Mount directories for service resources
app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/assets", StaticFiles(directory="assets"), name="assets")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
