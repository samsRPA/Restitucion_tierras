from fastapi import status
from fastapi.responses import JSONResponse
from fastapi import APIRouter, Depends, HTTPException
from dependency_injector.wiring import inject, Provide
from app.dependencies.Dependencies import Dependencies


from app.application.dto.OfficeDto import OfficeDto
from app.domain.interfaces.IOfficesLandRestitution import IOfficesLandRestitution



router = APIRouter()

@router.post(
    "/offices/queues_land_restitution",
    response_model=OfficeDto,
    response_model_exclude_none=True,
    status_code=status.HTTP_202_ACCEPTED
)
@inject
async def publishAllOffices(
        offices_land_restitution_service: IOfficesLandRestitution = Depends(Provide[Dependencies.offices_land_restitution_service])
):
    try:
        raw_offices= await offices_land_restitution_service.publish_offices()
        return JSONResponse(status_code=status.HTTP_202_ACCEPTED,
                            content="✔️ Mensajes enviados a las cola de restitucion de tierras")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


