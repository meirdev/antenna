import contextlib
from typing import Annotated, AsyncIterator

import asyncpg
from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware

import helpers


@contextlib.asynccontextmanager
async def lifespan(app: FastAPI):
    async with helpers.pool as pool_:
        app.state.pool = pool_
        yield


async def db() -> AsyncIterator[asyncpg.Connection]:
    if isinstance(app.state.pool, asyncpg.Pool):
        async with app.state.pool.acquire() as connection:
            yield connection


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/search-address")
async def search_address(query: str):
    return helpers.search_address(query)


@app.get("/nearest-antennas")
async def get_nearest_antennas(
    session: Annotated[asyncpg.Connection, Depends(db)],
    lng: float,
    lat: float,
    limit: int = 10,
):
    return await helpers.nearest_antennas(session, lng, lat, limit)
