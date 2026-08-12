

# ten skrypt mial zamieniac linki do surwych bajtow obrazow, i robi to, ale to rozwiazanie ma wade
# kazdy punktor, logo etc, cos co sie powtarza jest ladowane niezaleznie, wiec potraja to wielkosc pliku
# wracamy do opcji ze kopiujemy obrazy do docelowego katalogu i ma tam byc pdf, html i tresc interatywna - obrazy etc



import base64
import mimetypes
import os
import re
import sys
from urllib.parse import unquote

html_file = sys.argv[1]

base_dir = os.path.dirname(os.path.abspath(html_file))

with open(html_file, "r", encoding="utf-8") as f:
    html = f.read()


def inline_file(path):
    path = unquote(path)

    # Already embedded
    if path.startswith("data:"):
        return path

    # External resource
    if path.startswith(("http://", "https://", "//")):
        return path

    # Ignore fragments
    path = path.split("#", 1)[0]

    full_path = os.path.normpath(
        os.path.join(base_dir, path)
    )

    if not os.path.isfile(full_path):
        print(f"SKIP: {path}")
        return path

    mime, _ = mimetypes.guess_type(full_path)

    if mime is None:
        mime = "application/octet-stream"

    with open(full_path, "rb") as f:
        encoded = base64.b64encode(f.read()).decode("ascii")

    print(f"INLINE: {path}")

    return f"data:{mime};base64,{encoded}"


# ------------------------------------------------------------
# 1. Inline src="..."
# ------------------------------------------------------------

html = re.sub(
    r'(\bsrc=["\'])([^"\']+)(["\'])',
    lambda m:
        m.group(1)
        + inline_file(m.group(2))
        + m.group(3),
    html,
    flags=re.IGNORECASE,
)


# ------------------------------------------------------------
# 2. Inline CSS url(...)
# ------------------------------------------------------------

def replace_css_url(match):
    quote = match.group(1)
    path = match.group(2)

    return f"url({quote}{inline_file(path)}{quote})"


html = re.sub(
    r'url\(\s*([\'"]?)([^\'")]+)\1\s*\)',
    replace_css_url,
    html,
    flags=re.IGNORECASE,
)


# ------------------------------------------------------------
# Write result
# ------------------------------------------------------------

with open(html_file, "w", encoding="utf-8") as f:
    f.write(html)

print("DONE")