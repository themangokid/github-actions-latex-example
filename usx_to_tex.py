#!/usr/bin/env python3
"""
usx_to_tex.py  -  Convert USX 3.0 Bible files to LaTeX .txt chapter files.

Configuration is read from usx_config.json (same directory).
Re-run this script whenever the USX files or the config change.

Features toggled in usx_config.json → features:
  added_text_highlight  <char style="bk">  →  \\textcolor{addedtext}{…}
  verse_numbers         inline \\versenumber{N}~ before each verse (skips v1)
  section_headings      <para style="s">   →  \\sechead{…} between verse groups
  footnotes             <note style="f">   →  \\footnote{…} after the verse word
  cross_references      <note style="x">   →  \\footnote{\\small …}

Also generates srb_config.tex (LaTeX preamble fragment) and a preview render
file (render/preview.tex) driven by usx_config.json → preview.
"""

import json
import os
import re
import xml.etree.ElementTree as ET

# ---------------------------------------------------------------------------
PROJ      = os.path.dirname(os.path.abspath(__file__))
USX_DIR   = os.path.join(PROJ, "raw_data_bible", "release", "USX_1")
TXT_BASE  = os.path.join(PROJ, "srb_bibeln", "usx")
RENDER_GT = os.path.join(PROJ, "render", "GT")
RENDER_NT = os.path.join(PROJ, "render", "NT")
CFG_FILE  = os.path.join(PROJ, "usx_config.json")
SRB_CFG   = os.path.join(PROJ, "srb_config.tex")
PREVIEW_TEX = os.path.join(PROJ, "render", "preview.tex")

