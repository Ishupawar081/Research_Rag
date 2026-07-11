from pathlib import Path
from pprint import pprint

from docling.document_converter import (
    DocumentConverter,
    PdfFormatOption,
    InputFormat,
)
from docling.datamodel.pipeline_options import PdfPipelineOptions

pipeline_options = PdfPipelineOptions()
pipeline_options.do_ocr = False

converter = DocumentConverter(
    format_options={
        InputFormat.PDF: PdfFormatOption(
            pipeline_options=pipeline_options
        )
    }
)

pdf = Path("pdfs/2212.00186v3.pdf")

result = converter.convert(pdf)
doc = result.document

for item, level in doc.iterate_items():

    if type(item).__name__ == "PictureItem":

        print("=" * 120)

        pprint(vars(item))

        print()

        print("DIR")

        pprint(dir(item))

        print()

        print("=" * 120)