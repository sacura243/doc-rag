"""讯飞星火大模型对话封装（WebSocket）。"""
import base64
import hashlib
import hmac
import json
import ssl
import threading
import time
from datetime import datetime
from time import mktime
from urllib.parse import urlencode, urlparse

import websocket
from wsgiref.handlers import format_date_time

from .config import Config


class SparkChat:
    """一次星火对话会话，失败抛 RuntimeError。"""

    def __init__(self, cfg: Config):
        self.cfg = cfg
        self._answer = ""
        self._error = None
        self._complete = False
        self._done = threading.Event()
        self._text = ""

    def _create_url(self) -> str:
        parsed = urlparse(self.cfg.ws_url)
        date = format_date_time(mktime(datetime.now().timetuple()))
        signature_origin = (
            f"host: {parsed.netloc}\n"
            f"date: {date}\n"
            f"GET {parsed.path} HTTP/1.1"
        )
        signature_sha = hmac.new(
            self.cfg.apisecret.encode("utf-8"),
            signature_origin.encode("utf-8"),
            digestmod=hashlib.sha256,
        ).digest()
        signature = base64.b64encode(signature_sha).decode("utf-8")
        authorization_origin = (
            f'api_key="{self.cfg.apikey}", algorithm="hmac-sha256", '
            f'headers="host date request-line", signature="{signature}"'
        )
        authorization = base64.b64encode(authorization_origin.encode("utf-8")).decode("utf-8")
        params = {"authorization": authorization, "date": date, "host": parsed.netloc}
        return self.cfg.ws_url + "?" + urlencode(params)

    def _on_open(self, ws):
        payload = {
            "header": {"app_id": self.cfg.appid, "uid": str(time.time_ns())},
            "parameter": {"chat": {"domain": self.cfg.domain, "temperature": self.cfg.temperature}},
            "payload": {"message": {"text": [{"role": "user", "content": self._text}]}},
        }
        ws.send(json.dumps(payload, ensure_ascii=False))

    def _on_message(self, ws, message):
        try:
            data = json.loads(message)
        except json.JSONDecodeError:
            self._error = "无效响应"
            self._finish(ws)
            return
        code = data.get("header", {}).get("code", -1)
        if code != 0:
            self._error = f"接口错误 {code}: {data.get('header', {}).get('message', '')}"
            self._finish(ws)
            return
        try:
            choices = data["payload"]["choices"]
            self._answer += choices["text"][0].get("content", "")
            if choices.get("status") == 2:
                self._complete = True
                self._finish(ws)
        except (KeyError, IndexError) as exc:
            self._error = f"响应解析失败: {exc}"
            self._finish(ws)

    def _on_error(self, ws, error):
        self._error = f"连接出错: {error}"
        self._done.set()

    def _finish(self, ws):
        try:
            ws.close()
        finally:
            self._done.set()

    def chat(self, text: str, timeout: float = 120.0) -> str:
        self._text = text
        self._answer = ""
        self._error = None
        self._complete = False
        self._done.clear()
        ws = websocket.WebSocketApp(
            self._create_url(),
            on_open=self._on_open,
            on_message=self._on_message,
            on_error=self._on_error,
        )
        ws.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE}, ping_timeout=10)
        self._done.wait(timeout=5)
        if self._error:
            raise RuntimeError(self._error)
        if not self._complete:
            raise RuntimeError("连接提前关闭，回复不完整")
        return self._answer