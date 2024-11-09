import argparse
import re
from ebooklib import epub
import requests
from WebNovelScraper import WebNovelScraper
from models import BookInfo, ChapterInfo


def create_epub(book_info: BookInfo, chapters_info: list[ChapterInfo]):
    """
    Creates an EPUB file from the given book and chapters information.
    Args:
        book_info (BookInfo): An object containing metadata about the book, such as bookId, bookName, authorName, and bookCover.
        chapters_info (list[ChapterInfo]): A list of ChapterInfo objects, each containing metadata and content for a chapter.
    Returns:
        None: The function writes the EPUB file to the current working directory.
    """
    book = epub.EpubBook()

    # Set metadata
    book.set_identifier(book_info.bookId)
    book.set_title(book_info.bookName)
    book.set_language("en")
    book.add_author(book_info.authorName)

    # Add cover image
    cover_image_content = requests.get(book_info.bookCover).content
    book.set_cover(f"cover_{book_info.bookId}.jpg", cover_image_content)

    # Add chapters
    chapter_items = []
    for chapter_info in chapters_info:
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
        uid="style_nav", file_name="style/nav.css", media_type="text/css", content=style
    )
    book.add_item(nav_css)

    # Basic spine
    book.spine = ["nav"] + chapter_items

    # Write to the file
    invalid_chars = r'[<>:"/\\|?*]'
    filename = re.sub(invalid_chars, "", book_info.bookName + ".epub").replace(" ", "_")
    epub.write_epub(filename, book)


def main():
    parser = argparse.ArgumentParser(description="Get book information from WebNovel.")
    parser.add_argument("url", type=str, help="The URL of the WebNovel book")
    args = parser.parse_args()

    scraper = WebNovelScraper(args.url)
    book_info = scraper.get_book_info()
    # chapters_info = list(scraper.get_all_chapters())
    chapters_info = []
    for chapter in scraper.get_all_chapters():
        chapters_info.append(chapter)
        print("fetched:", chapter.chapterName)
    create_epub(book_info, chapters_info)


if __name__ == "__main__":
    main()
