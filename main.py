"""doc-rag 命令行工具

用法示例：
  python main.py summarize --input E:\资料 --output E:\总结
  python main.py ingest --dir E:\资料
  python main.py ask "这份文档的核心结论是什么？" --top-k 4
"""
import argparse
import os
import sys

from doc_rag.config import load_config
from doc_rag.readers import iter_docs, read_file
from doc_rag.llm import SparkChat
from doc_rag.rag import ask, ingest_folder


# Windows 控制台中文输出修复（避免乱码）
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")


def cmd_summarize(cfg, args):
    os.makedirs(args.output, exist_ok=True)
    ok = skipped = failed = 0
    for path in iter_docs(args.input):
        base = os.path.splitext(os.path.basename(path))[0]
        out_name = os.path.join(args.output, f"{base}_总结结果.txt")
        if os.path.exists(out_name):
            print(f"已处理过，跳过: {path}")
            skipped += 1
            continue
        doc_text = read_file(path)
        if not doc_text.strip():
            print(f"无有效内容，跳过: {path}")
            skipped += 1
            continue
        if len(doc_text) > cfg.max_text_len:
            doc_text = doc_text[:cfg.max_text_len]
            print(f"内容过长已截断: {path}")
        prompt = f"认真阅读下面文档，条理清晰提炼核心要点，分点输出：\n{doc_text}"
        try:
            result = SparkChat(cfg).chat(prompt)
        except Exception as e:
            print(f"请求失败: {path} -> {e}")
            failed += 1
            continue
        if not result.strip():
            print(f"无有效结果，跳过: {path}")
            failed += 1
            continue
        with open(out_name, "w", encoding="utf-8") as f:
            f.write(result)
        print(f"已保存: {out_name}")
        ok += 1
    print(f"\n完成：成功 {ok}，跳过 {skipped}，失败 {failed}")


def cmd_ingest(cfg, args):
    n = ingest_folder(cfg, args.dir)
    print(f"共处理 {n} 个文档")


def cmd_ask(cfg, args):
    print(ask(cfg, args.question, top_k=args.top_k))


def main():
    parser = argparse.ArgumentParser(description="文档智能处理与 RAG 问答系统")
    parser.add_argument("--config", help="配置文件路径（config.toml），不填则读环境变量")
    sub = parser.add_subparsers(dest="command", required=True)

    p_sum = sub.add_parser("summarize", help="批量总结文档")
    p_sum.add_argument("--input", required=True, help="文档目录")
    p_sum.add_argument("--output", required=True, help="总结输出目录")
    p_sum.set_defaults(func=cmd_summarize)

    p_in = sub.add_parser("ingest", help="文档入库（分块+向量化）")
    p_in.add_argument("--dir", required=True, help="文档目录")
    p_in.set_defaults(func=cmd_ingest)

    p_ask = sub.add_parser("ask", help="基于知识库问答")
    p_ask.add_argument("question", help="问题")
    p_ask.add_argument("--top-k", type=int, default=4)
    p_ask.set_defaults(func=cmd_ask)

    args = parser.parse_args()
    cfg = load_config(args.config)
    args.func(cfg, args)


if __name__ == "__main__":
    main()