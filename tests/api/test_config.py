from api.config import load_api_settings


def test_api_settings_read_storage_paths_from_environment(monkeypatch, tmp_path):
    upload_dir = tmp_path / "uploads"
    database_path = tmp_path / "api.sqlite3"
    monkeypatch.setenv("API_UPLOAD_DIR", str(upload_dir))
    monkeypatch.setenv("API_DATABASE_PATH", str(database_path))

    settings = load_api_settings()

    assert settings.upload_dir == upload_dir
    assert settings.database_path == database_path
