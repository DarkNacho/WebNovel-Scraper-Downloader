import re
from pydantic import BaseModel, field_validator


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


class BaseChapter(BaseModelClean):
    chapterId: str
    chapterName: str
    chapterIndex: int
    preChapterId: str
    preChapterName: str
    nextChapterId: str
    nextChapterName: str
    isAuth: int
    chapterLevel: int
    userLevel: int
    publishTime: int
    updateTime: int


class BaseInfo(BaseModelClean):
    name: str = None
    cover: str = None
    authorName: str
    languageCode: int
    languageName: str
    description: str
    firstChapterId: str
    firstChapterName: str
