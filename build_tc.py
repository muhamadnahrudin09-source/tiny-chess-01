import os
import lzma
import bz2
import zlib
import base64 as b

engine_file = 'engine.min.py' if os.path.exists('engine.min.py') else 'engine_trim.py'
client_file = 'client.min.py' if os.path.exists('client.min.py') else 'client.py'

with open(engine_file, 'r', encoding='utf-8') as f:
    engine_code = f.read()

with open(client_file, 'r', encoding='utf-8') as f:
    client_code = f.read()

combined = engine_code + '\n' + client_code

candidates = []

# 1. lzma FORMAT_ALONE
try:
    c = lzma.compress(combined.encode('utf-8'), format=lzma.FORMAT_ALONE, preset=9 | lzma.PRESET_EXTREME)
    payload = b.b85encode(c).decode('ascii')
    code = f"import lzma,base64 as b;exec(lzma.decompress(b.b85decode('{payload}')))"
    candidates.append(('lzma_alone', len(code), code))
except Exception as e:
    print('lzma_alone failed:', e)

# 2. lzma FORMAT_XZ
try:
    c = lzma.compress(combined.encode('utf-8'), format=lzma.FORMAT_XZ, preset=9 | lzma.PRESET_EXTREME)
    payload = b.b85encode(c).decode('ascii')
    code = f"import lzma,base64 as b;exec(lzma.decompress(b.b85decode('{payload}')))"
    candidates.append(('lzma_xz', len(code), code))
except Exception as e:
    print('lzma_xz failed:', e)

# 3. lzma FORMAT_RAW
try:
    filters = [{"id": lzma.FILTER_LZMA2, "preset": 9 | lzma.PRESET_EXTREME}]
    c = lzma.compress(combined.encode('utf-8'), format=lzma.FORMAT_RAW, filters=filters)
    payload = b.b85encode(c).decode('ascii')
    code = f"import lzma,base64 as b;exec(lzma.decompress(b.b85decode('{payload}'),format=lzma.FORMAT_RAW,filters=[{id:lzma.FILTER_LZMA2}]))"
    candidates.append(('lzma_raw', len(code), code))
except Exception as e:
    print('lzma_raw failed:', e)

# 4. bz2
try:
    c = bz2.compress(combined.encode('utf-8'), 9)
    payload = b.b85encode(c).decode('ascii')
    code = f"import bz2,base64 as b;exec(bz2.decompress(b.b85decode('{payload}')))"
    candidates.append(('bz2', len(code), code))
except Exception as e:
    print('bz2 failed:', e)

# 5. zlib
try:
    c = zlib.compress(combined.encode('utf-8'), 9)
    payload = b.b85encode(c).decode('ascii')
    code = f"import zlib,base64 as b;exec(zlib.decompress(b.b85decode('{payload}')))"
    candidates.append(('zlib', len(code), code))
except Exception as e:
    print('zlib failed:', e)

print("Candidates found:")
for name, size, code in candidates:
    print(f"  {name}: {size} bytes")

valid = [c for c in candidates if c[1] <= 4096]
if valid:
    valid.sort(key=lambda x: x[1])
    best_name, best_size, best_code = valid[0]
    print(f"Selecting best valid candidate: {best_name} with {best_size} bytes")
    with open('main.py', 'w', encoding='utf-8') as f:
        f.write(best_code)
else:
    print("WARNING: No candidate <= 4096 bytes found!")
    # Fallback to smallest anyway
    candidates.sort(key=lambda x: x[1])
    best_name, best_size, best_code = candidates[0]
    print(f"Fallback to smallest: {best_name} with {best_size} bytes")
    with open('main.py', 'w', encoding='utf-8') as f:
        f.write(best_code)

print(len(best_code))
