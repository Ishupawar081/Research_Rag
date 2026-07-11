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

interesting = {
    "PictureItem",
    "TableItem",
    "FormulaItem",
    "SectionHeaderItem"
}

for item, level in doc.iterate_items():

    if type(item).__name__ in interesting:

        print("\n")
        print("=" * 120)

        print(type(item).__name__)

        pprint(vars(item))

        print()