import asyncio
from sqlalchemy import select
from app.db.session import async_session_factory
from app.models.listing import Listing

async def main():
    async with async_session_factory() as session:
        result = await session.execute(select(Listing.public_id, Listing.deleted_at, Listing.status))
        for row in result:
            print(row)

asyncio.run(main())
