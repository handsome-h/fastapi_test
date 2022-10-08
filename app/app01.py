# app/app01.py
from fastapi import APIRouter

router1 = APIRouter(prefix="/router1")

# 以后访问的时候要通过 /router/v1 来访问
@router1.get("/v1")
async def v1():
    return {"message": "hello world"}
