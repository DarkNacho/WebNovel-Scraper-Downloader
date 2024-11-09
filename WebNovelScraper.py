import requests
from bs4 import BeautifulSoup
import re
import json
from models import BookInfo, ChapterInfo
from typing import Iterator


class WebNovelScraper:
    """
    A class to scrape web novel information and chapters from a given URL.
    Attributes:
        url (str): The URL of the web novel.
        headers (dict): The headers to use for HTTP requests.
        book (BookInfo): The information about the book.
    Methods:
        _fetch_book_info() -> BookInfo:
            Fetches and parses the book information from the web novel page.
        _fetch_chapter_info(chapterId) -> ChapterInfo:
            Fetches and parses the chapter information for a given chapter ID.
        get_book_info() -> BookInfo:
            Returns the book information.
        get_all_chapters() -> Iterator[ChapterInfo]:
            Yields all available chapters of the web novel.
    """

    def __init__(self, url: str):
        self.url = url
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
        }
        self.book = self._fetch_book_info()

    def _fetch_book_info(self) -> BookInfo:
        response = requests.get(self.url, headers=self.headers)
        soup = BeautifulSoup(response.content, "html.parser")

        script_tag = soup.find("script", string=re.compile(r"g_data\.book\s*=\s*\{"))
        if script_tag:
            script_content = script_tag.string

            match = re.search(
                r"g_data\.book\s*=\s*(\{.*?\})\s*,\s*g_data\.",
                script_content,
                re.DOTALL,
            )

            if match:
                json_data = match.group(1)

                # Clean the JSON data
                json_data = json_data.replace("\\\\", "\\")
                json_data = re.sub(r'\\(?!["\\/bfnrtu])', r"\\\\", json_data)

                book_dict = json.loads(json_data)
                return BookInfo(**book_dict["bookInfo"])

            else:
                raise ValueError("g_data.book not found.")
        else:
            raise ValueError("No <script> tag containing g_data.book was found.")

    def _fetch_chapter_info(self, chapterId) -> ChapterInfo:
        response = requests.get(f"{self.url}/{chapterId}", headers=self.headers)
        soup = BeautifulSoup(response.content, "html.parser")

        script_tag = soup.find("script", string=re.compile(r"var chapInfo\s*=\s*"))
        if script_tag:
            script_content = script_tag.string

            match = re.search(
                r"var chapInfo\s*=\s*(\{.*?\});", script_content, re.DOTALL
            )

            if match:
                json_data = match.group(1)

                # Clean the JSON data
                json_data = json_data.replace("\\\\", "\\")
                json_data = re.sub(r'\\(?!["\\/bfnrtu])', r"\\\\", json_data)

                chap_info_dict = json.loads(json_data)

                # book_info = BookInfo(**chap_info_dict["bookInfo"])
                return ChapterInfo(**chap_info_dict["chapterInfo"])

            else:
                raise ValueError("chapInfo not found.")
        else:
            raise ValueError("No <script> tag containing chapInfo was found.")

    def get_book_info(self) -> BookInfo:
        return self.book

    def get_all_chapters(self) -> Iterator[ChapterInfo]:
        chapterId = self.book.firstChapterId
        while chapterId and chapterId != "-1":
            chapter_info = self._fetch_chapter_info(chapterId)

            if chapter_info.isAuth == 0:
                break  # If the chapter is not available, break the loop
            yield chapter_info
            chapterId = chapter_info.nextChapterId
