from types import SimpleNamespace

import pytest
from typer.testing import CliRunner

from router.cli import app
from router.cliente import ErroExecucao
from router.registro import Registro
from router.servico import processar

JSON_BAIXO = '{"complexidade":"baixa","tipo_tarefa":"resumo","risco_erro":"baixo","contexto_longo":false}'


class FakeClient:
    """Responde JSON ao classificador (system presente) e texto ao modelo final."""
    def __init__(self):
        self.messages = self
        self.modelos = []

    def create(self, **kw):
        self.modelos.append(kw["model"])
        texto = JSON_BAIXO if "system" in kw else "resposta final"
        return SimpleNamespace(content=[SimpleNamespace(type="text", text=texto)],
                               usage=SimpleNamespace(input_tokens=3, output_tokens=4))


@pytest.fixture
def reg(tmp_path):
    return Registro(tmp_path / "t.db")


def test_fluxo_completo(reg):
    fake = FakeClient()
    r = processar("resuma isto", reg, client=fake)
    assert r.decisao.modelo == "haiku" and r.resposta == "resposta final"
    assert len(fake.modelos) == 2  # classificador + execução
    assert reg.listar()[0]["tokens_out"] == 4


def test_dry_run_nao_chama_modelo_final(reg):
    fake = FakeClient()
    r = processar("resuma isto", reg, client=fake, dry_run=True)
    assert r.resposta is None and len(fake.modelos) == 1
    assert len(reg.listar()) == 1


def test_forcar_pula_classificador(reg):
    fake = FakeClient()
    r = processar("oi", reg, client=fake, forcar="opus")
    assert r.decisao.modelo == "opus" and len(fake.modelos) == 1


def test_validacoes(reg):
    with pytest.raises(ErroExecucao):
        processar("  ", reg, client=FakeClient())
    with pytest.raises(ErroExecucao):
        processar("oi", reg, client=FakeClient(), forcar="gpt")


def test_cli_sem_chave_sai_com_erro_limpo(tmp_path, monkeypatch):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    monkeypatch.setattr("router.cliente.load_dotenv", lambda: None)
    res = CliRunner().invoke(app, ["rotear", "oi", "--db", str(tmp_path / "x.db")])
    assert res.exit_code == 1 and "ANTHROPIC_API_KEY" in res.output


def test_cli_feedback_e_calibrar(tmp_path):
    db = str(tmp_path / "c.db")
    id_ = Registro(db).salvar("p", {}, "haiku", 0.9)
    runner = CliRunner()
    assert runner.invoke(app, ["feedback", str(id_), "n", "--preferido", "sonnet", "--db", db]).exit_code == 0
    out = runner.invoke(app, ["calibrar", "--db", db]).output
    assert "haiku" in out and "haiku -> sonnet" in out


def test_cli_modelo_forcar_invalido(tmp_path):
    res = CliRunner().invoke(app, ["rotear", "oi", "--forcar", "gpt", "--db", str(tmp_path / "y.db")])
    assert res.exit_code != 0
