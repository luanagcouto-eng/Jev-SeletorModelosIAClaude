# Spec 005 — Classificador Jev (TypeSafe)

## Objetivo
Alternativa ao classificador Haiku: 1 chamada `system_one` com 4 perguntas sobre o prompt, devolvendo `Caracteristicas` + confiança derivada das probabilidades.

## Perguntas (state = {"prompt": <texto>})
- `complexidade`: Choice (baixa|media|alta)
- `tipo_tarefa`: Choice (codigo|analise|escrita|resumo|extracao|agentic)
- `risco_erro`: Choice (baixo|medio|alto) — impacto de uma resposta errada
- `contexto_longo`: Noul — sim se `noul >= 0.5`

## Confiança
`confianca_classificacao = min(confidence das 3 Choice)`. No serviço: `Decisao.confianca = min(confianca_da_regra, confianca_classificacao)`.

## Erros
Qualquer `TypeSafeError`/resposta incompleta → `ErroExecucao` (mensagem curta). Chave: `TYPESAFE_API_KEY` no `.env`.

## Seleção
CLI: `--classificador haiku|jev` (padrão haiku) para comparar os dois com o mesmo feedback. O registro guarda qual classificador foi usado.

## Aceite
Testes com cliente falso; sem rede. Validação real exige rodar localmente (a sandbox da sessão bloqueia o domínio TypeSafe).
