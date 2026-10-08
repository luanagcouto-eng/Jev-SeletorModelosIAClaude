"""CLI fina sobre o serviço (typer)."""

from typing import Optional

import typer

from router.catalogo import CATALOGO
from router.cliente import ErroExecucao
from router.registro import Registro
from router.servico import processar

app = typer.Typer(help="Indica (e executa) o modelo Claude ideal para cada prompt.",
                  no_args_is_help=True)

LIMIAR_ERRO, MIN_AMOSTRAS = 0.30, 10


def _modelo_valido(valor: Optional[str]) -> Optional[str]:
    if valor is not None and valor not in CATALOGO:
        raise typer.BadParameter(f"Use um de {sorted(CATALOGO)}")
    return valor


def _falha(msg: str) -> None:
    typer.secho(f"Erro: {msg}", fg=typer.colors.RED, err=True)
    raise typer.Exit(1)


@app.command()
def rotear(
    prompt: str = typer.Argument(..., help="Prompt a ser roteado"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Só mostra a decisão, sem chamar o modelo"),
    forcar: Optional[str] = typer.Option(None, "--forcar", callback=_modelo_valido,
                                         help="haiku|sonnet|opus"),
    classificador: str = typer.Option("haiku", "--classificador", help="haiku|jev"),
    db: str = typer.Option("router.db", "--db", help="Arquivo SQLite"),
) -> None:
    registro = Registro(db)
    try:
        r = processar(prompt, registro, dry_run=dry_run, forcar=forcar,
                      classificador=classificador)
    except ErroExecucao as e:
        _falha(str(e))
    d = r.decisao
    typer.secho(f"Modelo: {CATALOGO[d.modelo].nome} (confiança {d.confianca:.0%})", bold=True)
    typer.echo(f"Motivo: {d.motivo}")
    if r.resposta is not None:
        typer.echo(f"\n{r.resposta}\n")
        typer.echo(f"Tokens: {r.tokens_in} in / {r.tokens_out} out")
    if dry_run:
        return
    if typer.confirm("Acertou?", default=True):
        registro.registrar_feedback(r.id, True)
    else:
        pref = typer.prompt("Qual modelo seria o ideal?", default=d.modelo)
        registro.registrar_feedback(r.id, False, pref if pref in CATALOGO else None)


@app.command()
def historico(limite: int = 10, db: str = "router.db") -> None:
    for e in Registro(db).listar(limite):
        fb = e["feedback"] or "-"
        typer.echo(f"#{e['id']} {e['data'][:16]} {e['modelo_escolhido']:<6} {fb:<8} {e['prompt'][:60]!r}")


@app.command()
def feedback(id: int, acertou: str = typer.Argument(..., help="s ou n"),
             preferido: Optional[str] = typer.Option(None, callback=_modelo_valido),
             db: str = "router.db") -> None:
    if acertou.lower() not in ("s", "n"):
        _falha("Use 's' ou 'n'.")
    try:
        Registro(db).registrar_feedback(id, acertou.lower() == "s", preferido)
    except KeyError as e:
        _falha(str(e))
    typer.echo("Feedback registrado.")


@app.command()
def calibrar(db: str = "router.db") -> None:
    registro = Registro(db)
    taxas = registro.taxa_acerto()
    if not taxas:
        typer.echo("Ainda sem feedback registrado.")
        return
    for modelo, t in sorted(taxas.items()):
        typer.echo(f"{modelo:<7} {t['acertos']}/{t['total']} acertos ({t['taxa']:.0%})")
        if t["total"] >= MIN_AMOSTRAS and 1 - t["taxa"] > LIMIAR_ERRO:
            typer.secho(f"  ! {modelo} erra mais de {LIMIAR_ERRO:.0%}: revise as REGRAS em roteador.py",
                        fg=typer.colors.YELLOW)
    erros = [e for e in registro.listar(200) if e["feedback"] == "errou"][:5]
    if erros:
        typer.echo("\nErros recentes (escolhido -> preferido):")
        for e in erros:
            typer.echo(f"  {e['modelo_escolhido']} -> {e['modelo_preferido'] or '?'}  {e['prompt'][:50]!r}")
