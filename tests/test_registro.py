import pytest

from router.registro import Registro


@pytest.fixture
def reg(tmp_path):
    return Registro(tmp_path / "t.db")


def test_salvar_e_listar(reg):
    id_ = reg.salvar("p", {"a": 1}, "haiku", 0.9, "r", 1, 2)
    linha = reg.listar()[0]
    assert linha["id"] == id_ and linha["modelo_escolhido"] == "haiku"


def test_feedback_e_taxa(reg):
    a = reg.salvar("p1", {}, "haiku", 0.9)
    b = reg.salvar("p2", {}, "haiku", 0.9)
    reg.registrar_feedback(a, True)
    reg.registrar_feedback(b, False, "sonnet")
    assert reg.taxa_acerto()["haiku"] == {"total": 2, "acertos": 1, "taxa": 0.5}


def test_feedback_id_inexistente(reg):
    with pytest.raises(KeyError):
        reg.registrar_feedback(999, True)


def test_prompt_com_aspas_nao_quebra_sql(reg):
    reg.salvar("x'); DROP TABLE execucoes;--", {}, "opus", 0.5)
    assert len(reg.listar()) == 1