# ---------------------------------------------------------------------------
BOOKS = [
    # (usx_code, swedish_title, testament, render_basename)
    # Gamla Testamentet
    ("GEN", "Första Moseboken",     "GT", "Forsta_Moseboken"),
    ("EXO", "Andra Moseboken",      "GT", "Andra_Moseboken"),
    ("LEV", "Tredje Moseboken",     "GT", "Tredje_Moseboken"),
    ("NUM", "Fjärde Moseboken",     "GT", "Fjarde_Moseboken"),
    ("DEU", "Femte Moseboken",      "GT", "Femte_Moseboken"),
    ("JOS", "Josua",                "GT", "Josua"),
    ("JDG", "Domarboken",           "GT", "Domarboken"),
    ("RUT", "Rut",                  "GT", "Rut"),
    ("1SA", "Första Samuelsboken",  "GT", "Forsta_Samuelsboken"),
    ("2SA", "Andra Samuelsboken",   "GT", "Andra_Samuelsboken"),
    ("1KI", "Första Kungaboken",    "GT", "Forsta_Kungaboken"),
    ("2KI", "Andra Kungaboken",     "GT", "Andra_Kungaboken"),
    ("1CH", "Första Krönikeboken",  "GT", "Forsta_Kronikeboken"),
    ("2CH", "Andra Krönikeboken",   "GT", "Andra_Kronikeboken"),
    ("EZR", "Esra",                 "GT", "Esra"),
    ("NEH", "Nehemja",              "GT", "Nehemja"),
    ("EST", "Ester",                "GT", "Ester"),
    ("JOB", "Job",                  "GT", "Job"),
    ("PSA", "Psaltaren",            "GT", "Psaltaren"),
    ("PRO", "Ordspråksboken",       "GT", "Ordspraksboken"),
    ("ECC", "Predikaren",           "GT", "Predikaren"),
    ("SNG", "Höga Visan",           "GT", "Hoga_Visan"),
    ("ISA", "Jesaja",               "GT", "Jesaja"),
    ("JER", "Jeremia",              "GT", "Jeremia"),
    ("LAM", "Klagovisorna",         "GT", "Klagovisorna"),
    ("EZK", "Hesekiel",             "GT", "Hesekiel"),
    ("DAN", "Daniel",               "GT", "Daniel"),
    ("HOS", "Hosea",                "GT", "Hosea"),
    ("JOL", "Joel",                 "GT", "Joel"),
    ("AMO", "Amos",                 "GT", "Amos"),
    ("OBA", "Obadja",               "GT", "Obadja"),
    ("JON", "Jona",                 "GT", "Jona"),
    ("MIC", "Mika",                 "GT", "Mika"),
    ("NAM", "Nahum",                "GT", "Nahum"),
    ("HAB", "Habackuk",             "GT", "Habackuk"),
    ("ZEP", "Sefanja",              "GT", "Sefanja"),
    ("HAG", "Haggai",               "GT", "Haggai"),
    ("ZEC", "Sakarja",              "GT", "Sakarja"),
    ("MAL", "Malaki",               "GT", "Malaki"),
    # Nya Testamentet
    ("MAT", "Matteusevangeliet",          "NT", "matteus"),
    ("MRK", "Markusevangeliet",           "NT", "markus"),
    ("LUK", "Lukasevangeliet",            "NT", "lukas"),
    ("JHN", "Johannesevangeliet",         "NT", "johannes"),
    ("ACT", "Apostlagärningarna",         "NT", "apostlagarningarna"),
    ("ROM", "Romarbrevet",                "NT", "romarbrevet"),
    ("1CO", "Första Korinthierbrevet",    "NT", "forsta_korinthierbrevet"),
    ("2CO", "Andra Korinthierbrevet",     "NT", "andra_korithierbrevet"),
    ("GAL", "Galatierbrevet",             "NT", "galatierbrevet"),
    ("EPH", "Efesierbrevet",              "NT", "efesierbrevet"),
    ("PHP", "Filipperbrevet",             "NT", "filipperbrevet"),
    ("COL", "Kolosserbrevet",             "NT", "kolosserbrevet"),
    ("1TH", "Första Thessalonikerbrevet", "NT", "forsta_thesselonikerbrevet"),
    ("2TH", "Andra Thessalonikerbrevet",  "NT", "andra_thesselonikerbrevet"),
    ("1TI", "Första Timotheosbrevet",     "NT", "forsta_timotheosbrevet"),
    ("2TI", "Andra Timotheosbrevet",      "NT", "andra_timotheosbrevet"),
    ("TIT", "Titusbrevet",                "NT", "titus"),
    ("PHM", "Filemonbrevet",              "NT", "filemonbrevet"),
    ("HEB", "Hebreerbrevet",              "NT", "hebreerbrevet"),
    ("JAS", "Jakobsbrevet",               "NT", "jakob"),
    ("1PE", "Första Petrusbrevet",        "NT", "forsta_petrus"),
    ("2PE", "Andra Petrusbrevet",         "NT", "andra_petrusbrevet"),
    ("1JN", "Första Johannesbrevet",      "NT", "forsta_johannesbrev"),
    ("2JN", "Andra Johannesbrevet",       "NT", "andra_johannesbrev"),
    ("3JN", "Tredje Johannesbrevet",      "NT", "tredje_johannes_brev"),
    ("JUD", "Judasbrevet",                "NT", "judasbrev"),
    ("REV", "Uppenbarelseboken",          "NT", "uppenbarelseboken"),
]

BOOK_BY_CODE = {code: (sv, t, rb) for code, sv, t, rb in BOOKS}


# ---------------------------------------------------------------------------
# Config loading
# ---------------------------------------------------------------------------

DEFAULT_CFG = {
    "features": {
        "added_text_highlight": True,
        "verse_numbers":        False,
        "section_headings":     False,
        "footnotes":            False,
        "cross_references":     False,
    },
    "added_text_color_rgb": [125, 120, 105],
    "preview": {
        "books":             ["GEN", "MAT"],
        "chapters_per_book": 5,
    },
}


def load_config():
    if not os.path.isfile(CFG_FILE):
        print(f"  No usx_config.json found — using defaults.")
        return DEFAULT_CFG
    with open(CFG_FILE, encoding="utf-8") as f:
        data = json.load(f)
    # Merge with defaults so missing keys always have a value
    cfg = dict(DEFAULT_CFG)
    cfg.update(data)
    cfg["features"] = dict(DEFAULT_CFG["features"])
    cfg["features"].update(data.get("features", {}))
    cfg["preview"] = dict(DEFAULT_CFG["preview"])
    cfg["preview"].update(data.get("preview", {}))
    return cfg


# ---------------------------------------------------------------------------
# LaTeX helpers
# ---------------------------------------------------------------------------

