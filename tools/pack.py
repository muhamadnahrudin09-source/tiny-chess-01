import lzma, base64

def pack():
    with open('engine_trim.py', encoding='utf-8') as f:
        e = f.read()
    with open('client.py', encoding='utf-8') as f:
        c = f.read()
    filters = [{"id": lzma.FILTER_LZMA1, "preset": 9 | lzma.PRESET_EXTREME, "lc": 0, "lp": 0, "pb": 0}]
    comp = lzma.compress((e + '\n' + c).encode('utf-8'), format=lzma.FORMAT_ALONE, filters=filters)
    payload = base64.b85encode(comp).decode('ascii')
    stub = f"import lzma,base64 as b;exec(lzma.decompress(b.b85decode('{payload}')))"
    size = len(stub.encode('utf-8'))
    assert size <= 4096, f"Stub size {size} exceeds 4096 bytes!"
    print(stub)

if __name__ == '__main__':
    pack()
