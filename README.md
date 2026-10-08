# Jev – Seletor de Modelos Claude

Dado um prompt, indica Haiku, Sonnet ou Opus (critério: equilíbrio custo × qualidade), reenvia o prompt ao modelo escolhido e registra seu feedback (acertou/errou) para calibração.

## Uso
```bash
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
cp .env.example .env        # preencha ANTHROPIC_API_KEY e TYPESAFE_API_KEY

router rotear "Resuma este e-mail em 3 linhas" --dry-run --classificador jev   # ou haiku (padrão)
router rotear "Refatore este módulo..."
router historico
router feedback 3 n --preferido opus
router calibrar
pytest
```

## Estrutura
- `catalogo.py` – modelos (IDs da API só aqui; **confirme em docs.claude.com**)
- `classificador.py` – Haiku extrai características (JSON validado, retry, fallback)
- `roteador.py` – tabela `REGRAS` (função pura)
- `cliente.py` – chamada à API · `registro.py` – SQLite · `servico.py` – pipeline · `cli.py` – typer
- `docs/specs/` – specs (SDD)

## Próximos passos
Plugar o Jev (TypeSafe AI) no classificador e comparar com o JSON simples; usar o feedback acumulado para ajustar `REGRAS`.
