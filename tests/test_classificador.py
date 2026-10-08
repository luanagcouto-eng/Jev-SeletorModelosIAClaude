from types import SimpleNamespace

from router.classificador import FALLBACK, classificar


class FakeClient:
    def __init__(self, *textos):
        self.textos = list(textos)
        self.chamadas = 0
        self.messages = self

    def create(self, **kw):
        self.chamadas += 1
        t = self.textos.pop(0)
        return SimpleNamespace(content=[SimpleNamespace(text=t)])


OK = '{"complexidade":"baixa","tipo_tarefa":"resumo","risco_erro":"baixo","contexto_longo":false}'


def test_json_valido():
    c = classificar("resuma", FakeClient(OK))
    assert (c.complexidade, c.tipo_tarefa) == ("baixa", "resumo")


def test_json_com_texto_ao_redor():
    assert classificar("x", FakeClient(f"Claro!\n{OK}\nfim")).risco_erro == "baixo"


def test_retry_apos_resposta_invalida():
    fake = FakeClient("não sei", OK)
    assert classificar("x", fake).tipo_tarefa == "resumo"
    assert fake.chamadas == 2


def test_fallback_apos_duas_falhas():
    fake = FakeClient("lixo", '{"complexidade":"enorme"}')
    assert classificar("x", fake) == FALLBACK


def test_exemplos_entram_no_system():
    class Spy(FakeClient):
        def create(self, **kw):
            self.system = kw["system"]
            return super().create(**kw)
    spy = Spy(OK)
    classificar("x", spy, exemplos=[{"prompt": "p1", "caracteristicas": {"risco_erro": "alto"}}])
    assert "p1" in spy.system
