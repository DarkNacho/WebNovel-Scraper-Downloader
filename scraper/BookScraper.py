import os
from typing import Dict, Iterator
from models.book import Info, Chapter
from scraper.WebNovelScraperBase import WebNovelScraperBase
import re
import requests
from ebooklib import epub


class BookScraper(WebNovelScraperBase):
    url: str
    headers: Dict[str, str]
    cookies: Dict[str, str]
    info: Info

    def get_info_regex(self) -> str:
        return r"g_data\.book\s*=\s*(\{.*?\})\s*,\s*g_data\."

    def parse_info(self, info_dict: dict) -> Info:
        return Info(**info_dict["bookInfo"])

    def get_chapter_info_regex(self) -> str:
        return r"var chapInfo\s*=\s*(\{.*?\});"

    def parse_chapter_info(self, chap_info_dict: dict) -> Chapter:
        return Chapter(**chap_info_dict["chapterInfo"])

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

        # Define CSS style
        style = "BODY { font-family: Arial, Helvetica, sans-serif; }"
        nav_css = epub.EpubItem(
            uid="style_nav",
            file_name="style/nav.css",
            media_type="text/css",
            content=style,
        )
        book.add_item(nav_css)

        # Add default NCX and Nav file
        book.add_item(epub.EpubNcx())
        book.add_item(epub.EpubNav())

        # Initialize chapter items list
        chapter_items = []

        # Write to the file
        invalid_chars = r'[<>:"/\\|?*]'
        filename = re.sub(invalid_chars, "", self.info.bookName + ".epub").replace(
            " ", "_"
        )
        filepath = os.path.join(output_path, filename)

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

            # Update spine and TOC
            book.spine = ["nav"] + chapter_items
            book.toc = tuple(chapter_items)

            # Save the EPUB file incrementally
            epub.write_epub(filepath, book)

        print(f"EPUB saved at {filepath}")
