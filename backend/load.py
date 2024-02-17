import asyncio
import sys

import helpers


async def main() -> None:
    path = sys.argv[1]

    async with helpers.db() as session:
        await helpers.init_db(session)

        data = helpers.read_file(path)

        await helpers.update_db(session, data)


if __name__ == "__main__":
    asyncio.run(main())
