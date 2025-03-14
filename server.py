import json
from aiohttp import web
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from models import Session, Advertisement, close_orm, init_orm

app = web.Application()


async def orm_context(app: web.Application):
    print("start")
    await init_orm()
    yield
    await close_orm()
    print("finish")


@web.middleware
async def session_middleware(request: web.Request, handler):
    async with Session() as session:
        request.session = session
        response = await handler(request)
        return response


app.cleanup_ctx.append(orm_context)
app.middlewares.append(session_middleware)


def get_error(err_cls, message: str | dict | list):
    error_message = json.dumps({"error": message})
    return err_cls(text=error_message, content_type="application/json")


async def get_advertisement_by_id(advertisement_id: int, session: AsyncSession) -> Advertisement:
    advertisement = await session.get(Advertisement, advertisement_id)
    if advertisement is None:
        error = get_error(web.HTTPNotFound, "advertisement not found")
        raise error
    return advertisement


class AdvertisementView(web.View):

    @property
    def advertisement_id(self) -> int:

        return int(self.request.match_info["advertisement_id"])

    @property
    def session(self) -> AsyncSession:
        return self.request.session

    async def get(self):
        advertisement = await get_advertisement_by_id(self.advertisement_id, self.session)
        return web.json_response(advertisement.info)

    async def post(self):
        data = await self.request.json()
        advertisement = Advertisement(**data)
        self.session.add(advertisement)
        await self.session.commit()
        return web.json_response(advertisement.info)

    async def delete(self):
        advertisement = await get_advertisement_by_id(self.advertisement_id, self.session)
        await self.session.delete(advertisement)
        await self.session.commit()
        return web.json_response({"status": "deleted"})


app.add_routes(
    [
        web.post("/api/v1/advertisement", AdvertisementView),
        web.get("/api/v1/advertisement/{advertisement_id:[0-9]+}", AdvertisementView),
        web.delete("/api/v1/advertisement/{advertisement_id:[0-9]+}", AdvertisementView),
    ]
)

web.run_app(app)