def escape_tex(text):
    if not text:
        return ""
    text = text.replace("%", "\\%")
    text = text.replace("$", "\\$")
    text = text.replace("#", "\\#")
    text = text.replace("&", "\\&")
    text = text.replace("_", "\\_")
    return text


def strip_initial_color(content):
    """
    Remove leading \\textcolor{addedtext}{…} wrapper so the first character
    is always a plain letter (required by ProcessAndRenderFile's drop-cap).
    """
    prefix = r"\textcolor{addedtext}{"
    if not content.startswith(prefix):
        return content
    depth = 0
    start = len(prefix)
    for i, ch in enumerate(content[start:], start):
        if ch == "{":
            depth += 1
        elif ch == "}":
            if depth == 0:
                return content[start:i] + content[i + 1:]
            depth -= 1
    return content  # malformed – return as-is


# ---------------------------------------------------------------------------
# USX parsing  →  event list per chapter
# ---------------------------------------------------------------------------
# Events:
#   ("heading", str)                   — from <para style="s">
#   ("verse",   int, list[str])        — verse_num, text segments
# ---------------------------------------------------------------------------

def _extract_footnote(note_elem):
    """Return LaTeX-escaped footnote body from a <note style="f"> element."""
    parts = []
    for char in note_elem.iter("char"):
        if char.get("style") == "ft":
            text = (char.text or "").strip().lstrip("*").strip()
            if text:
                parts.append(escape_tex(text))
    return " ".join(parts)


def _extract_xref(note_elem):
    """Return LaTeX-escaped cross-reference list from a <note style="x"> element."""
    parts = []
    for char in note_elem:
        if char.get("style") == "xt":
            if char.text:
                parts.append(escape_tex(char.text))
            for ref in char:
                if ref.text:
                    parts.append(escape_tex(ref.text))
                if ref.tail:
                    parts.append(escape_tex(ref.tail))
    text = "".join(parts).strip().rstrip(";").strip()
    return text


def _collect_elem(elem, segs, feat):
    """
    Collect text from one child element of a <para style="m">.
    Handles note (footnote/xref), char (bk = added text), verse markers.
    Does NOT handle verse number tracking — caller does that.
    """
    tag   = elem.tag
    style = elem.get("style", "")

    if tag == "note":
        note_style = style
        if note_style == "f" and feat["footnotes"]:
            body = _extract_footnote(elem)
            if body:
                segs.append(f"\\footnote{{{body}}}")
        elif note_style == "x" and feat["cross_references"]:
            body = _extract_xref(elem)
            if body:
                segs.append(f"\\footnote{{\\small {body}}}")
        # Always collect tail (text after the note tag in the verse flow)
        if elem.tail:
            segs.append(escape_tex(elem.tail))
        return

    if tag == "char" and style == "bk":
        text = escape_tex(elem.text or "")
        if text:
            if feat["added_text_highlight"]:
                segs.append(f"\\textcolor{{addedtext}}{{{text}}}")
            else:
                segs.append(text)
        # Recurse (rare nesting inside bk)
        for child in elem:
            _collect_elem(child, segs, feat)
        if elem.tail:
            segs.append(escape_tex(elem.tail))
        return

    # Generic element: collect text + tail
    if elem.text:
        segs.append(escape_tex(elem.text))
    for child in elem:
        _collect_elem(child, segs, feat)
    if elem.tail:
        segs.append(escape_tex(elem.tail))


def _walk_para(para_elem, events, feat):
    """
    Walk a <para style="m"> element and append verse/heading events.
    Tracks verse transitions via <verse number="N"> start markers.
    """
    cur_vnum = None
    cur_segs = []

    def flush():
        if cur_vnum is not None:
            events.append(("verse", cur_vnum, cur_segs[:]))

    # Para may have leading text before any <verse> (unusual but handle it)
    if para_elem.text and para_elem.text.strip():
        cur_segs.append(escape_tex(para_elem.text))

    for elem in para_elem:
        tag   = elem.tag

        if tag == "verse" and elem.get("number"):
            # Start of a new verse — flush the previous one
            flush()
            cur_vnum = int(elem.get("number"))
            cur_segs = []
            # Tail is the opening text of this verse
            if elem.tail:
                cur_segs.append(escape_tex(elem.tail))

        elif tag == "verse":
            # eid (end) marker — tail is usually whitespace/nothing
            if elem.tail:
                cur_segs.append(escape_tex(elem.tail))

        else:
            _collect_elem(elem, cur_segs, feat)

    flush()


