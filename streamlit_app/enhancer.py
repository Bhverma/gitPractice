import re
from typing import Optional


def enhance_resume(text: str) -> str:
    """A simple, local heuristic-based resume enhancer.

    This will:
    - Normalize whitespace
    - Ensure consistent bullet points
    - Add simple section headers if detected
    - Reflow long lines
    - Return a plain text enhanced resume
    """
    # Normalize CRLF and whitespace
    text = text.replace('\r\n', '\n').strip()

    # Basic section header normalization: detect common headers and uppercase them
    headers = ["summary", "experience", "education", "skills", "projects", "certifications", "publications"]
    for h in headers:
        # replace case-insensitive header lines like 'Experience:' or 'Experience\n' with 'EXPERIENCE\n'
        pattern = re.compile(rf"^\s*{h}\s*[:\-]?\s*$", flags=re.IGNORECASE | re.MULTILINE)
        text = pattern.sub(h.upper(), text)

    # Normalize bullets: convert -, *, • to '-'
    text = re.sub(r"^[ \t]*[\-\*•]\s+", "- ", text, flags=re.MULTILINE)

    # Ensure bullets are indented under headers (simple heuristic)
    lines = text.split('\n')
    out_lines = []
    in_section = False
    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped.upper() in [h.upper() for h in headers]:
            out_lines.append(stripped.upper())
            in_section = True
            continue
        if in_section and stripped and not stripped.startswith('-') and ':' not in stripped:
            # maybe a paragraph under header; keep as-is
            out_lines.append(stripped)
            continue
        out_lines.append(line)

    text = '\n'.join(out_lines)

    # Reflow long lines (naive 80-char wrap)
    def wrap_line(s, width=80):
        if len(s) <= width:
            return s
        words = s.split(' ')
        lines = []
        cur = ''
        for w in words:
            if len(cur) + 1 + len(w) <= width:
                cur = (cur + ' ' + w).strip()
            else:
                lines.append(cur)
                cur = w
        if cur:
            lines.append(cur)
        return '\n'.join(lines)

    wrapped = []
    for line in text.split('\n'):
        if line.strip().startswith('-'):
            wrapped.append(line)
        else:
            wrapped.append(wrap_line(line))

    text = '\n'.join(wrapped)

    # Improve bullets ordering (simple dedupe of consecutive bullets)
    text = re.sub(r"(-\s+.+)(\n-\s+.+)+", lambda m: '\n'.join(dict.fromkeys(m.group(0).split('\n'))), text)

    return text


def extract_text_from_bytes(data: bytes, filename: Optional[str] = None) -> str:
    """Extract plain text from bytes for .txt, .pdf, or .docx uploads.

    - If filename ends with .pdf -> uses pypdf
    - If filename ends with .docx -> uses python-docx
    - Otherwise, tries to decode as utf-8 text
    """
    if filename:
        lower = filename.lower()
        if lower.endswith('.pdf'):
            try:
                from PyPDF2 import PdfReader
            except Exception as e:
                raise RuntimeError('PyPDF2 is required to parse PDF files. Install python package "pypdf2" or "pypdf".')
            from io import BytesIO
            reader = PdfReader(BytesIO(data))
            pages = [p.extract_text() or '' for p in reader.pages]
            return "\n\n".join(pages)
        if lower.endswith('.docx'):
            try:
                import docx
            except Exception:
                raise RuntimeError('python-docx is required to parse .docx files. Install package "python-docx".')
            from io import BytesIO
            doc = docx.Document(BytesIO(data))
            paragraphs = [p.text for p in doc.paragraphs]
            return "\n\n".join(paragraphs)

    # fallback text decode
    try:
        return data.decode('utf-8')
    except Exception:
        # try latin-1 as a gentle fallback
        return data.decode('latin-1', errors='ignore')
