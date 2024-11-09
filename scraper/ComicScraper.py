import os
from typing import Dict, Iterator
from models.comic import Info, Chapter
from scraper.WebNovelScraperBase import WebNovelScraperBase
import re
import requests
from fpdf import FPDF
from PyPDF2 import PdfMerger


class ComicScraper(WebNovelScraperBase):
    url: str
    headers: Dict[str, str]
    cookies: Dict[str, str]
    info: Info

    def get_info_regex(self) -> str:
        return r"g_data\.book\s*=\s*(\{.*\})"

    def parse_info(self, info_dict: dict) -> Info:
        return Info(**info_dict["comicInfo"])

    def get_chapter_info_regex(self) -> str:
        return r"var chapInfo\s*=\s*(\{.*?\});"

    def parse_chapter_info(self, chap_info_dict: dict) -> Chapter:
        return Chapter(**chap_info_dict["chapterInfo"])

    def save(self, output_path: str = "."):
        # Crear el archivo PDF principal
        invalid_chars = r'[<>:"/\\|?*]'
        filename = re.sub(invalid_chars, "", self.info.comicName + ".pdf").replace(
            " ", "_"
        )
        final_pdf_path = os.path.join(output_path, filename)

        # Crear un archivo PDF para la portada
        cover_image_content = requests.get(self.info.cover).content
        cover_image_path = f"cover_{self.info.comicId}.jpg"
        with open(cover_image_path, "wb") as cover_img_file:
            cover_img_file.write(cover_image_content)
        pdf = FPDF()
        pdf.add_page()
        pdf.image(cover_image_path, x=0, y=0, w=pdf.w, h=pdf.h)
        pdf.output(final_pdf_path, "F")
        os.remove(cover_image_path)

        for chapter_info in self.get_all_chapters():
            print(f"Fetching chapter: {chapter_info.chapterName}")

            chapter_pdf_path = os.path.join(
                output_path, f"chapter_{chapter_info.chapterIndex}.pdf"
            )
            chapter_pdf = FPDF()

            for page in chapter_info.chapterPage:
                image_content = requests.get(page.url).content
                image_path = f"{page.pageId}.jpg"

                # Guardar la imagen temporalmente
                with open(image_path, "wb") as img_file:
                    img_file.write(image_content)

                # Agregar una nueva página al PDF del capítulo
                chapter_pdf.add_page()
                chapter_pdf.image(
                    image_path, x=0, y=0, w=chapter_pdf.w, h=chapter_pdf.h
                )

                # Eliminar la imagen temporal
                os.remove(image_path)

            # Guardar el PDF del capítulo
            chapter_pdf.output(chapter_pdf_path, "F")

            # Fusionar el capítulo con el PDF principal
            merger = PdfMerger()
            merger.append(final_pdf_path)
            merger.append(chapter_pdf_path)
            merger.write(final_pdf_path)
            merger.close()

            # Eliminar el archivo PDF temporal del capítulo
            os.remove(chapter_pdf_path)

        print(f"PDF saved at {final_pdf_path}")
