import argparse
import json
import os
import re
from ebooklib import epub
import requests

# from WebNovelScraper2 import WebNovelScraper
from scraper.BookScraper import BookScraper
from scraper.ComicScraper import ComicScraper

# from models2 import BookInfo, ChapterInfo


parser = argparse.ArgumentParser(description="Get book information from WebNovel.")
parser.add_argument("url", type=str, help="The URL of the WebNovel book or comic")
parser.add_argument("-c", "--cookies", type=str, help="Path to the cookies JSON file")
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
if "webnovel.com/book" in args.url:
    scraper = BookScraper(args.url, cookies=cookies)
elif "webnovel.com/comic" in args.url:
    scraper = ComicScraper(args.url, cookies=cookies)
else:
    raise ValueError("Invalid URL. Please provide a valid WebNovel book or comic URL.")

scraper.save(args.output)
