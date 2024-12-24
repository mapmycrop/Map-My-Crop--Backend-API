from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import text


from db import get_db
from cache import get_redis

route = APIRouter(prefix="/status", tags=["Status"], include_in_schema=False)


@route.get("/db")
def status_db(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
        return {"status": "connected"}
    except Exception as e:
        print("DB not connceted", e)
        raise HTTPException(
            status_code=status.HTTP_204_NO_CONTENT,
            detail="Not connected. Check logs",
        )


@route.get("/cache")
def status_cache(cache=Depends(get_redis)):
    try:
        response = cache.ping()
        if response:
            return {"status": "connected"}
        else:
            return {"status": "not connected"}
    except Exception as e:
        print("Cache not connceted", e)
        raise HTTPException(
            status_code=status.HTTP_204_NO_CONTENT,
            detail="Not connected. Check logs",
        )
