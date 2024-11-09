# WebNovel Scraper

This project scrapes unlocked chapters from [WebNovel](www.webnovel.com) and compiles them into an EPUB book. 

## Features

- **Scrapes Unlocked Chapters Only**: The scraper gathers only Unlocked content by default.
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
python main.py <URL> [-c COOKIES] [-o OUTPUT]
```

### Arguments

- `url`: The URL of the WebNovel book.
- `-c, --cookies`: Path to the cookies JSON file (optional).
- `-o, --output`: Output directory for the EPUB file (optional, default is the current directory).

### Example

```sh
python main.py https://www.webnovel.com/book/example-book -o /path/to/output/directory
```

## How to Get Cookies for Credentials

To get locked chapters, you need to provide your WebNovel session cookies. Using your credentials allows the scraper to access chapters you have unlocked or paid for. Here is how you can get them:

1. **Log in to WebNovel**: Open your web browser and log in to your WebNovel account.
2. **Open Developer Tools**: Press `F12` or right-click on the page and select `Inspect` to open the Developer Tools.
3. **Go to the Network Tab**: Click on the `Network` tab in the Developer Tools.
4. **Reload the Page**: Reload the WebNovel page to capture the network requests.
5. **Find the Request**: Look for a request to `webnovel.com` in the list of network requests.
6. **Copy Cookies**: Click on the request and go to the `Headers` tab. Scroll down to the `Request Headers` section and find the `Cookie` header. Copy the entire value of the `Cookie` header.
7. **Create a JSON File**: Create a file named `cookies.json` and paste the copied cookies into it in JSON format. It should look something like this:

```json
{
  "e2": "",
  "e1": "",
  "webnovel_uuid": "",
  "_csrfToken": "",
  "webnovel-content-language": "",
  "webnovel-language": "",
  "bookCitysex": "",
  "checkInTip": "",
  "show_lib_tip": "",
  "uid": "",
  "ukey": "",
  "dontneedgoogleonetap": "",
  "QDReport_utm": "",
}
```

8. **Use the Cookies File**: Pass the path to the `cookies.json` file using the `-c` or `--cookies` argument when running the scraper.

This will allow the scraper to use your session cookies and access any unlocked or paid chapters.

## NOTES: 
1. The scraper stops automatically when it encounters the first locked chapter. As a result, any unlocked chapters appearing after a locked chapter will not be included in the EPUB.

1. It does not add Auxiliary Chapters.