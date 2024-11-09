import re
from pydantic import BaseModel, field_validator, model_validator, validator
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


class AuthorItem(BaseModelClean):
    id: Optional[int] = None
    userId: Optional[int] = None
    UUT: Optional[str] = None
    guid: Optional[int] = None
    name: Optional[str] = None


class TagInfo(BaseModelClean):
    id: int
    tagName: str
    likeCount: int
    isLiked: bool = False

    @field_validator("id", mode="before")
    def validate_id(cls, v, values):
        if v is None:
            return values.get("tagId")
        return v

    @field_validator("likeCount", mode="before")
    def validate_likeCount(cls, v, values):
        if v is None:
            return values.get("likeNums")
        return v

    @field_validator("isLiked", mode="before")
    def validate_isLiked(cls, v, values):
        if v is None:
            return values.get("like", 0)
        if isinstance(v, int):
            return bool(v)
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
    vipStatus: int
    price: int
    originalPrice: int
    discountInfo: str
    chapterLevel: int
    userLevel: int
    contents: List[Content]
    isAuth: int
    batchUnlockStatus: int
    isRichFormat: int
    announcementItems: List
    groupItems: List
    editorItems: List
    translatorItems: List
    firstChapterId: str
    # chapterReviewItems: List # This is not needed
    firstChapterIndex: int
    reviewTotal: int
    notes: dict
    orderIndex: int
    noArchive: int
    transRating: int
    banner: dict
    adPosition: dict
    encryptType: int
    encryptKeyPool: str
    encryptVersion: int
    nextChapterEncrypt: dict
    fastPassNum: int
    isToApp: bool
    updateTime: int
    publishTime: int

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
    actionStatus: int
    type: Optional[int] = None
    languageCode: int
    languageName: str
    bookType: int
    reviewTotal: Optional[int] = None
    checkLevel: int
    totalPreChapterNum: Optional[int] = None
    translateMode: int
    groupItems: List = []
    editorItems: List = []
    translatorItems: List = []
    authorItems: List[AuthorItem]
    patreonLink: Optional[str] = None
    coverUpdateTime: int
    giftNum: int
    videoAdIds: Optional[List] = None
    adIds: Optional[List] = None
    availableFpNum: Optional[int] = None
    publishTime: int
    updateTime: int
    isShowAds: Optional[int] = None
    categoryType: int
    categoryId: int
    categoryName: str
    description: str
    tagInfos: List[TagInfo]

    @model_validator(mode="after")
    def set_book_cover(cls, values):
        values.bookCover = f"https://book-pic.webnovel.com/bookcover/{values.bookId}"
        return values

    @field_validator("totalChapterNum", mode="before")
    def validate_total_chapter_num(cls, v, values):
        if v is None:
            return values.get("chapterNum")
        return v
