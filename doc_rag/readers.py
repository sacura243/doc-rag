"""文档读取：txt / pdf / docx（含文本框内容）。"""
import os
import re
import zipfile


def load_txt(file_path: str) -> str:
    for encoding in ("utf-8", "gbk"):
        try:
            with open(file_path, "r", encoding=encoding) as f:
                return f.read()
        except (UnicodeDecodeError, OSError):
            continue
    return ""


def read_pdf(file_path: str) -> str:
    try:
        from pypdf import PdfReader
    except ImportError:
        from PyPDF2 import PdfReader
    parts = []
    for page in PdfReader(file_path).pages:
        text = page.extract_text()
        if text:
            parts.append(text)
    return "\n".join(parts)


def read_docx(file_path: str) -> str:
    """读取 docx：段落 + 表格 + 文本框/画布文字（python-docx 读不到的部分从 XML 补）。"""
    import docx

    d = docx.Document(file_path)
    parts = [p.text.strip() for p in d.paragraphs if p.text.strip()]
    for table in d.tables:
        for row in table.rows:
            parts.append(" | ".join(c.text.strip() for c in row.cells))

    # 补充：文本框/图形画布里的文字（python-docx 不解析，但 XML 里有）
    try:
        with zipfile.ZipFile(file_path) as z:
            xml = z.read("word/document.xml").decode("utf-8", errors="ignore")
        for block in xml.split("</w:p>"):
            t = "".join(re.findall(r"<w:t[^>]*>([^<]*)</w:t>", block)).strip()
            if t and t not in parts:
                parts.append(t)
    except Exception:
        pass  # 解析不到也不影响已有内容

    return "\n".join(parts)


def read_file(file_path: str) -> str:
    ext = os.path.splitext(file_path)[1].lower()
    if ext == ".txt":
        return load_txt(file_path)
    if ext == ".pdf":
        return read_pdf(file_path)
    if ext in (".docx", ".doc"):
        return read_docx(file_path)
    return ""


SUPPORTED_EXTS = (".txt", ".pdf", ".docx")


def iter_docs(folder: str):
    for root, _dirs, files in os.walk(folder):
        for name in files:
            if name.lower().endswith(SUPPORTED_EXTS):
                yield os.path.join(root, name)
