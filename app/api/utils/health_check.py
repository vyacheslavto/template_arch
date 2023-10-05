from fastapi import APIRouter
from starlette.responses import Response
from starlette.status import HTTP_200_OK

router = APIRouter()


@router.get("/", status_code=HTTP_200_OK)
async def default_k8s_health_check() -> Response:
    """Хелсчек для k8s. Всегда отдает OK. Нужен, чтоб понять жив ли под.

    Returns:
        Response
    """
    return Response(content="OK", status_code=HTTP_200_OK)
