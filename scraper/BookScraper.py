import os
from typing import Dict, Iterator
import demjson3
from models.book import Info, Chapter
from scraper.WebNovelScraperBase import WebNovelScraperBase
import re
import requests
from bs4 import BeautifulSoup
from ebooklib import epub


class BookScraper(WebNovelScraperBase):

    url: str
    headers: Dict[str, str]
    cookies: Dict[str, str]
    info: Info

    def _fetch_info(self) -> Info:
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
                return Info(**book_dict["bookInfo"])

            else:
                raise ValueError("g_data.book not found.")
        else:
            raise ValueError("No <script> tag containing g_data.book was found.")

    def _fetch_chapter_info(self, chapterId) -> Chapter:
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
                return Chapter(**chap_info_dict["chapterInfo"])

            else:
                raise ValueError("chapInfo not found.")
        else:
            raise ValueError("No <script> tag containing chapInfo was found.")

    def get_info(self) -> Info:
        return self.info

    def get_all_chapters(self) -> Iterator[Chapter]:
        chapterId = self.info.firstChapterId
        while chapterId and chapterId != "-1":
            chapter_info = self._fetch_chapter_info(chapterId)

            if chapter_info.isAuth == 0:
                break  # If the chapter is not available, break the loop
            yield chapter_info
            chapterId = chapter_info.nextChapterId

    def save(self, output_path: str = "."):
        book = epub.EpubBook()

        # Set metadata
        book.set_identifier(self.info.bookId)
        book.set_title(self.info.bookName)
        book.set_language("en")
        book.add_author(self.info.authorName)

        # Add cover image
        cover_image_content = requests.get(self.info.cover).content
        book.set_cover(f"cover_{self.info.bookId}.jpg", cover_image_content)

        # Add chapters
        chapter_items = []
        for chapter_info in self.get_all_chapters():
            print(f"Fetching chapter: {chapter_info.chapterName}")
            chapter = epub.EpubHtml(
                title=chapter_info.chapterName,
                file_name=f"chap_{chapter_info.chapterIndex}.xhtml",
                lang="en",
            )
            chapter.content = (
                f"<h1>{chapter_info.chapterName}</h1>{chapter_info.get_full_content()}"
            )
            book.add_item(chapter)
            chapter_items.append(chapter)
        # Define Table Of Contents
        book.toc = tuple(chapter_items)

        # Add default NCX and Nav file
        book.add_item(epub.EpubNcx())
        book.add_item(epub.EpubNav())

        # Define CSS style
        style = "BODY { font-family: Arial, Helvetica, sans-serif; }"
        nav_css = epub.EpubItem(
            uid="style_nav",
            file_name="style/nav.css",
            media_type="text/css",
            content=style,
        )
        book.add_item(nav_css)

        # Basic spine
        book.spine = ["nav"] + chapter_items

        # Write to the file
        invalid_chars = r'[<>:"/\\|?*]'
        filename = re.sub(invalid_chars, "", self.info.bookName + ".epub").replace(
            " ", "_"
        )
        filepath = os.path.join(output_path, filename)
        epub.write_epub(filepath, book)
