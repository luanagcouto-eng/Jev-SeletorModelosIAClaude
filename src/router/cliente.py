"""Envio do prompt ao modelo escolhido via API Anthropic."""

import os
import time
from dataclasses import dataclass

import anthropic
from dotenv import load_dotenv

from router.catalogo import CATALOGO


class ErroExecucao(Exception):
    """Falha ao chamar a API (chave ausente, rede, limite, etc.)."""


@dataclass(frozen=True)
class Resposta:
    texto: str
    tokens_in: int
    tokens_out: int
    latencia_s: float


def get_client() -> anthropic.Anthropic:
    load_dotenv()
    if not os.getenv("ANTHROPIC_API_KEY"):
        raise ErroExecucao("ANTHROPIC_API_KEY não definida. Crie o .env a partir do .env.example.")
    return anthropic.Anthropic()


def executar(prompt: str, modelo: str, client=None, max_tokens: int = 1024,
             timeout: float = 60.0) -> Resposta:
    if modelo not in CATALOGO:
        raise ErroExecucao(f"Modelo desconhecido: {modelo!r}")
    client = client or get_client()
    inicio = time.perf_counter()
    try:
        resp = client.messages.create(
            model=CATALOGO[modelo].id_api,
            max_tokens=max_tokens,
            timeout=timeout,
            messages=[{"role": "user", "content": prompt}],
        )
    except anthropic.APIError as e:
        raise ErroExecucao(f"Erro da API: {e}") from e
    texto = "".join(b.text for b in resp.content if getattr(b, "type", "text") == "text")
    return Resposta(texto, resp.usage.input_tokens, resp.usage.output_tokens,
                    time.perf_counter() - inicio)
