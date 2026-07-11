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

for i, (item, level) in enumerate(doc.iterate_items()):

    print("=" * 120)

    print(f"ITEM : {i}")

    print("TYPE :", type(item).__name__)

    print("LEVEL:", level)

    print("\nATTRIBUTES")

    pprint(vars(item))

    print()

    if i == 20:
        break