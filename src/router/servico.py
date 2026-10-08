"""Orquestra o pipeline classificar -> rotear -> executar -> registrar."""

from dataclasses import asdict, dataclass

from router.catalogo import CATALOGO
from router.classificador import classificar
from router.classificador_jev import classificar_detalhado
from router.cliente import ErroExecucao, executar
from router.registro import Registro
from router.roteador import Caracteristicas, Decisao, rotear


@dataclass(frozen=True)
class Resultado:
    id: int
    decisao: Decisao
    caracteristicas: Caracteristicas | None
    resposta: str | None
    tokens_in: int | None = None
    tokens_out: int | None = None


def processar(prompt: str, registro: Registro, client=None, dry_run: bool = False,
              forcar: str | None = None, classificador: str = "haiku",
              jev_client=None) -> Resultado:
    if not prompt.strip():
        raise ErroExecucao("Prompt vazio.")
    if forcar is not None and forcar not in CATALOGO:
        raise ErroExecucao(f"Modelo inválido: {forcar!r}. Use {sorted(CATALOGO)}")

    if classificador not in ("haiku", "jev"):
        raise ErroExecucao(f"Classificador inválido: {classificador!r}. Use haiku ou jev")

    if forcar:
        carac = None
        decisao = Decisao(forcar, 1.0, "Modelo forçado pelo usuário")
    elif classificador == "jev":
        carac, conf = classificar_detalhado(prompt, client=jev_client)
        base = rotear(carac)
        decisao = Decisao(base.modelo, min(base.confianca, conf), base.motivo)
    else:
        carac = classificar(prompt, client=client)
        decisao = rotear(carac)

    resposta = None
    if not dry_run:
        resposta = executar(prompt, decisao.modelo, client=client)

    id_ = registro.salvar(
        prompt, asdict(carac) if carac else {}, decisao.modelo, decisao.confianca,
        resposta.texto if resposta else None,
        resposta.tokens_in if resposta else None,
        resposta.tokens_out if resposta else None,
    )
    return Resultado(id_, decisao, carac, resposta.texto if resposta else None,
                     resposta.tokens_in if resposta else None,
                     resposta.tokens_out if resposta else None)
