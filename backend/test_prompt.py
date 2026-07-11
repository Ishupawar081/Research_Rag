from rag.prompts import *

context = """
Section 3.3

Variation Field

The variation field identifies dynamic voxels.
"""

print()

print(get_prompt(

    mode="single",

    query="Explain variation field",

    context=context

))