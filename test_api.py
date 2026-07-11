import asyncio
from pathlib import Path
from backend.pipeline.pipeline_manager import run_pipeline

async def main():
    dummy = Path("temp_uploads/dummy.pdf")
    dummy.parent.mkdir(exist_ok=True)
    with open(dummy, "w") as f:
        f.write("dummy")

    try:
        async for line in run_pipeline(str(dummy), "test-user"):
            print(line.strip())
    except Exception as e:
        print("EXCEPTION IN RUN:", e)

if __name__ == "__main__":
    asyncio.run(main())
