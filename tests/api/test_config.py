import pytest

from api.config import load_api_settings, validate_production_settings
from doc_rag.config import load_config


def test_api_settings_read_storage_paths_from_environment(monkeypatch, tmp_path):
    upload_dir = tmp_path / "uploads"
    database_path = tmp_path / "api.sqlite3"
    monkeypatch.setenv("API_UPLOAD_DIR", str(upload_dir))
    monkeypatch.setenv("API_DATABASE_PATH", str(database_path))

    settings = load_api_settings()

    assert settings.upload_dir == upload_dir
    assert settings.database_path == database_path


def test_rag_config_reads_local_config_toml_when_environment_is_empty(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    (tmp_path / "config.toml").write_text(
        'appid = "local-app"\napikey = "local-key"\napisecret = "local-secret"\nembed_backend = "local"\n',
        encoding="utf-8",
    )
    for name in ("XF_APPID", "XF_APIKEY", "XF_APISECRET", "XF_EMB_APPID", "XF_EMB_APIKEY", "XF_EMB_APISECRET"):
        monkeypatch.delenv(name, raising=False)

    config = load_config()

    assert config.appid == "local-app"
    assert config.apikey == "local-key"
    assert config.apisecret == "local-secret"


def test_production_settings_reject_missing_auth_and_explicit_cors(monkeypatch):
    monkeypatch.setenv("API_ENV", "production")
    monkeypatch.setenv("API_JWT_SECRET", "short")
    monkeypatch.delenv("WECHAT_APPID", raising=False)
    monkeypatch.delenv("WECHAT_APPSECRET", raising=False)
    monkeypatch.setenv("API_CORS_ORIGINS", "http://localhost")

    with pytest.raises(ValueError, match="API_JWT_SECRET"):
        validate_production_settings(load_api_settings())


def test_production_settings_accept_valid_configuration(monkeypatch):
    monkeypatch.setenv("API_ENV", "production")
    monkeypatch.setenv("API_JWT_SECRET", "a" * 48)
    monkeypatch.setenv("WECHAT_APPID", "wx-test")
    monkeypatch.setenv("WECHAT_APPSECRET", "secret")
    monkeypatch.setenv("API_CORS_ORIGINS", "https://servicewechat.com")

    validate_production_settings(load_api_settings())
