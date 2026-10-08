from types import SimpleNamespace

import anthropic
import httpx2 as httpx
import pytest

from router.cliente import ErroExecucao, executar, get_client


class FakeClient:
    def __init__(self, erro=None):
        self.erro, self.messages, self.kw = erro, self, None

    def create(self, **kw):
        self.kw = kw
        if self.erro:
            raise self.erro
        return SimpleNamespace(
            content=[SimpleNamespace(type="text", text="olá")],
            usage=SimpleNamespace(input_tokens=5, output_tokens=7),
        )


def test_executar_ok():
    fake = FakeClient()
    r = executar("oi", "haiku", client=fake)
    assert (r.texto, r.tokens_in, r.tokens_out) == ("olá", 5, 7)
    assert fake.kw["model"]


def test_modelo_desconhecido():
    with pytest.raises(ErroExecucao):
        executar("oi", "gpt", client=FakeClient())


def test_erro_da_api_vira_erro_execucao():
    req = httpx.Request("POST", "https://x")
    with pytest.raises(ErroExecucao):
        executar("oi", "opus", client=FakeClient(anthropic.APIConnectionError(request=req)))


def test_sem_chave(monkeypatch):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    monkeypatch.setattr("router.cliente.load_dotenv", lambda: None)
    with pytest.raises(ErroExecucao, match="ANTHROPIC_API_KEY"):
        get_client()
