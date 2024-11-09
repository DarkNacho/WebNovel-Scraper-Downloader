from abc import ABC, abstractmethod
import re
from typing import Dict, Iterator
from models.base import BaseInfo, BaseChapter

# from base_modals import BaseInfo, BaseChapter


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
        print(self.info.name)

    def _clean_json(self, json_data: str) -> str:
        # Remove invalid escape sequences
        json_data = re.sub(r'\\(?!["\\/bfnrtu])', "", json_data)
        return json_data

    @abstractmethod
    def _fetch_info(self) -> BaseInfo:
        pass

    @abstractmethod
    def _fetch_chapter_info(self, chapterId) -> BaseChapter:
        pass

    @abstractmethod
    def get_info(self):
        pass

    @abstractmethod
    def get_all_chapters(self) -> Iterator[BaseChapter]:
        pass

    @abstractmethod
    def save(self, output_path: str = "."):
        pass
