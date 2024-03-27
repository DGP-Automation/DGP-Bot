from fastapi import APIRouter, Depends
from dgp_utils.dgp_tools import verify_generic_token
from operater import get_access_token

router = APIRouter(prefix="/admin", dependencies=[Depends(verify_generic_token)])


@router.get("/pat")
async def get_pat():
    pat = get_access_token()
    return {"pat": pat}
