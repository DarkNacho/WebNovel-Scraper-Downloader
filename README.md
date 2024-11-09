# WebNovel Scraper

This project scrapes free chapters from [WebNovel](www.webnovel.com) and compiles them into an EPUB book. The scraper stops automatically when it encounters the first locked chapter. As a result, any unlocked chapters appearing after a locked chapter will not be included in the EPUB.

## Features

- **Scrapes Free Chapters Only**: The scraper gathers only free content by default.
- **EPUB File Creation**: Compiles downloaded chapters into a single EPUB file for offline reading.

## Prerequisites

- **Python**: Ensure you have Python installed (version 3+ recommended).
- **Dependencies**: Required packages are listed in `requirements.txt`.

## Installation

Install the required packages by running:

```sh
pip install -r requirements.txt
```

## Usage

Run the scraper with the following command, replacing the URL with the novel's link:

```sh
python main.py https://www.webnovel.com/book/example-book
```

The script will save an EPUB file in the current directory with the chapters scraped from the specified book.

## Future Enhancements

- **User Credential Support**: Enable the input of user credentials to access and download unlocked chapters.
- **Complete Chapter Scan**: Add an option to scan and include any unlocked chapters in the book, regardless of their position.
- **Auxiliary Content**: Support downloading additional content like author notes, side stories, and bonus chapters.
