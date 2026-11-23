"""Generate sample PDFs and compare extraction against their source text."""

import argparse
import html
import json
import unicodedata
from pathlib import Path


def normalize(text):
    """Ignore whitespace and Arabic presentation forms; retain reading order."""
    converted = []
    for char in text:
        codepoint = ord(char)
        if 0xFB50 <= codepoint <= 0xFDFF or 0xFE70 <= codepoint <= 0xFEFC:
            char = unicodedata.normalize("NFKC", char)
        converted.append(char)
    return " ".join(unicodedata.normalize("NFC", "".join(converted)).split())


def extract(pdf, engine):
    if engine == "pypdf":
        from pypdf import PdfReader

        return PdfReader(pdf).pages[0].extract_text()

    import pymupdf

    with pymupdf.open(pdf) as document:
        return document[0].get_text()


def generate(cases, folder):
    import pymupdf

    folder.mkdir(parents=True, exist_ok=True)
    for case in cases:
        direction = case["dir"]
        source = html.escape(case["text"])
        with pymupdf.open() as document:
            page = document.new_page(width=450, height=110)
            area = pymupdf.Rect(24, 24, 426, 86)
            spare, scale = page.insert_htmlbox(
                area,
                f'<div dir="{direction}">{source}</div>',
                css="div {font-size: 22pt;}",
                scale_low=1,
            )
            if spare < 0 or scale != 1:
                raise RuntimeError(f"Text does not fit case {case['id']}")
            document.save(folder / f"{case['id']}.pdf")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--engine", choices=("pypdf", "pymupdf"), default="pypdf")
    parser.add_argument("--fixtures", type=Path, default=Path("generated"))
    parser.add_argument("--generate", action="store_true", help="Regenerate the test PDFs.")
    parser.add_argument("--strict", action="store_true", help="Exit 1 if any text differs.")
    args = parser.parse_args()
    cases = json.loads(Path(__file__).with_name("cases.json").read_text(encoding="utf-8"))
    if args.generate:
        generate(cases, args.fixtures)

    results = []
    for case in cases:
        pdf = args.fixtures / f"{case['id']}.pdf"
        if not pdf.is_file():
            parser.error(f"Missing test file {pdf}. Run with --generate first.")
        actual = normalize(extract(pdf, args.engine))
        expected = normalize(case["text"])
        results.append({
            "case": case["id"],
            "expected": expected,
            "actual": actual,
            "match": actual == expected,
        })
    # ASCII escaping keeps the JSON identical even in non-UTF-8 terminals.
    print(json.dumps({"engine": args.engine, "cases": results}, indent=2))
    return int(args.strict and any(not result["match"] for result in results))


if __name__ == "__main__":
    raise SystemExit(main())
