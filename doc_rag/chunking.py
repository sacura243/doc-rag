"""文本分块：按句子切分 + 重叠，防止把一句话拦腰切断。"""


def split_text(text: str, chunk_size: int = 600, chunk_overlap: int = 120) -> list:
    sentences = [
        s.strip()
        for s in text.replace("。", "。\n").replace("？", "？\n").replace("！", "！\n")
        .replace("\r\n", "\n").split("\n")
        if s.strip()
    ]
    chunks, current = [], ""
    for sen in sentences:
        if len(current) + len(sen) <= chunk_size:
            current += sen
        else:
            if current:
                chunks.append(current)
            current = current[-chunk_overlap:] + sen
    if current:
        chunks.append(current)
    return chunks