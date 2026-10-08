from types import SimpleNamespace

import pytest

from router.classificador_jev import classificar, classificar_detalhado
from router.cliente import ErroExecucao
from router.registro import Registro
from router.servico import processar


def ans(choice, conf):
    return SimpleNamespace(choice=choice, confidence=conf)


class FakeJev:
    def __init__(self, resp=None, erro=None):
        self.resp, self.erro = resp, erro

    def system_one(self, state, questions):
        if self.erro:
            raise self.erro
        return self.resp


def resposta(comp="baixa", tipo="resumo", risco="baixo", longo=0.1, conf=0.9):
    return SimpleNamespace(
        choices={"complexidade": ans(comp, conf), "tipo_tarefa": ans(tipo, 0.95),
                 "risco_erro": ans(risco, 0.8)},
        nouls={"contexto_longo": SimpleNamespace(noul=longo)},
    )


def test_mapeia_respostas():
    c, conf = classificar_detalhado("x", FakeJev(resposta("alta", "codigo", "alto", 0.9)))
    assert (c.complexidade, c.tipo_tarefa, c.risco_erro, c.contexto_longo) == ("alta", "codigo", "alto", True)
    assert conf == 0.8  # mínimo entre as 3 Choice


def test_classificar_simples():
    assert classificar("x", FakeJev(resposta())).tipo_tarefa == "resumo"


def test_resposta_incompleta_vira_erro():
    with pytest.raises(ErroExecucao):
        classificar("x", FakeJev(SimpleNamespace(choices={}, nouls={})))


def test_sem_chave(monkeypatch):
    monkeypatch.delenv("TYPESAFE_API_KEY", raising=False)
    monkeypatch.setattr("router.classificador_jev.load_dotenv", lambda: None)
    with pytest.raises(ErroExecucao, match="TYPESAFE_API_KEY"):
        classificar("x")


def test_servico_com_jev_reduz_confianca(tmp_path):
    reg = Registro(tmp_path / "j.db")
    r = processar("x", reg, dry_run=True, classificador="jev",
                  jev_client=FakeJev(resposta(conf=0.6)))
    assert r.decisao.modelo == "haiku" and r.decisao.confianca == 0.6


def test_classificador_invalido(tmp_path):
    with pytest.raises(ErroExecucao):
        processar("x", Registro(tmp_path / "k.db"), classificador="gpt")
