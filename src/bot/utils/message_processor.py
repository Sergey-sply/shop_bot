import aiofiles
from aiogram.types import InputMediaPhoto, BufferedInputFile


async def get_media_obj(image_path: str, caption: str) -> InputMediaPhoto:
    async with aiofiles.open(image_path, "rb") as f:
        photo_bytes = await f.read()

    if photo_bytes:
        file = BufferedInputFile(
            file=photo_bytes,
            filename=image_path.split("\\")[-1]
        )

        return InputMediaPhoto(
            media=file,
            caption=caption
        )