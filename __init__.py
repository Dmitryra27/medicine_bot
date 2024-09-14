from aiogram.filters import BaseFilter
from aiogram.types import Message, CallbackQuery


from aiogram.filters import BaseFilter
from aiogram.types import Message, CallbackQuery
class Text(BaseFilter):
    def __init__(self, text: str = None, text_contains: str = None, text_startswith: str = None, text_endswith: str = None):
        self.text = text
        self.text_contains = text_contains
        self.text_startswith = text_startswith
        self.text_endswith = text_endswith
    async def __call__(self, message: Message | CallbackQuery) -> bool:
        text = message.text or message.data
        if self.text is not None and text == self.text:
            return True
        if self.text_contains is not None and self.text_contains in text:
            return True
        if self.text_startswith is not None and text.startswith(self.text_startswith):
            return True
        if self.text_endswith is not None and text.endswith(self.text_endswith):
            return True
        return False
