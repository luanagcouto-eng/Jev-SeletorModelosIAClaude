"""Roteador por regras: Caracteristicas -> Decisao. Função pura (ver docs/specs/002-roteador.md)."""

from collections.abc import Callable
from dataclasses import dataclass

from router.catalogo import CATALOGO

COMPLEXIDADES = ("baixa", "media", "alta")
TIPOS_TAREFA = ("codigo", "analise", "escrita", "resumo", "extracao", "agentic")
RISCOS = ("baixo", "medio", "alto")


@dataclass(frozen=True)
class Caracteristicas:
    complexidade: str
    tipo_tarefa: str
    risco_erro: str
    contexto_longo: bool = False

    def __post_init__(self) -> None:
        for campo, valor, validos in (
            ("complexidade", self.complexidade, COMPLEXIDADES),
            ("tipo_tarefa", self.tipo_tarefa, TIPOS_TAREFA),
            ("risco_erro", self.risco_erro, RISCOS),
        ):
            if valor not in validos:
                raise ValueError(f"{campo} inválido: {valor!r}. Use um de {validos}")
        if not isinstance(self.contexto_longo, bool):
            raise ValueError("contexto_longo deve ser bool")


@dataclass(frozen=True)
class Decisao:
    modelo: str
    confianca: float
    motivo: str


@dataclass(frozen=True)
class Regra:
    condicao: Callable[[Caracteristicas], bool]
    modelo: str
    confianca: float
    motivo: str


# Ordem = prioridade. Para calibrar, edite só esta tabela.
REGRAS: tuple[Regra, ...] = (
    Regra(
        lambda c: c.complexidade == "alta" or c.risco_erro == "alto",
        "opus", 0.9, "Complexidade alta ou risco de erro alto",
    ),
    Regra(
        lambda c: c.tipo_tarefa == "agentic" or c.contexto_longo,
        "sonnet", 0.8, "Tarefa agentic ou contexto longo (piso Sonnet)",
    ),
    Regra(
        lambda c: c.complexidade == "baixa" and c.risco_erro == "baixo",
        "haiku", 0.9, "Tarefa simples e de baixo risco",
    ),
)

PADRAO = Decisao("sonnet", 0.7, "Caso intermediário: melhor equilíbrio custo x qualidade")


def rotear(c: Caracteristicas) -> Decisao:
    for regra in REGRAS:
        if regra.condicao(c):
            return Decisao(regra.modelo, regra.confianca, regra.motivo)
    return PADRAO


# Falha cedo se a tabela referenciar modelo que não existe no catálogo.
assert all(r.modelo in CATALOGO for r in REGRAS) and PADRAO.modelo in CATALOGO
