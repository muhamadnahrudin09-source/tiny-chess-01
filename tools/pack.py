import os
import ast
import lzma
import base64
import python_minifier
import subprocess
import time
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
        engine_code = f.read()
    with open('client.py', 'r', encoding='utf-8') as f:
        client_code = f.read()
    raw_engine_size = len(engine_code.encode('utf-8'))
    min_engine = python_minifier.minify(
        engine_code,
        rename_globals=True,
        preserve_globals=['Position', 'initial', 'parse', 'render', 'Move', 'Searcher', 'Stop', 'MATE_UPPER']
    )
    min_engine_size = len(min_engine.encode('utf-8'))
    filters = [{"id": lzma.FILTER_LZMA1, "preset": 9 | lzma.PRESET_EXTREME, "lc": 0, "lp": 0, "pb": 0}]
    c_engine = lzma.compress(min_engine.encode('utf-8'), format=lzma.FORMAT_ALONE, filters=filters)
    comp_engine_size = len(c_engine)
    b85_engine = base64.b85encode(c_engine).decode('ascii')
    enc_engine_size = len(b85_engine.encode('utf-8'))
    raw_client_size = len(client_code.encode('utf-8'))
    processed_client = process_client_code(client_code)
    min_client = python_minifier.minify(
        processed_client,
        rename_globals=False,
        rename_locals=False
    )
    min_client_size = len(min_client.encode('utf-8'))
    c_client = lzma.compress(min_client.encode('utf-8'), format=lzma.FORMAT_ALONE, filters=filters)
    comp_client_size = len(c_client)
    b85_client = base64.b85encode(c_client).decode('ascii')
    enc_client_size = len(b85_client.encode('utf-8'))
    print("--- ENGINE STAGES ---")
    print(f"Raw: {raw_engine_size} bytes")
    print(f"Minified: {min_engine_size} bytes")
    print(f"Compressed: {comp_engine_size} bytes")
    print(f"Encoded (base85): {enc_engine_size} bytes")
