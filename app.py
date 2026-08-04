"""Local engineering-document RAG workbench built with Streamlit."""
from __future__ import annotations

import html
import os
import shutil
from pathlib import Path
from uuid import uuid4

import streamlit as st

from doc_rag.config import load_config
from doc_rag.rag import ask_with_sources, ingest_files
from doc_rag.vector_store import VectorStore


PROJECT_DIR = Path(__file__).resolve().parent
UPLOAD_DIR = PROJECT_DIR / "uploaded_docs"
DEMO_DIR = PROJECT_DIR / "demo_product_docs"
ACCEPTED_EXTENSIONS = ["txt", "pdf", "docx"]

st.set_page_config(page_title="企业知识库智能助手", page_icon="K", layout="wide")


def apply_style() -> None:
    st.markdown(
        """
        <style>
        :root { --ink:#192534; --muted:#657789; --line:#d8e1e8; --accent:#167c87; --soft:#f3f7f8; }
        .stApp { background:#f7f9fa; color:var(--ink); }
        [data-testid="stSidebar"] { background:#fff; border-right:1px solid var(--line); }
        [data-testid="stSidebar"] > div:first-child { padding-top:1.35rem; }
        .block-container { max-width:1120px; padding-top:3rem; padding-bottom:2.5rem; }
        h1,h2,h3 { color:var(--ink); letter-spacing:0 !important; }
        h1 { font-size:2rem !important; margin-bottom:.35rem !important; }
        .lead { color:var(--muted); margin-bottom:1.5rem; }
        .metric-band { display:flex; gap:2.5rem; padding:.82rem 0; margin:1.2rem 0 1.5rem; border-top:1px solid var(--line); border-bottom:1px solid var(--line); color:var(--muted); }
        .metric-band strong { color:var(--ink); font-size:1.08rem; }
        .answer { background:#fff; border-left:4px solid var(--accent); padding:1.05rem 1.2rem; line-height:1.75; white-space:pre-wrap; }
        .user-q { color:#345167; font-weight:650; margin:.5rem 0; }
        .stButton > button { background:var(--accent); color:#fff; border:1px solid var(--accent); border-radius:6px; min-height:2.4rem; font-weight:600; }
        .stButton > button:hover { background:#106773; border-color:#106773; color:#fff; }
        .stTextInput input,.stTextArea textarea { border-radius:6px !important; border-color:#c9d4dc !important; }
        [data-testid="stFileUploader"] { background:#fff; border:1px dashed #aabcc8; border-radius:8px; padding:.45rem; }
        @media (max-width:760px) { .block-container { padding:2.2rem 1rem 2rem; } h1 { font-size:1.6rem !important; } }
        </style>
        """,
        unsafe_allow_html=True,
    )


@st.cache_resource
def get_config():
    return load_config(str(PROJECT_DIR / "config.toml"))


def get_store(cfg) -> VectorStore:
    return VectorStore(cfg.db_dir, cfg.collection)


def save_uploads(uploaded_files) -> list[str]:
    UPLOAD_DIR.mkdir(exist_ok=True)
    paths = []
    for uploaded in uploaded_files:
        safe_name = Path(uploaded.name).name
        path = UPLOAD_DIR / f"{uuid4().hex}_{safe_name}"
        path.write_bytes(uploaded.getbuffer())
        paths.append(str(path))
    return paths


def display_source_name(source: str) -> str:
    name = Path(source).name
    return name.split("_", 1)[-1] if "_" in name else name


def render_sources(sources: list[dict]) -> None:
    if not sources:
        return
    st.caption("回答依据")
    for index, item in enumerate(sources, start=1):
        suffix = f" · 第 {item['page']} 页" if item.get("page") else ""
        with st.expander(f"{index}. {display_source_name(item['source'])}{suffix}", expanded=False):
            st.caption(item["source"])
            st.write(item["content"])


def render_history() -> None:
    for item in reversed(st.session_state.history):
        st.markdown(f'<div class="user-q">问题：{html.escape(item["question"])}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="answer">{html.escape(item["answer"])}</div>', unsafe_allow_html=True)
        render_sources(item["sources"])
        st.divider()


