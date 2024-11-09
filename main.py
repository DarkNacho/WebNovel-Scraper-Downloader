import argparse
import json
import os
import re
from ebooklib import epub
import requests
from WebNovelScraper import WebNovelScraper
from models import BookInfo, ChapterInfo


def create_epub(
    book_info: BookInfo, chapters_info: list[ChapterInfo], output_path: str = "."
):
    """
    Creates an EPUB file from the given book and chapters information.
    Args:
        book_info (BookInfo): An object containing metadata about the book, such as bookId, bookName, authorName, and bookCover.
        chapters_info (list[ChapterInfo]): A list of ChapterInfo objects, each containing metadata and content for a chapter.
        output_path (str): The directory where the EPUB file will be saved.
    Returns:
        None: The function writes the EPUB file to the specified directory.
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
    filepath = os.path.join(output_path, filename)
    epub.write_epub(filepath, book)


def main():
    parser = argparse.ArgumentParser(description="Get book information from WebNovel.")
    parser.add_argument("url", type=str, help="The URL of the WebNovel book")
    parser.add_argument(
        "-c", "--cookies", type=str, help="Path to the cookies JSON file"
    )
    parser.add_argument(
        "-o",
        "--output",
        type=str,
        default=".",
        help="Output directory for the EPUB file",
    )

    args = parser.parse_args()

    cookies = {}
    if args.cookies:
        with open(args.cookies, "r") as f:
            cookies = json.load(f)

    scraper = WebNovelScraper(args.url, cookies=cookies)
    book_info = scraper.get_book_info()
    # chapters_info = list(scraper.get_all_chapters())
    chapters_info = []
    print("Fetching chapters for: " + book_info.bookName)
    for chapter in scraper.get_all_chapters():
        chapters_info.append(chapter)
        print("fetched:", chapter.chapterName)

    create_epub(book_info, chapters_info, output_path=args.output)


if __name__ == "__main__":
    main()
