# Guia rápido — Jev Seletor de Modelos

Indica qual modelo Claude usar (Haiku, Sonnet ou Opus), envia o prompt a ele e guarda seu feedback.

## 1. Ativar (uma vez só)

**Requisito:** Python 3.11+ (`python --version`).

```powershell
# 1. Entre na pasta do projeto
cd "C:\Users\luana.couto\OneDrive - Estaleiro Mauá\Outros\Área de Trabalho\Jev-SeletorModelosIA"

# 2. Crie e ative o ambiente virtual (fora do OneDrive)
python -m venv C:\venvs\jev-router
C:\venvs\jev-router\Scripts\activate

# 3. Instale
pip install -e ".[dev]"

# 4. Crie o .env
copy .env.example .env
notepad .env
```

Preencha o `.env` (sem aspas):

```
ANTHROPIC_API_KEY=sk-ant-...     # console.anthropic.com > Settings > API Keys
TYPESAFE_API_KEY=apikey_...      # console da TypeSafe (Jev)
```

Confirme que está tudo certo:

```powershell
pytest          # esperado: 41 passed
```

> Antes do primeiro uso real, confira os `id_api` dos modelos em `src\router\catalogo.py` (docs.claude.com).

## 2. Usar (todo dia)

Abra o PowerShell, entre na pasta e ative o ambiente:

```powershell
cd "C:\Users\luana.couto\OneDrive - Estaleiro Mauá\Outros\Área de Trabalho\Jev-SeletorModelosIA"
C:\venvs\jev-router\Scripts\activate
```

| Quero... | Comando |
|---|---|
| Só ver qual modelo ele indica (sem custo com Claude) | `router rotear "seu prompt" --dry-run --classificador jev` |
| Indicar **e** executar no modelo escolhido | `router rotear "seu prompt" --classificador jev` |
| Usar o Haiku como classificador (padrão) | `router rotear "seu prompt"` |
| Forçar um modelo | `router rotear "seu prompt" --forcar opus` |
| Ver as últimas execuções | `router historico` |
| Dar feedback depois | `router feedback 3 n --preferido opus` |
| Ver taxa de acerto por modelo | `router calibrar` |

Depois de cada execução ele pergunta **"Acertou?"**: responda `s` ou `n`. Se for `n`, informe o modelo que seria o ideal. Esse feedback calibra o roteador.

## 3. Regras atuais

1. Complexidade alta **ou** risco de erro alto → **Opus**
2. Tarefa agentic **ou** contexto longo → **Sonnet** (mínimo)
3. Complexidade baixa **e** risco baixo → **Haiku**
4. Demais casos → **Sonnet**

Para ajustar, edite a tabela `REGRAS` em `src\router\roteador.py`.

## 4. Problemas comuns

| Mensagem | Causa / solução |
|---|---|
| `ANTHROPIC_API_KEY não definida` | Falta a chave no `.env` |
| `TYPESAFE_API_KEY não definida` | Falta a chave do Jev no `.env` |
| `activate` bloqueado | `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` |
| `router` não encontrado | Ambiente não ativado, ou rode `pip install -e .` de novo |
| Erro de modelo não encontrado | `id_api` errado em `catalogo.py` |

O histórico fica em `router.db` (na pasta onde você rodou o comando). Nunca versione o `.env`.
