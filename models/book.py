from typing import List, Optional

from pydantic import field_validator
from models.base import BaseChapter, BaseInfo, BaseModelClean


class Content(BaseModelClean):
    contentId: str
    content: str
    appId: int
    userId: int
    paragraphId: str
    likeAmount: int
    contentAmount: int
    userName: str
    UUT: int
    isLiked: int


class Chapter(BaseChapter):
    contents: List[Content]
    firstChapterId: str

    def get_full_content(self) -> str:
        def wrap_in_p(content: str) -> str:
            if not content.strip().startswith("<p>") and not content.strip().endswith(
                "</p>"
            ):
                return f"<p>{content}</p>"
            return content

        return "\n".join([wrap_in_p(content.content) for content in self.contents])


class Info(BaseInfo):
    bookId: str
    bookName: str
    authorId: str
    totalChapterNum: int
    description: Optional[str] = None
    firstChapterId: Optional[str] = None

    def __init__(self, **data):
        super().__init__(**data)
        self.name = self.bookName
        self.cover = f"https://book-pic.webnovel.com/bookcover/{self.bookId}"

    # @model_validator(mode="after")
    # def set_book_cover(cls, values):
    #    values.bookCover = f"https://book-pic.webnovel.com/bookcover/{values.bookId}"
    #    return values

    @field_validator("totalChapterNum", mode="before")
    def validate_total_chapter_num(cls, v, values):
        if v is None:
            return values.get("chapterNum")
        return v
