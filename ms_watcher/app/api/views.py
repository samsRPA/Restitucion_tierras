from fastapi import APIRouter

from app.api.routes import land_restitution_routes

apiRouter = APIRouter(prefix="/api/v1")
apiRouter.include_router(land_restitution_routes.router, tags=["keys"])

def getApiRouter():
    return apiRouter