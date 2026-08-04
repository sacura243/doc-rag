"""配置：支持环境变量或配置文件（config.toml）。"""
import os
import sys
from dataclasses import dataclass
from typing import Optional


@dataclass
class Config:
    appid: str = ""
    apikey: str = ""
    apisecret: str = ""
    ws_url: str = "wss://spark-api.xf-yun.com/v1.1/chat"
    domain: str = "lite"
    temperature: float = 0.3
    emb_url: str = "https://embedding.xf-yun.com/v1"
    db_dir: str = "./chroma_db"
    collection: str = "docs"
    chunk_size: int = 600
    chunk_overlap: int = 120
    max_text_len: int = 8000
    # 向量化后端: "local"（本地免费 bge，默认）或 "xfyun"（讯飞，需授权）
    embed_backend: str = "local"
    embed_model: str = "BAAI/bge-small-zh-v1.5"
    embed_cache_dir: str = "./models"


def _load_toml(path: str) -> dict:
    try:
        import tomllib
    except ImportError:
        sys.exit("配置文件需要 Python 3.11+；或直接使用环境变量 XF_APPID/XF_APIKEY/XF_APISECRET")
    with open(path, "rb") as f:
        return tomllib.load(f)


def load_config(config_path: Optional[str] = None) -> Config:
    cfg = Config(
        appid=os.getenv("XF_APPID", ""),
        apikey=os.getenv("XF_APIKEY", ""),
        apisecret=os.getenv("XF_APISECRET", ""),
    )
    if config_path:
        d = _load_toml(config_path)
        for k in (
            "appid", "apikey", "apisecret", "ws_url", "domain", "temperature",
            "emb_url", "db_dir", "collection", "chunk_size", "chunk_overlap",
            "max_text_len", "embed_backend", "embed_model", "embed_cache_dir",
        ):
            if k in d:
                setattr(cfg, k, d[k])
    # embedding 密钥回退
    if not cfg.appid:
        cfg.appid = os.getenv("XF_EMB_APPID", "")
    if not cfg.apikey:
        cfg.apikey = os.getenv("XF_EMB_APIKEY", "")
    if not cfg.apisecret:
        cfg.apisecret = os.getenv("XF_EMB_APISECRET", "")
    if not (cfg.appid and cfg.apikey and cfg.apisecret):
        sys.exit("缺少 API 配置：请设置环境变量 XF_APPID/XF_APIKEY/XF_APISECRET，或用 --config 指定配置文件")
    return cfg
