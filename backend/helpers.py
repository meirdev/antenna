import contextlib
from typing import Any, AsyncIterator, TypedDict

import asyncpg
import googlemaps
import pandas as pd
import pyproj

from settings import settings

pool = asyncpg.create_pool(settings.pg_dns.unicode_string())

gmaps = googlemaps.Client(key=settings.google_maps_api_key.get_secret_value())


@contextlib.asynccontextmanager
async def db() -> AsyncIterator[asyncpg.Connection]:
    connection = await asyncpg.connect(settings.pg_dns.unicode_string())
    yield connection
    await connection.close()


async def init_db(session: asyncpg.Connection) -> None:
    await session.execute(
        """
        CREATE TABLE IF NOT EXISTS antennas (
            id SERIAL PRIMARY KEY,
            info JSONB,
            location GEOGRAPHY(POINT, 4326)
        );
        """
    )


class Row(TypedDict):
    id: int
    raw: str  # JSON
    location: tuple[int, int]


def read_file(path: str) -> list[Row]:
    dataframe = pd.read_excel(path)

    transformer = pyproj.Transformer.from_crs(
        "+proj=tmerc +lat_0=31.73439361111111 +lon_0=35.20451694444445 +k=1.0000067 +x_0=219529.584 +y_0=626907.39 +ellps=GRS80 +towgs84=-48,55,52,0,0,0,0 +units=m +no_defs",
        "EPSG:4326",
    )

    rows = []

    for i, row in dataframe.iterrows():
        data = {}
        data["id"] = row["ID"]
        data["raw"] = dataframe.loc[i].to_json()
        data["location"] = transformer.transform(row["X_ITM"], row["Y_ITM"])

        rows.append(data)

    return rows


async def update_db(session: asyncpg.Connection, data: list[Row]) -> None:
    await session.execute("TRUNCATE antennas;")

    def to_args(row: Row):
        x, y = row["location"]

        return (row["id"], row["raw"], f"SRID=4326;POINT({x} {y})")

    await session.executemany(
        "INSERT INTO antennas (id, info, location) VALUES ($1, $2, $3)",
        list(map(to_args, data)),
    )


def search_address(query: str) -> list[Any]:
    return gmaps.geocode(query, language="he")


async def nearest_antennas(
    session: asyncpg.Connection, lng: float, lat: float, limit: int = 10
) -> list[dict[str, Any]]:
    sql = f"""
    SELECT
        *,
        ST_X(location::geometry) as lng,
        ST_Y(location::geometry) as lat,
        location <-> 'SRID=4326;POINT({lat} {lng})'::geometry AS distance
    FROM antennas
    ORDER BY distance ASC LIMIT {limit}
    """

    return list(map(dict, await session.fetch(sql)))
