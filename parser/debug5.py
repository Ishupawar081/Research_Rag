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

for i, (item, level) in enumerate(doc.iterate_items()):

    if type(item).__name__ == "PictureItem":

        print("Picture", i)

        image = item.get_image(doc)

        print(type(image))

        if image is not None:

            image.save(f"figure_{i}.png")

            print("saved")

        else:

            print("None")