import itertools

import pytest

from router.catalogo import CATALOGO
from router.roteador import (
    COMPLEXIDADES, RISCOS, TIPOS_TAREFA, Caracteristicas, rotear,
)


def car(complexidade="media", tipo="analise", risco="medio", longo=False):
    return Caracteristicas(complexidade, tipo, risco, longo)


def test_regra1_complexidade_alta_vai_para_opus():
    assert rotear(car(complexidade="alta", risco="baixo")).modelo == "opus"


def test_regra1_risco_alto_vai_para_opus():
    assert rotear(car(complexidade="baixa", risco="alto")).modelo == "opus"


def test_regra2_agentic_nunca_haiku():
    d = rotear(car(complexidade="baixa", tipo="agentic", risco="baixo"))
    assert d.modelo == "sonnet"


def test_regra2_contexto_longo_nunca_haiku():
    d = rotear(car(complexidade="baixa", tipo="resumo", risco="baixo", longo=True))
    assert d.modelo == "sonnet"


def test_regra3_simples_vai_para_haiku():
    d = rotear(car(complexidade="baixa", tipo="extracao", risco="baixo"))
    assert d.modelo == "haiku"
    assert d.confianca >= 0.9


def test_regra4_intermediario_vai_para_sonnet():
    assert rotear(car()).modelo == "sonnet"


def test_prioridade_opus_vence_agentic():
    d = rotear(car(complexidade="alta", tipo="agentic", longo=True))
    assert d.modelo == "opus"


def test_deterministico():
    c = car("baixa", "escrita", "baixo")
    assert rotear(c) == rotear(c)


@pytest.mark.parametrize(
    "campo,valor",
    [("complexidade", "enorme"), ("tipo_tarefa", "poesia"), ("risco_erro", "nenhum")],
)
def test_valor_invalido_levanta_erro(campo, valor):
    args = dict(complexidade="media", tipo_tarefa="analise", risco_erro="medio")
    args[campo] = valor
    with pytest.raises(ValueError, match=campo):
        Caracteristicas(**args)


def test_todas_combinacoes_retornam_modelo_do_catalogo():
    for comp, tipo, risco, longo in itertools.product(
        COMPLEXIDADES, TIPOS_TAREFA, RISCOS, (False, True)
    ):
        d = rotear(Caracteristicas(comp, tipo, risco, longo))
        assert d.modelo in CATALOGO
        assert 0 <= d.confianca <= 1
        assert d.motivo
