import lzma, base64 as b
with open('main_v5.py') as f:
    code = f.read()
# extract b85 string
import re
match = re.search(r"b85decode\('(.*)'\)", code)
if match:
    data = lzma.decompress(b.b85decode(match.group(1)))
    print("Decoded length:", len(data))
    print("Decoded preview:", data[:200])
