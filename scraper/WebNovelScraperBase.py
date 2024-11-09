from abc import ABC, abstractmethod
import re
from typing import Dict, Iterator
from models.base import BaseInfo, BaseChapter
import requests
from bs4 import BeautifulSoup
import demjson3


class WebNovelScraperBase(ABC):
    url: str
    headers: Dict[str, str]
    cookies: Dict[str, str]
    info: BaseInfo

    def __init__(self, url: str, cookies: dict = None):
        self.url = url
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
        }
        self.cookies = cookies or {}
        self.info = self._fetch_info()
        print(f"Fetching info for: {self.info.name}")

    def _clean_json(self, json_data: str) -> str:
        # Remove invalid escape sequences
        json_data = re.sub(r'\\(?!["\\/bfnrtu])', "", json_data)
        return json_data

    def _fetch_info(self) -> BaseInfo:
        response = requests.get(self.url, headers=self.headers, cookies=self.cookies)
        soup = BeautifulSoup(response.content, "html.parser")

        script_tag = soup.find("script", string=re.compile(self.get_info_regex()))
        if script_tag:
            script_content = script_tag.string

            match = re.search(self.get_info_regex(), script_content, re.DOTALL)

            if match:
                json_data = match.group(1)
                json_data = self._clean_json(json_data)
                info_dict = demjson3.decode(json_data)
                return self.parse_info(info_dict)

            else:
                raise ValueError("Info not found.")
        else:
            raise ValueError("No <script> tag containing info was found.")

    def _fetch_chapter_info(self, chapterId) -> BaseChapter:
        response = requests.get(
            f"{self.url}/{chapterId}", headers=self.headers, cookies=self.cookies
        )
        soup = BeautifulSoup(response.content, "html.parser")

        script_tag = soup.find(
            "script", string=re.compile(self.get_chapter_info_regex())
        )
        if script_tag:
            script_content = script_tag.string

            match = re.search(self.get_chapter_info_regex(), script_content, re.DOTALL)

            if match:
                json_data = match.group(1)
                json_data = self._clean_json(json_data)
                chap_info_dict = demjson3.decode(json_data)
                return self.parse_chapter_info(chap_info_dict)

            else:
                raise ValueError("Chapter info not found.")
        else:
            raise ValueError("No <script> tag containing chapter info was found.")

    def get_info(self) -> BaseInfo:
        return self.info

    def get_all_chapters(self) -> Iterator[BaseChapter]:
        chapterId = self.info.firstChapterId
        while chapterId and chapterId != "-1":
            chapter_info = self._fetch_chapter_info(chapterId)

            if chapter_info.isAuth == 0:
                break  # If the chapter is not available, break the loop
            yield chapter_info
            chapterId = chapter_info.nextChapterId

    @abstractmethod
    def get_info_regex(self) -> str:
        pass

    @abstractmethod
    def parse_info(self, info_dict: dict) -> BaseInfo:
        pass

    @abstractmethod
    def get_chapter_info_regex(self) -> str:
        pass

    @abstractmethod
    def parse_chapter_info(self, chap_info_dict: dict) -> BaseChapter:
        pass

    @abstractmethod
    def save(self, output_path: str = "."):
        pass
