import lzma, base64, python_minifier, ast

def process_client_code(code):
    tree = ast.parse(code)
    class ClientTransformer(ast.NodeTransformer):
        def visit_Import(self, node):
            new_names = [alias for alias in node.names if not alias.name.startswith('engine')]
            if not new_names:
                return None
            node.names = new_names
            return node
        def visit_ImportFrom(self, node):
            if node.module and node.module.startswith('engine'):
                return None
            return node
        def visit_Attribute(self, node):
            self.generic_visit(node)
            if isinstance(node.value, ast.Name) and node.value.id == 'sunfish':
                return ast.Name(id=node.attr, ctx=node.ctx)
            return node
    tree = ClientTransformer().visit(tree)
    return ast.unparse(tree)

def pack():
    with open('engine_trim.py', 'r', encoding='utf-8') as f:
        e = f.read()
    with open('client.py', 'r', encoding='utf-8') as f:
        c = f.read()
    min_engine = python_minifier.minify(
        e,
        rename_globals=True,
        preserve_globals=['Position', 'initial', 'parse', 'render', 'Move', 'Searcher', 'Stop', 'MATE_UPPER']
    )
    processed_client = process_client_code(c)
    min_client = python_minifier.minify(
        processed_client,
        rename_globals=False,
        rename_locals=False
    )
    combined = min_engine + '\n' + min_client
    filters = [{"id": lzma.FILTER_LZMA1, "preset": 9 | lzma.PRESET_EXTREME, "lc": 0, "lp": 0, "pb": 0}]
    comp = lzma.compress(combined.encode('utf-8'), format=lzma.FORMAT_ALONE, filters=filters)
    payload = base64.b85encode(comp).decode('ascii')
    stub = f"import lzma,base64 as b;exec(lzma.decompress(b.b85decode('{payload}')))"
    print("Stub size:", len(stub.encode('utf-8')))
    return stub

if __name__ == '__main__':
    pack()