apply_style()
try:
    cfg = get_config()
except SystemExit:
    st.error("未找到讯飞 API 配置。请先填写 config.toml 或设置环境变量。")
    st.stop()

if "history" not in st.session_state:
    st.session_state.history = []

store = get_store(cfg)
source_items = store.source_summary()
chunk_count = store.count()

with st.sidebar:
    st.markdown("### 知识库管理")
    st.caption("导入产品文档、运营 SOP、FAQ、会议纪要或任意业务资料。")
    files = st.file_uploader("上传业务资料", type=ACCEPTED_EXTENSIONS, accept_multiple_files=True)
    if st.button("上传并导入", use_container_width=True, disabled=not files):
        try:
            with st.spinner("正在解析、分块并建立索引..."):
                result = ingest_files(cfg, save_uploads(files))
            st.success(f"已导入 {result['files']} 个文件，新增 {result['chunks']} 个片段。")
            st.rerun()
        except Exception as exc:
            st.error(f"导入失败：{exc}")

    if DEMO_DIR.exists() and st.button("导入互联网产品资料样例", use_container_width=True):
        with st.spinner("正在导入产品资料样例..."):
            result = ingest_files(cfg, [str(path) for path in DEMO_DIR.glob("*") if path.suffix.lower() in (".txt", ".pdf", ".docx")])
        st.success(f"已导入 {result['files']} 个演示文件。")
        st.rerun()

    st.divider()
    st.markdown("#### 已导入资料")
    if source_items:
        for item in source_items:
            st.caption(f"{display_source_name(item['source'])} · {item['chunks']} 个片段")
    else:
        st.caption("暂无资料，可上传文件或导入工程演示资料。")

    st.divider()
    if st.button("清空并重建知识库", use_container_width=True):
        store.reset()
        st.session_state.history = []
        st.success("知识库已清空。")
        st.rerun()


st.title("企业知识库智能助手")
st.markdown("面向产品、运营、客服等团队的本地知识库问答。每条回答均可回看原文依据。", unsafe_allow_html=True)
st.markdown(
    f'<div class="metric-band"><span>已导入资料 <strong>{len(source_items)}</strong> 份</span><span>知识库片段 <strong>{chunk_count}</strong> 条</span><span>问答记录 <strong>{len(st.session_state.history)}</strong> 条</span></div>',
    unsafe_allow_html=True,
)

sample_questions = [
    "请选择一个示例问题",
    "新用户注册后可以使用哪些核心功能？",
    "退款申请的处理时效和流程是什么？",
    "本周产品迭代中各角色的待办是什么？",
]
selected = st.selectbox("工程场景示例", sample_questions, label_visibility="collapsed")
question = st.text_area(
    "问题",
    value="" if selected == sample_questions[0] else selected,
    placeholder="例如：退款申请的处理时效和流程是什么？",
    height=104,
    label_visibility="collapsed",
)

col1, col2, col3 = st.columns([1.25, 1.55, 4.2], vertical_alignment="center")
with col1:
    ask_clicked = st.button("开始问答", type="primary", use_container_width=True)
with col2:
    top_k = st.select_slider("引用片段", options=[2, 3, 4, 5, 6], value=4, label_visibility="collapsed")
with col3:
    if st.button("清空对话记录"):
        st.session_state.history = []
        st.rerun()

if ask_clicked:
    if not question.strip():
        st.warning("请输入一个问题。")
    elif chunk_count == 0:
        st.warning("知识库为空，请先在左侧上传资料或导入产品资料样例。")
    else:
        try:
            with st.spinner("正在检索资料并生成回答..."):
                answer, sources = ask_with_sources(cfg, question.strip(), top_k)
            st.session_state.history.append({"question": question.strip(), "answer": answer, "sources": sources})
        except Exception as exc:
            st.error(f"问答失败：{exc}")

if st.session_state.history:
    st.subheader("问答记录")
    render_history()
else:
    st.info("先导入资料，再输入一个业务问题。系统会给出回答，并展示对应原文片段。")
