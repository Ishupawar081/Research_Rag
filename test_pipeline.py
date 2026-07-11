import asyncio
from pathlib import Path
from backend.pipeline.pipeline_manager import run_pipeline

async def main():
    # create a dummy pdf
    dummy_pdf = Path("temp_uploads/dummy.pdf")
    dummy_pdf.parent.mkdir(exist_ok=True)
    dummy_pdf.touch()

    user_id = "test-user-id"
    async for msg in run_pipeline(str(dummy_pdf), user_id):
        print(msg)

asyncio.run(main())