def parse_usx(usx_path, feat):
    """
    Parse one USX file.
    Returns {chapter_num (int): [event, ...]} where events are
    ("heading", str) or ("verse", int, list[str]).
    """
    tree = ET.parse(usx_path)
    root = tree.getroot()

    chapters = {}
    current_ch = None

    for child in root:
        tag   = child.tag
        style = child.get("style", "")

        if tag == "chapter" and child.get("number"):
            current_ch = int(child.get("number"))
            chapters[current_ch] = []

        elif tag == "para" and current_ch is not None:
            if style == "s":
                heading = (child.text or "").strip()
                if heading:
                    chapters[current_ch].append(("heading", heading))
            elif style == "m":
                _walk_para(child, chapters[current_ch], feat)

    return chapters


# ---------------------------------------------------------------------------
# Chapter assembly  →  single .txt string
# ---------------------------------------------------------------------------

def assemble_chapter(events, feat):
    """
    Convert the event list for one chapter into the flat .txt string
    that ProcessAndRenderFile will read.
    """
    parts = []

    for event in events:
        kind = event[0]

        if kind == "heading":
            if feat["section_headings"]:
                heading = escape_tex(event[1])
                parts.append(f"\\sechead{{{heading}}}")

        elif kind == "verse":
            vnum, segs = event[1], event[2]
            verse_text = "".join(segs)
            verse_text = re.sub(r"[ \t]+", " ", verse_text).strip()
            if not verse_text:
                continue
            if feat["verse_numbers"] and vnum > 1:
                verse_text = f"\\versenumber{{{vnum}}}~{verse_text}"
            parts.append(verse_text)

    text = " ".join(parts).strip()
    text = re.sub(r"  +", " ", text)
    text = strip_initial_color(text)
    return text or "—"


# ---------------------------------------------------------------------------
# File writers
# ---------------------------------------------------------------------------

def write_chapter_files(code, chapters_events, feat):
    """Write per-chapter .txt files; return [(ch_num, rel_path), ...]."""
    out_dir = os.path.join(TXT_BASE, code)
    os.makedirs(out_dir, exist_ok=True)
    paths = []
    for ch_num in sorted(chapters_events):
        text  = assemble_chapter(chapters_events[ch_num], feat)
        fname = f"ch{ch_num:03d}.txt"
        with open(os.path.join(out_dir, fname), "w", encoding="utf-8") as f:
            f.write(text)
        paths.append((ch_num, f"srb_bibeln/usx/{code}/{fname}"))
    return paths


