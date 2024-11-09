from typing import List
from models.base import BaseModelClean, BaseChapter, BaseInfo


class Page(BaseModelClean):
    pageId: str
    height: int
    width: int
    url: str


class Chapter(BaseChapter):
    pageCount: int
    nextAmpUrl: str
    chapterPage: List[Page]


class Info(BaseInfo):
    comicId: str
    comicName: str
    chapterNum: int
    publisher: str

    def __init__(self, **data):
        super().__init__(**data)
        self.name = self.comicName
        self.cover = f"https://book-pic.webnovel.com/bookcover/{self.comicId}"
