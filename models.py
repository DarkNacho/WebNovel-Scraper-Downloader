import re
from pydantic import BaseModel, field_validator, model_validator
from typing import List, Optional


def clean_text(text: str) -> str:
    # Remove unwanted characters and clean the description
    text = text.replace("\\", "")
    text = text.replace("\r\n", " ")
    text = re.sub(r"\s+", " ", text).strip()
    return text


class BaseModelClean(BaseModel):
    @field_validator("*", mode="before")
    def clean_strings(cls, v):
        if isinstance(v, str):
            return clean_text(v)
        if isinstance(v, dict):
            return {
                k: clean_text(val) if isinstance(val, str) else val
                for k, val in v.items()
            }
        return v


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


class ChapterInfo(BaseModelClean):
    chapterId: str
    chapterName: str
    chapterIndex: int
    preChapterId: str
    preChapterName: str
    nextChapterId: str
    nextChapterName: str
    contents: List[Content]
    isAuth: int
    firstChapterId: str

    def get_full_content(self) -> str:
        def wrap_in_p(content: str) -> str:
            if not content.strip().startswith("<p>") and not content.strip().endswith(
                "</p>"
            ):
                return f"<p>{content}</p>"
            return content

        return "\n".join([wrap_in_p(content.content) for content in self.contents])


class BookInfo(BaseModelClean):
    bookId: str
    bookName: str
    bookCover: str = None
    authorName: str
    authorId: str
    totalChapterNum: int
    description: Optional[str] = None
    firstChapterId: Optional[str] = None

    @model_validator(mode="after")
    def set_book_cover(cls, values):
        values.bookCover = f"https://book-pic.webnovel.com/bookcover/{values.bookId}"
        return values

    @field_validator("totalChapterNum", mode="before")
    def validate_total_chapter_num(cls, v, values):
        if v is None:
            return values.get("chapterNum")
        return v
