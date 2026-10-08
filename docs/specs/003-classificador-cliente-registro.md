# Spec 003 — Classificador, cliente Anthropic e registro

## Classificador (`classificador.py`)
- `classificar(prompt, client=None) -> Caracteristicas`
- Usa o modelo `MODELO_CLASSIFICADOR` pedindo **somente JSON** com os 4 campos.
- Valida com `Caracteristicas`; se inválido/não-JSON, retry 1x; persistindo a falha, fallback conservador: `media / analise / medio / False` (cai em Sonnet).
- Aceita exemplos few-shot (`exemplos`) para a calibração futura.

## Cliente (`cliente.py`)
- `executar(prompt, modelo, client=None, max_tokens=1024, timeout=60) -> Resposta(texto, tokens_in, tokens_out, latencia_s)`
- `get_client()` lê `ANTHROPIC_API_KEY` (via `.env`); sem chave → `ErroExecucao` com mensagem clara.
- Erros da SDK são convertidos em `ErroExecucao`.

## Registro (`registro.py`)
- SQLite, tabela `execucoes`: id, data, prompt, caracteristicas(JSON), modelo_escolhido, confianca, resposta, tokens_in, tokens_out, feedback('acertou'|'errou'|NULL), modelo_preferido.
- `salvar`, `registrar_feedback`, `listar`, `taxa_acerto` (por modelo).
- Queries parametrizadas (sem concatenação de SQL).

## Aceite
- Tudo testável com clientes falsos (sem rede, sem chave).
