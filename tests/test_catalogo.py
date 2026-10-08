from router.catalogo import CATALOGO, MODELO_CLASSIFICADOR


def test_catalogo_tem_tres_modelos():
    assert set(CATALOGO) == {"haiku", "sonnet", "opus"}


def test_valores_dentro_da_escala():
    for m in CATALOGO.values():
        assert 1 <= m.custo_relativo <= 3
        assert 1 <= m.latencia_relativa <= 3
        assert 1 <= m.capacidade <= 3
        assert m.id_api


def test_classificador_existe_no_catalogo():
    assert MODELO_CLASSIFICADOR in CATALOGO
