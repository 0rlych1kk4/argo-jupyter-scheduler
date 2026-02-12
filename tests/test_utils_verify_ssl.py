import pytest

from hera.shared import global_config

from argo_jupyter_scheduler.utils import authenticate


def _set_required_env(monkeypatch):
    monkeypatch.setenv("ARGO_NAMESPACE", "dev")
    monkeypatch.setenv("ARGO_TOKEN", "Bearer abc123")
    monkeypatch.setenv("ARGO_BASE_HREF", "/")
    monkeypatch.setenv("ARGO_SERVER", "argo.example.com")


@pytest.fixture(autouse=True)
def _reset_global_config():
    # Snapshot/restore global_config to avoid cross-test contamination.
    old = {
        "host": getattr(global_config, "host", None),
        "token": getattr(global_config, "token", None),
        "namespace": getattr(global_config, "namespace", None),
        "verify_ssl": getattr(global_config, "verify_ssl", None),
    }
    yield
    global_config.host = old["host"]
    global_config.token = old["token"]
    global_config.namespace = old["namespace"]
    if hasattr(global_config, "verify_ssl"):
        global_config.verify_ssl = old["verify_ssl"]


def test_authenticate_defaults_verify_ssl_true(monkeypatch):
    _set_required_env(monkeypatch)
    monkeypatch.delenv("ARGO_VERIFY_SSL", raising=False)

    cfg = authenticate()
    assert cfg.verify_ssl is True


@pytest.mark.parametrize("val", ["false", "False", "0", "no", "off", " OFF "])
def test_authenticate_verify_ssl_false(monkeypatch, val):
    _set_required_env(monkeypatch)
    monkeypatch.setenv("ARGO_VERIFY_SSL", val)

    cfg = authenticate()
    assert cfg.verify_ssl is False


@pytest.mark.parametrize("val", ["true", "True", "1", "yes", "on", " ON "])
def test_authenticate_verify_ssl_true(monkeypatch, val):
    _set_required_env(monkeypatch)
    monkeypatch.setenv("ARGO_VERIFY_SSL", val)

    cfg = authenticate()
    assert cfg.verify_ssl is True


def test_authenticate_invalid_verify_ssl_raises(monkeypatch):
    _set_required_env(monkeypatch)
    monkeypatch.setenv("ARGO_VERIFY_SSL", "maybe")

    with pytest.raises(ValueError):
        authenticate()
