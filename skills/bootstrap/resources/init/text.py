import re

def pascal(name: str) -> str:
    words = re.findall(r'[a-zA-Z0-9]+', name)
    return "".join(word.capitalize() for word in words)

def lower(name: str) -> str:
    words = re.findall(r'[a-zA-Z0-9]+', name)
    return "".join(word.lower() for word in words)

def path(package: str) -> str:
    return package.replace('.', '/')
