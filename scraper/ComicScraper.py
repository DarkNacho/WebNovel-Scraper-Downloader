import os
from typing import Dict, Iterator
import demjson3
from models.comic import Info, Chapter
from scraper.WebNovelScraperBase import WebNovelScraperBase
import re
import requests
from bs4 import BeautifulSoup
from fpdf import FPDF


class ComicScraper(WebNovelScraperBase):

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
                r"g_data\.book\s*=\s*(\{.*\})",
                script_content,
                re.DOTALL,
            )

            if match:
                json_data = match.group(1)
                json_data = self._clean_json(json_data)
                book_dict = demjson3.decode(json_data)
                return Info(**book_dict["comicInfo"])

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
        pdf = FPDF()

        for chapter_info in self.get_all_chapters():
            print(f"Fetching chapter: {chapter_info.chapterName}")

            for page in chapter_info.chapterPage:
                image_content = requests.get(page.url).content
                image_path = f"{page.pageId}.jpg"

                # Guardar la imagen temporalmente
                with open(image_path, "wb") as img_file:
                    img_file.write(image_content)

                # Agregar una nueva página al PDF
                pdf.add_page()
                pdf.image(image_path, x=10, y=10, w=pdf.w - 20)

                # Eliminar la imagen temporal
                os.remove(image_path)
            break
        # Guardar el PDF
        invalid_chars = r'[<>:"/\\|?*]'
        filename = re.sub(invalid_chars, "", self.info.comicName + ".pdf").replace(
            " ", "_"
        )
        filepath = os.path.join(output_path, filename)
        pdf.output(filepath)
