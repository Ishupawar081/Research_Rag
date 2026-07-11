from collections import Counter
from pathlib import Path

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

counter = Counter()

for item, level in doc.iterate_items():
    counter[type(item).__name__] += 1

print("\n========== OBJECT TYPES ==========\n")

for k, v in sorted(counter.items()):
    print(f"{k:30} : {v}")