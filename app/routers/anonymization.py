import logging
from fastapi import APIRouter, Request, HTTPException, status

from app.models.anonymization import AnonymizeRequest, AnonymizeResult, DeanonymizeRequest
from app.services.anonymizer import AnonymizerService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/system", tags=["anonymization"])

@router.post(
    "/anonymize",
    status_code=status.HTTP_200_OK,
    summary="Anonymize text containing PII"
)
async def anonymize(req: AnonymizeRequest, request: Request):
    if not hasattr(request.app.state, "anonymizer"):
        request.app.state.anonymizer = AnonymizerService()
        
    try:
        return request.app.state.anonymizer.anonymize(req)
    except ValueError as e:
        logger.warning(f"Invalid anonymization request: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Anonymization failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Anonymization failed: {str(e)}"
        )

@router.post(
    "/deanonymize",
    status_code=status.HTTP_200_OK,
    summary="Deanonymize previously anonymized text"
)
async def deanonymize(req: DeanonymizeRequest, request: Request):
    if not hasattr(request.app.state, "anonymizer"):
        request.app.state.anonymizer = AnonymizerService()
        
    try:
        return request.app.state.anonymizer.deanonymize(req)
    except ValueError as e:
        logger.warning(f"Invalid deanonymization request: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Deanonymization failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Deanonymization failed: {str(e)}"
        )

@router.get(
    "/anonymizers",
    status_code=status.HTTP_200_OK,
    summary="Get available anonymizers"
)
async def anonymizers(request: Request):
    if not hasattr(request.app.state, "anonymizer"):
        request.app.state.anonymizer = AnonymizerService()
        
    return request.app.state.anonymizer.get_anonymizers()

@router.get(
    "/deanonymizers",
    status_code=status.HTTP_200_OK,
    summary="Get available deanonymizers"
)
async def deanonymizers(request: Request):
    if not hasattr(request.app.state, "anonymizer"):
        request.app.state.anonymizer = AnonymizerService()
        
    return request.app.state.anonymizer.get_deanonymizers()
