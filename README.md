# Arabic PDF Test Kit

Measure whether a PDF text extractor returns Arabic in logical reading order. The six original sample strings cover plain Arabic, Arabic with western and Arabic-Indic digits, mixed Arabic and English, parentheses and punctuation, and an English control case. The kit generates the PDFs locally from the source strings.

## Run

```sh
python -m pip install pypdf pymupdf
python benchmark.py --generate --engine pypdf
python benchmark.py --engine pymupdf
```

Each command prints a JSON report with the expected value, actual value, and match status. Parse the JSON to display the Arabic characters. Use `--fixtures` to select the PDF directory. Add `--strict` to return exit code 1 on any difference. A mismatch means that the extractor did not recover the original string for this fixture, including any difference in placement of punctuation or digits.

The comparison collapses whitespace and normalizes Arabic presentation forms while retaining character and token order. The tool measures one PDF producer and a small set of samples. Real documents, scan/OCR workflows, and other producers need separate tests.

The underlying class of issue is discussed in [pypdf #1629](https://github.com/py-pdf/pypdf/issues/1629). The corpus does not include attachments from that issue.

In a baseline run using PyMuPDF 1.27.1 to generate the PDFs, pypdf 7.1.1 matched 1 of 6 cases and PyMuPDF 1.27.1 matched 2 of 6. Both matched the English control. These are fixture results, not estimates of overall library accuracy.

The source and sample strings use the 0BSD license. The optional tools used to produce and read PDFs retain their own licenses.
