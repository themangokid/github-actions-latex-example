# README

## Detailed instructions below

* Assumptions: One verse per row for each text file

1. Download all the text from you version
2. Strip verse numbers and comments
3. Export all of the .txt and put them into a folder
4. Upload all texts onto overleaf, the max amout of files is somewhere around 180 files. Separate bible books into folders, then upload.
5. Generate .tex (as in LaTeX) files for each .txt file and add them to the "render" folder. Include all render files in to the main folder
6. Separate the versions into if-statments
7. Connect to Github Actions
8. ???



Any title of the files included in the project is going to matter since the title is what sets the name of the chapter. Eg: "Psalm 1" is automatically generated using the file name, making it important to have the corret file name for 


This document explains how to create and process files from Bible verses using content from [Bibelonline](https://bibelonline.se/biblereader.php) and how to remove unwanted characters using Sublime Text, along with automating LaTeX command insertion and batch processing with Perl.

---
## Manually adding text files from srbs website

## 0. Generating the textr files
Open up visual studio code and then runt the following command in the terminal: 
```touch första_mosebok_kapitel_{1..50}.txt``` Assuming you change the neccesary things.

## 1. Downloading and Creating Files

- **Step 1:** Go to [Bibelonline](https://bibelonline.se/biblereader.php).
- **Step 2:** Copy a verse from the site.
- **Step 3:** Create a new file (using your preferred editor) and paste the verse. The name you choose for this file will later become the title.

---

## 2. Removing Extra Characters with Sublime Text

1. **Install Sublime Text.**
2. **Open your file** in Sublime Text.
3. Press **Ctrl + F** to open the Find panel.
4. Click the **".*"** icon to enable regular expression search.
5. **Note:**  
   - If you need to remove an extra character (for example, a left square bracket `[`) add `|\[` to the end of the regular expression.
6. In the Find field, paste the following regular expression:
   ```
   \b\d+\s|\*
   ```
7. Press **Option + Enter** (on Windows, press **Alt + Enter**) to select all matches.
8. Press **Backspace** to delete the selected text.
9. **Done.**

---

## 3. Automating LaTeX Command Generation

If you want to generate LaTeX commands for multiple psalm files, use the following Python snippet. It prints LaTeX commands that call your custom command `\ProcessAndRenderFile` for each psalm file:

```python
for i in range(x, y):
    print(
        """\\ProcessAndRenderFile{{bible//psaltaren/psalm{0}.txt}}{{\\huge Psalm {1}}}""".format(i, i)
    )
```

- Replace `x` and `y` with the starting and ending numbers for your psalm files.

---

## 4. Batch Processing with Perl

To remove unwanted characters from multiple psalm text files at once, you can use the following shell command (requires Perl):

```bash
for X in {1..150}; do
  perl -pi -e 's/\d+\s|\*//g' psalm${X}.txt
done
```

- This command processes files named `psalm1.txt` through `psalm150.txt` by removing:
  - Any numbers followed by whitespace (`\d+\s`)
  - Any asterisks (`\*`)

---

By following these detailed steps, you can efficiently download, clean, and prepare your Bible verses for further processing or inclusion in your LaTeX documents.


## 5. Add relative path to seriebibelns images 

#!/bin/bash
# Assume the current working directory is "img"
# Define the prefix to add (the full relative path from the project root)
prefix="seriebibeln/img"

# Output file for the LaTeX commands
outfile="images.tex"

# Clear the output file (or create it if it doesn't exist)
> "$outfile"

# Recursively find all .jpg files (case-insensitive)
find . -type f -iname "*.jpg" | while read -r file; do
  # Remove the leading "./" if present
  rel="${file#./}"
  # Write the LaTeX command into the output file
  echo "\\includegraphics[width=\\textwidth]{$prefix/$rel}" >> "$outfile"
done

echo "LaTeX code generated in $outfile"

# Download from YouVersions API

 git clone --recurse https://github.com/Glowstudent777/YouVersion-API.git && cd YouVersion-API
 npm i && npm run build
 curl -X 'GET' \\n  'http://localhost:3000/api/v1/verse?book=JOHN&version=3413-srb16-svenska-reformationsbibeln' \










______________________________________________________________

#!/usr/bin/env python3
"""
download_nt.py
--------------
Fetches every chapter of every New-Testament book (Swedish SRB16)
from a local YouVersion-API clone running on http://localhost:3000,
strips verse numbers / chapter headings, and writes one UTF-8 .txt
file per book in ./srb_bibeln/.

• Requires:  requests  (pip install requests)
• Tested on Python 3.8+ (no other deps)
"""

import os
import re
import unicodedata
from pathlib import Path

import requests
from requests.exceptions import HTTPError

# ------------------------------------------------------------------
BASE_URL   = "http://localhost:3000/api/v1/verse"
VERSION_ID = "3413-srb16-svenska-reformationsbibeln"
OUT_DIR    = Path("srb_bibeln")
OUT_DIR.mkdir(exist_ok=True)
# ------------------------------------------------------------------

BOOKS = [
    "MAT", "MRK", "LUK", "JOHN", "ACT", "ROM", "1CO", "2CO", "GAL", "EPH",
    "PHP", "COL", "1TH", "2TH", "1TI", "2TI", "TIT", "PHM", "HEB", "JAS",
    "1PE", "2PE", "1JN", "2JN", "3JN", "JUD", "REV",
]

SW_NAME = {
    "MAT": "matteusevangeliet", "MRK": "markusevangeliet",
    "LUK": "lukasevangeliet",   "JOHN": "johannesevangeliet",
    "ACT": "apostlagärningarna","ROM": "romarbrevet",
    "1CO": "första_korintherbrevet",   "2CO": "andra_korintherbrevet",
    "GAL": "galaterbrevet",     "EPH": "efesierbrevet",
    "PHP": "filipperbrevet",    "COL": "kolosserbrevet",
    "1TH": "första_thessalonikerbrevet","2TH": "andra_thessalonikerbrevet",
    "1TI": "första_timotheosbrevet",   "2TI": "andra_timotheosbrevet",
    "TIT": "titusbrevet",       "PHM": "filemonbrevet",
    "HEB": "hebreerbrevet",     "JAS": "jakobsbrevet",
    "1PE": "första_petrusbrevet","2PE": "andra_petrusbrevet",
    "1JN": "första_johannesbrevet","2JN": "andra_johannesbrevet",
    "3JN": "tredje_johannesbrevet","JUD": "judasbrevet",
    "REV": "uppenbarelseboken",
}

# ------------------------------------------------------------------
def clean_text(raw_verses: dict) -> str:
    """Join verses, drop numbers / headings, normalise unicode."""
    # keep verses in numerical order
    ordered = [raw_verses[k] for k in sorted(raw_verses, key=lambda v: int(re.sub(r"\D", "", v) or 0))]
    text = "\n".join(ordered)

    # remove leading verse numbers like '12 ', '12:', '12. '
    text = re.sub(r"^[ \t]*\d+[:.]?[ \t]+", "", text, flags=re.M)
    # remove 'Kapitel 3', 'CHAPTER 3', etc.
    text = re.sub(r"^[ \t]*(KAPITEL|CHAPTER)[ \t]+\d+\s*$", "", text, flags=re.M | re.I)
    # squeeze 3+ blank lines to 1
    text = re.sub(r"\n{3,}", "\n\n", text).strip()

    return unicodedata.normalize("NFKD", text)


def fetch_chapter(book_alias: str, chapter: int) -> dict | None:
    """Return JSON for one chapter or None if it doesn't exist."""
    params = {
        "book":   f"{book_alias}{chapter}",
        "verses": "-1",
        "version": VERSION_ID,
    }
    try:
        resp = requests.get(BASE_URL, params=params, headers={"accept": "application/json"})
        resp.raise_for_status()
        data = resp.json()
        # crude guard: ensure a 'verses' dict actually came back
        return data if isinstance(data.get("verses"), dict) else None
    except (HTTPError, ValueError):
        return None


def main() -> None:
    for book in BOOKS:
        out_path = OUT_DIR / f"{SW_NAME.get(book, book.lower())}.txt"
        out_path.write_text("", encoding="utf-8")      # truncate/create
        print(f"⏳  {book} …")

        chapter = 1
        while True:
            payload = fetch_chapter(book, chapter)
            if not payload:
                break

            clean = clean_text(payload["verses"])
            with out_path.open("a", encoding="utf-8") as fh:
                fh.write(clean + "\n\n")

            print(f"   ·  chapter {chapter}")
            chapter += 1

        print(f"✔  {out_path.name} — {len(out_path.read_text(encoding='utf-8').split())} words")

    print(f"\n✅  Finished! Clean NT files live in '{OUT_DIR}/'.")


if __name__ == "__main__":
    main()
