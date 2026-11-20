#!/usr/bin/env python3
"""Pack sunfish fork + client into main.py <= 4096 bytes (lzma + base85 exec stub)."""
import base64, lzma, sys
from python_minifier import minify

engine = minify(open('/root/makefun/tiny-chess-01-fork/engine.py').read(),
                remove_literal_statements=True, rename_globals=True)
client_src = open('/root/makefun/tiny-chess-01-fork/client.py').read()
client_src = client_src.replace('import engine as sunfish\n', '')
client_src = client_src.replace('sunfish.', '')
client = minify(client_src, remove_literal_statements=True, rename_globals=False)

full = engine + '\n' + client
blob = base64.b85encode(lzma.compress(full.encode('utf-8'), preset=9 | lzma.PRESET_EXTREME)).decode()
stub = "import lzma,base64;exec(lzma.decompress(base64.b85decode('%s')))" % blob
out = "# GPL-3.0-only fork of sunfish (github.com/thomasahle/sunfish)\n" + stub
open('/root/makefun/tiny-chess-01-fork/main.py', 'w').write(out)
print('main.py bytes:', len(out))
