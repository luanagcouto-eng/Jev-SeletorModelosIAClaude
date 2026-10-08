"""Classificador baseado no Jev (TypeSafe). Ver docs/specs/005-classificador-jev.md."""

import os

from dotenv import load_dotenv
from typesafe_sdk import Choice, Noul, TypeSafeClient, TypeSafeError

from router.cliente import ErroExecucao
from router.roteador import Caracteristicas

PERGUNTAS = {
    "complexidade": Choice(
        instructions="Qual a complexidade da tarefa pedida neste prompt?",
        criteria={
            "baixa": "Tarefa direta, de um passo, resposta curta ou mecânica",
            "media": "Exige alguma análise ou vários passos, mas escopo bem definido",
            "alta": "Raciocínio profundo, muitas partes interdependentes, arquitetura ou decisões em aberto",
        },
    ),
    "tipo_tarefa": Choice(
        instructions="Qual o tipo principal de tarefa pedida?",
        criteria={
            "codigo": "Escrever, revisar, depurar ou explicar código",
            "analise": "Analisar dados, comparar opções, raciocinar sobre um problema",
            "escrita": "Redigir ou reescrever textos (e-mails, posts, documentos)",
            "resumo": "Resumir ou condensar um conteúdo existente",
            "extracao": "Extrair ou classificar informações de um texto",
            "agentic": "Executar várias ações em sequência usando ferramentas ou arquivos",
        },
    ),
    "risco_erro": Choice(
        instructions="Qual o impacto de uma resposta errada para quem pediu?",
        criteria={
            "baixo": "Erro é barato: rascunho, curiosidade, fácil de conferir",
            "medio": "Erro causa retrabalho ou decisão pior, mas é corrigível",
            "alto": "Erro causa prejuízo financeiro, de segurança, legal ou de reputação",
        },
    ),
    "contexto_longo": Noul(
        instructions="O prompt traz um volume grande de texto, código ou dados que precisa ser processado?"
    ),
}


def get_client() -> TypeSafeClient:
    load_dotenv()
    if not os.getenv("TYPESAFE_API_KEY"):
        raise ErroExecucao("TYPESAFE_API_KEY não definida. Adicione ao .env.")
    return TypeSafeClient()


def classificar_detalhado(prompt: str, client=None) -> tuple[Caracteristicas, float]:
    """Retorna (características, confiança da classificação em 0..1)."""
    client = client or get_client()
    try:
        resp = client.system_one(state={"prompt": prompt}, questions=PERGUNTAS)
        ch = resp.choices
        carac = Caracteristicas(
            complexidade=ch["complexidade"].choice,
            tipo_tarefa=ch["tipo_tarefa"].choice,
            risco_erro=ch["risco_erro"].choice,
            contexto_longo=float(resp.nouls["contexto_longo"].noul) >= 0.5,
        )
        conf = min(ch[k].confidence for k in ("complexidade", "tipo_tarefa", "risco_erro"))
    except TypeSafeError as e:
        raise ErroExecucao(f"Erro do Jev: {e}") from e
    except (KeyError, ValueError, AttributeError) as e:
        raise ErroExecucao(f"Resposta inesperada do Jev: {e}") from e
    return carac, float(conf)


def classificar(prompt: str, client=None) -> Caracteristicas:
    return classificar_detalhado(prompt, client)[0]
