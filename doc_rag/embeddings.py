"""向量化模块：支持本地免费模型（默认）和讯飞 Embedding（可一键切换）。

- local（默认）：本地 bge-small-zh-v1.5，离线免费、无需授权、中文效果好
- xfyun：讯飞「文本向量化(新版本)」，需在讯飞平台单独申请授权

切换方式：config.toml 里写 embed_backend = "local" 或 "xfyun"
"""
import base64
import hashlib
import hmac
import json
import struct
import time
from datetime import datetime
from time import mktime
from urllib.parse import urlencode, urlparse

import requests
from wsgiref.handlers import format_date_time

from .config import Config

# 讯飞 Embedding 端点（备用：开通授权后可切回）
EMB_P_URL = "https://cn-huabei-1.xf-yun.com/v1/private/sa8a05c27"  # 文档向量化
EMB_Q_URL = "https://cn-huabei-1.xf-yun.com/v1/private/s50d55a16"  # 问题向量化

_model = None  # 本地模型单例（只加载一次）


def _get_local_model(cfg: Config):
    """懒加载本地 bge 模型，避免重复加载浪费时间。"""
    global _model
    if _model is None:
        from fastembed import TextEmbedding
        _model = TextEmbedding(cfg.embed_model, cache_dir=cfg.embed_cache_dir)
    return _model


def _embed_local_documents(texts, cfg):
    m = _get_local_model(cfg)
    return [v.tolist() for v in m.embed(texts)]


def _embed_local_query(text, cfg):
    m = _get_local_model(cfg)
    return next(iter(m.embed([text]))).tolist()


# ==================== 讯飞实现（保留，方便以后切回） ====================
def _signed_url(url: str, apikey: str, apisecret: str) -> str:
    parsed = urlparse(url)
    date = format_date_time(mktime(datetime.now().timetuple()))
    signature_origin = f"host: {parsed.netloc}\ndate: {date}\nPOST {parsed.path} HTTP/1.1"
    signature_sha = hmac.new(
        apisecret.encode(), signature_origin.encode(), digestmod=hashlib.sha256
    ).digest()
    signature = base64.b64encode(signature_sha).decode()
    authorization_origin = (
        f'api_key="{apikey}", algorithm="hmac-sha256", '
        f'headers="host date request-line", signature="{signature}"'
    )
    authorization = base64.b64encode(authorization_origin.encode()).decode()
    params = {"authorization": authorization, "date": date, "host": parsed.netloc}
    return url + "?" + urlencode(params)


def _xfyun_embed_one(text: str, cfg: Config, url: str) -> list:
    payload_text = base64.b64encode(
        json.dumps({"messages": [{"content": text, "role": "user"}]}, ensure_ascii=False).encode("utf-8")
    ).decode()
    body = {
        "header": {"app_id": cfg.appid, "uid": str(int(time.time() * 1000)), "status": 3},
        "parameter": {"emb": {"feature": {"encoding": "utf8"}}},
        "payload": {"messages": {"text": payload_text}},
    }
    resp = requests.post(_signed_url(url, cfg.apikey, cfg.apisecret), json=body, timeout=60)
    resp.raise_for_status()
    result = resp.json()
    code = result["header"]["code"]
    if code != 0:
        raise RuntimeError(f"embedding 错误 {code}: {result['header'].get('message')}")
    text_b64 = result["payload"]["feature"]["text"]
    raw = base64.b64decode(text_b64)
    n = len(raw) // 4
    return list(struct.unpack("<%df" % n, raw[: n * 4]))


def _xfyun_embed_documents(texts: list, cfg: Config) -> list:
    vectors = []
    for i, t in enumerate(texts, 1):
        vectors.append(_xfyun_embed_one(t, cfg, EMB_P_URL))
        print(f"  已向量化 {i}/{len(texts)}")
    return vectors


def _xfyun_embed_query(text: str, cfg: Config) -> list:
    return _xfyun_embed_one(text, cfg, EMB_Q_URL)


# ==================== 统一入口（按配置切换） ====================
def embed_documents(texts: list, cfg: Config) -> list:
    if cfg.embed_backend == "xfyun":
        return _xfyun_embed_documents(texts, cfg)
    return _embed_local_documents(texts, cfg)


def embed_query(text: str, cfg: Config) -> list:
    if cfg.embed_backend == "xfyun":
        return _xfyun_embed_query(text, cfg)
    return _embed_local_query(text, cfg)
