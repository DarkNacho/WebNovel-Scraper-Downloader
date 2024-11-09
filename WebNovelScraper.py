import requests
from bs4 import BeautifulSoup
import re
import demjson3
from models import BookInfo, ChapterInfo
from typing import Iterator


class WebNovelScraper:
    """
    A class to scrape from www.webnovel.com given a book URL.
    Attributes:
        url (str): The URL of the book.
        headers (dict): The headers to use for the HTTP requests.
        cookies (dict): The cookies to use for the HTTP requests.
        book (BookInfo): The information about the book.
    Methods:
        _clean_json(json_data: str) -> str:
            Cleans the JSON data by removing invalid escape sequences.
        _fetch_book_info() -> BookInfo:
            Fetches the book information from the URL.
        _fetch_chapter_info(chapterId) -> ChapterInfo:
            Fetches the chapter information for a given chapter ID.
        get_book_info() -> BookInfo:
            Returns the book information.
        get_all_chapters() -> Iterator[ChapterInfo]:
            Returns an iterator over all chapters of the book.
    """

    def __init__(self, url: str, cookies: dict = None):
        self.url = url
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
        }
        self.cookies = cookies or {}
        self.book = self._fetch_book_info()

    def _clean_json(self, json_data: str) -> str:
        # Remove invalid escape sequences
        json_data = re.sub(r'\\(?!["\\/bfnrtu])', "", json_data)

        # Replace invalid escape sequences
        # json_data = json_data.replace("\\\\", "\\")
        # json_data = re.sub(r'\\(?!["\\/bfnrtu])', r"\\\\", json_data)
        return json_data

    def _fetch_book_info(self) -> BookInfo:
        response = requests.get(self.url, headers=self.headers, cookies=self.cookies)
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
                json_data = self._clean_json(json_data)
                book_dict = demjson3.decode(json_data)
                return BookInfo(**book_dict["bookInfo"])

            else:
                raise ValueError("g_data.book not found.")
        else:
            raise ValueError("No <script> tag containing g_data.book was found.")

    def _fetch_chapter_info(self, chapterId) -> ChapterInfo:
        response = requests.get(
            f"{self.url}/{chapterId}", headers=self.headers, cookies=self.cookies
        )
        soup = BeautifulSoup(response.content, "html.parser")

        script_tag = soup.find("script", string=re.compile(r"var chapInfo\s*=\s*"))
        if script_tag:
            script_content = script_tag.string

            match = re.search(
                r"var chapInfo\s*=\s*(\{.*?\});", script_content, re.DOTALL
            )

            if match:
                json_data = match.group(1)
                json_data = self._clean_json(json_data)
                chap_info_dict = demjson3.decode(json_data)
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
