import re
m = re.search(r"b85decode\('(.*?)'\)", open('main.py').read())
print(f"'{m.group(1)}'", end='')
