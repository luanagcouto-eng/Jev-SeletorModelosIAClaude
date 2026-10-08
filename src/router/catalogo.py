"""Catálogo de modelos como dados configuráveis.

Os IDs da API ficam só aqui: quando um modelo novo sair, basta editar este arquivo.
Escalas relativas: 1 (baixo) a 3 (alto).
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class Modelo:
    nome: str
    id_api: str
    custo_relativo: int  # 1 = barato, 3 = caro
    latencia_relativa: int  # 1 = rápido, 3 = lento
    capacidade: int  # 1 = básica, 3 = máxima
    pontos_fortes: tuple[str, ...]


CATALOGO: dict[str, Modelo] = {
    "haiku": Modelo(
        nome="Haiku",
        id_api="claude-haiku-5-5",
        custo_relativo=1,
        latencia_relativa=1,
        capacidade=1,
        pontos_fortes=("classificação", "extração", "resumo curto", "alto volume"),
    ),
    "sonnet": Modelo(
        nome="Sonnet",
        id_api="claude-sonnet-5-5",
        custo_relativo=2,
        latencia_relativa=2,
        capacidade=2,
        pontos_fortes=("código", "análise", "escrita", "uso diário"),
    ),
    "opus": Modelo(
        nome="Opus",
        id_api="claude-opus-5-5",
        custo_relativo=3,
        latencia_relativa=3,
        capacidade=3,
        pontos_fortes=("raciocínio complexo", "arquitetura", "agentic", "alto risco"),
    ),
}

# Modelo usado pelo classificador (barato e rápido).
MODELO_CLASSIFICADOR = "haiku"