def write_render_file(code, sv_title, testament, render_base, chapter_paths):
    """Regenerate one render .tex file."""
    render_dir = RENDER_GT if testament == "GT" else RENDER_NT
    os.makedirs(render_dir, exist_ok=True)
    tex_path = os.path.join(render_dir, render_base + ".tex")

    lines = [
        f"% Generated by usx_to_tex.py — source: USX_1/{code}.usx",
        "% DO NOT EDIT — re-run usx_to_tex.py to regenerate",
        "",
        f"\\invisiblesection{{{sv_title}}}",
        "",
    ]
    for ch_num, rel_path in chapter_paths:
        heading = f"Psalm {ch_num}" if code == "PSA" else f"{sv_title} {ch_num}"
        lines.append(f"\\ProcessAndRenderFile{{{rel_path}}}{{{heading}}}")
    lines.append("")

    with open(tex_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    return tex_path


def write_srb_config(cfg):
    """
    Write srb_config.tex — LaTeX preamble fragment auto-generated from
    usx_config.json.  main.tex should \\input{srb_config} instead of
    hard-coding these definitions.
    """
    feat  = cfg["features"]
    r, g, b = cfg["added_text_color_rgb"]

    active = [k for k, v in feat.items() if v]
    inactive = [k for k, v in feat.items() if not v]

    lines = [
        "% Auto-generated by usx_to_tex.py from usx_config.json — DO NOT EDIT",
        f"% ON:  {', '.join(active) or 'none'}",
        f"% OFF: {', '.join(inactive) or 'none'}",
        "",
        "% Color for translator-added words (50 %% blend of text + paper).",
        f"\\definecolor{{addedtext}}{{RGB}}{{{r},{g},{b}}}",
        "",
        "% Inline section heading between verse groups.",
        "% Injected by the generator when section_headings=true.",
        "\\providecommand{\\sechead}[1]{%",
        "  \\par\\vspace{0.3em}%",
        "  {\\centering\\small\\itshape\\color{titlecolor}#1\\par}%",
        "  \\vspace{0.2em}\\noindent%",
        "}",
        "",
    ]

    with open(SRB_CFG, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"  srb_config.tex written.")


def write_preview(cfg):
    """
    Write render/preview.tex — a small subset for quick test builds.
    Driven by usx_config.json → preview.
    """
    preview_codes  = cfg["preview"].get("books", ["GEN", "MAT"])
    max_chapters   = cfg["preview"].get("chapters_per_book", 5)

    lines = [
        "% Auto-generated by usx_to_tex.py — DO NOT EDIT",
        f"% Preview: {preview_codes}, {max_chapters} chapters each",
        "",
    ]

    for code in preview_codes:
        if code not in BOOK_BY_CODE:
            continue
        sv_title, _, _ = BOOK_BY_CODE[code]
        lines.append(f"\\invisiblesection{{{sv_title}}}")
        lines.append("")
        for ch in range(1, max_chapters + 1):
            rel = f"srb_bibeln/usx/{code}/ch{ch:03d}.txt"
            heading = f"Psalm {ch}" if code == "PSA" else f"{sv_title} {ch}"
            lines.append(f"\\ProcessAndRenderFile{{{rel}}}{{{heading}}}")
        lines.append("")

    os.makedirs(os.path.dirname(PREVIEW_TEX), exist_ok=True)
    with open(PREVIEW_TEX, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"  render/preview.tex written.")


FULL_TEX = os.path.join(PROJ, "render", "full.tex")

def write_full():
    """
    Write render/full.tex — inputs every book render file in canonical order
    with the NT title page inserted between testaments.
    """
    lines = [
        "% Auto-generated by usx_to_tex.py — DO NOT EDIT",
        "% Full Bible: all 66 books in canonical order.",
        "",
        "% ── Gamla Testamentet ──────────────────────────────",
    ]

    nt_separator_written = False
    for code, _, testament, render_base in BOOKS:
        if testament == "NT" and not nt_separator_written:
            lines += [
                "",
                "% ── Nya Testamentet ────────────────────────────────",
                "\\newpage",
                "\\input{front-page/title_text_nya_testamentet}",
                "\\input{front-page/icons_low_quality}",
                "\\newpage",
                "",
            ]
            nt_separator_written = True
        render_dir = "render/GT" if testament == "GT" else "render/NT"
        lines.append(f"\\input{{{render_dir}/{render_base}}}")

    lines.append("")

    os.makedirs(os.path.dirname(FULL_TEX), exist_ok=True)
    with open(FULL_TEX, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"  render/full.tex written.")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    cfg  = load_config()
    feat = cfg["features"]

    print("Config:")
    for k, v in feat.items():
        print(f"  {k}: {v}")
    print()

    write_srb_config(cfg)
    write_preview(cfg)
    write_full()

    processed = 0
    for code, sv_title, testament, render_base in BOOKS:
        usx_path = os.path.join(USX_DIR, f"{code}.usx")
        if not os.path.isfile(usx_path):
            print(f"  SKIP {code}: USX not found")
            continue

        print(f"  {code}  {sv_title}...", end=" ", flush=True)
        chapters_events = parse_usx(usx_path, feat)
        chapter_paths   = write_chapter_files(code, chapters_events, feat)
        tex_path        = write_render_file(code, sv_title, testament,
                                            render_base, chapter_paths)
        print(f"{len(chapters_events)} ch → {os.path.relpath(tex_path, PROJ)}")
        processed += 1

    print(f"\nDone. {processed} books processed.")


if __name__ == "__main__":
    main()
