"""Streamlit Web UI for the document RAG application."""
from __future__ import annotations

import os
import html
from pathlib import Path

import streamlit as st

from doc_rag.config import load_config
from doc_rag.rag import ask_with_sources, ingest_folder
from doc_rag.vector_store import VectorStore


PROJECT_DIR = Path(__file__).resolve().parent
DEFAULT_DOC_DIR = PROJECT_DIR / "test_docs"


st.set_page_config(
    page_title="文档智能问答",
    page_icon="Q",
    layout="wide",
    initial_sidebar_state="expanded",
)


def apply_style() -> None:
    st.markdown(
        """
        <style>
        :root {
          --ink: #172033;
          --muted: #61708b;
          --line: #d9e1ea;
          --accent: #0f9cae;
          --surface: #ffffff;
          --soft: #f4f7f8;
        }
        .stApp { background: #f6f8fa; color: var(--ink); }
        [data-testid="stSidebar"] { background: #ffffff; border-right: 1px solid var(--line); }
        [data-testid="stSidebar"] > div:first-child { padding-top: 1.5rem; }
        .block-container { max-width: 1180px; padding-top: 4rem; padding-bottom: 3rem; }
        h1, h2, h3 { color: var(--ink); letter-spacing: 0 !important; }
        h1 { font-size: 2rem !important; margin-bottom: 0.25rem !important; }
        .subtitle { color: var(--muted); margin-bottom: 1.8rem; }
        .status-row { border-top: 1px solid var(--line); border-bottom: 1px solid var(--line); padding: 0.75rem 0; margin: 1.25rem 0 1.75rem; color: var(--muted); }
        .status-number { color: var(--ink); font-weight: 700; }
        .answer { background: #ffffff; border-left: 4px solid var(--accent); padding: 1.2rem 1.3rem; margin-top: 0.6rem; white-space: pre-wrap; line-height: 1.75; }
        .source-label { color: var(--muted); font-size: 0.86rem; }
        .stButton > button { background: #0f9cae; color: white; border: 1px solid #0f9cae; border-radius: 6px; min-height: 2.5rem; font-weight: 600; }
        .stButton > button:hover { background: #087b8b; border-color: #087b8b; color: white; }
        [data-testid="stSidebar"] .stButton > button { width: 100%; }
        .stTextInput input, .stTextArea textarea { border-radius: 6px !important; border-color: #c8d2dd !important; }
        @media (max-width: 760px) {
          .block-container { padding: 2.5rem 1rem 2rem; }
          h1 { font-size: 1.65rem !important; }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


@st.cache_resource
def get_config():
    return load_config(str(PROJECT_DIR / "config.toml"))


def knowledge_base_count(cfg) -> int:
    try:
        return VectorStore(cfg.db_dir, cfg.collection).count()
    except Exception:
        return 0


def choose_document_folder() -> str:
    """Open the native Windows folder picker for this local-only application."""
    try:
        import tkinter as tk
        from tkinter import filedialog

        root = tk.Tk()
        root.withdraw()
        root.attributes("-topmost", True)
        selected = filedialog.askdirectory(title="选择要导入的文档文件夹")
        root.destroy()
        return selected
    except Exception:
        return ""


def render_sources(sources: list[dict]) -> None:
    if not sources:
        return
    st.divider()
    st.subheader("检索来源")
    for index, item in enumerate(sources, start=1):
        source_name = os.path.basename(item["source"])
        with st.expander(f"{index}. {source_name}", expanded=False):
            st.caption(item["source"])
            st.write(item["content"])


apply_style()

try:
    cfg = get_config()
except SystemExit:
    st.error("未找到讯飞 API 配置。请先填写 config.toml 或设置 XF_APPID、XF_APIKEY、XF_APISECRET。")
    st.stop()
except Exception as exc:
    st.error(f"读取配置失败：{exc}")
    st.stop()

if "doc_dir" not in st.session_state:
    st.session_state.doc_dir = str(DEFAULT_DOC_DIR)

with st.sidebar:
    st.markdown("### 知识库管理")
    st.caption("导入本机目录中的 TXT、PDF 或 DOCX 文档。")
    if st.button("选择本机文件夹", use_container_width=True):
        selected_folder = choose_document_folder()
        if selected_folder:
            st.session_state.doc_dir = selected_folder
            st.rerun()
        st.warning("没有选择文件夹，可重新点击按钮。")
    st.text_input("文档目录", key="doc_dir", placeholder=r"例如 D:\资料")
    if st.button("导入文档", use_container_width=True):
        folder = st.session_state.doc_dir.strip()
        if not folder:
            st.warning("请先填写文档目录。")
        elif not os.path.isdir(folder):
            st.error("找不到该目录，请检查路径。")
        else:
            try:
                with st.spinner("正在读取、分块并写入知识库..."):
                    count = ingest_folder(cfg, folder)
                st.success(f"已处理 {count} 个文档。")
                st.rerun()
            except Exception as exc:
                st.error(f"导入失败：{exc}")

    st.divider()
    st.caption("向量库保存在本项目的 chroma_db 目录中。")


chunk_count = knowledge_base_count(cfg)
st.title("文档智能问答")
st.markdown("把自己的资料变成可检索、可追溯的知识库。")
st.markdown(
    f'<div class="status-row">当前知识库：<span class="status-number">{chunk_count}</span> 个文本片段</div>',
    unsafe_allow_html=True,
)

question = st.text_area(
    "你的问题",
    placeholder="例如：这份资料里提到的核心流程是什么？",
    height=118,
    label_visibility="collapsed",
)

left, right = st.columns([1, 5], vertical_alignment="center")
with left:
    ask_clicked = st.button("开始问答", type="primary", use_container_width=True)
with right:
    top_k = st.select_slider(
        "检索范围（每次参考的原文片段数量）",
        options=[2, 3, 4, 5, 6],
        value=4,
        help="资料少时选 2-3 段更聚焦；问题复杂时选 5-6 段更全面。",
    )

if ask_clicked:
    if not question.strip():
        st.warning("请输入一个问题。")
    elif chunk_count == 0:
        st.warning("知识库还是空的，请先在左侧导入文档。")
    else:
        try:
            with st.spinner("正在检索资料并生成回答..."):
                answer, sources = ask_with_sources(cfg, question.strip(), top_k)
            st.subheader("回答")
            st.markdown(
                f'<div class="answer">{html.escape(answer)}</div>',
                unsafe_allow_html=True,
            )
            render_sources(sources)
        except Exception as exc:
            st.error(f"问答失败：{exc}")
