#!/usr/bin/env python
"""Extract text from a .doc file by parsing the OLE2 compound document."""

import struct
import re

DOC_PATH = r"C:\Users\Nanfeng\Downloads\4.系统构架设计说明书.doc"

with open(DOC_PATH, "rb") as f:
    data = f.read()

# Try to extract Unicode text (UTF-16LE) chunks
text_parts = []
i = 0
while i < len(data) - 1:
    # Read as UTF-16LE if it looks like Chinese text
    try:
        chunk = data[i:i+2]
        val = struct.unpack('<H', chunk)[0]
        # Chinese range + ASCII + common punctuation
        if (0x4e00 <= val <= 0x9fff or 
            0x3000 <= val <= 0x303f or
            0x0020 <= val <= 0x007e or
            val in (0x0d, 0x0a, 0x00a0, 0x2000, 0x2003, 0x3001, 0x3002)):
            text_parts.append(chr(val))
        else:
            if text_parts and text_parts[-1] != '\n':
                text_parts.append('\n')
    except:
        pass
    i += 2

text = ''.join(text_parts)

# Clean up - remove excessive newlines
text = re.sub(r'\n{3,}', '\n\n', text)

# Write extracted text
with open("extracted_doc_content.txt", "w", encoding="utf-8") as f:
    f.write(text)

print("Extraction complete. See extracted_doc_content.txt")
print(f"Total characters: {len(text)}")
