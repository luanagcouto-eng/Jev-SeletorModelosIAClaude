# Spec 002 — Roteador de regras

## Objetivo
Dado um conjunto de `Caracteristicas` do prompt, devolver uma `Decisao` (modelo, confiança, motivo). Função pura, sem API, sem I/O.

## Entrada — `Caracteristicas`
| Campo | Valores |
|---|---|
| complexidade | baixa \| media \| alta |
| tipo_tarefa | codigo \| analise \| escrita \| resumo \| extracao \| agentic |
| risco_erro | baixo \| medio \| alto |
| contexto_longo | bool |

Valor fora do domínio → `ValueError`.

## Saída — `Decisao`
- `modelo`: chave do `CATALOGO` (`haiku` \| `sonnet` \| `opus`)
- `confianca`: float 0..1
- `motivo`: texto curto em pt-BR

## Regras (ordem = prioridade; primeira que casar vence)
| # | Condição | Modelo | Confiança |
|---|---|---|---|
| 1 | complexidade=alta **ou** risco_erro=alto | opus | 0.9 |
| 2 | tipo_tarefa=agentic **ou** contexto_longo | sonnet | 0.8 |
| 3 | complexidade=baixa **e** risco_erro=baixo | haiku | 0.9 |
| 4 | caso contrário | sonnet | 0.7 |

Regra 2 impõe piso Sonnet: agentic e contexto longo nunca vão para Haiku (e só chegam a Opus pela regra 1).

## Critérios de aceite
- Regras vivem em uma tabela de dados (`REGRAS`), não em `if` espalhados.
- Toda saída tem `modelo` existente em `CATALOGO`.
- Função determinística: mesma entrada, mesma saída.
- Cobertura de testes: cada regra + prioridade + validação de entrada.
