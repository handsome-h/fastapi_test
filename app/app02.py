# app/app01.py
from fastapi import APIRouter

router2 = APIRouter(prefix="/router2")

# 以后访问的时候要通过 /router/v1 来访问
@router2.get("/v1")
async def v1():
    return {"message": "hello world"}
