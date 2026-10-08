"""Persistência das execuções e feedback em SQLite."""

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

SCHEMA = """
CREATE TABLE IF NOT EXISTS execucoes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    data TEXT NOT NULL,
    prompt TEXT NOT NULL,
    caracteristicas TEXT NOT NULL,
    modelo_escolhido TEXT NOT NULL,
    confianca REAL NOT NULL,
    resposta TEXT,
    tokens_in INTEGER,
    tokens_out INTEGER,
    feedback TEXT CHECK (feedback IN ('acertou','errou')),
    modelo_preferido TEXT
)
"""


class Registro:
    def __init__(self, caminho: str | Path = "router.db") -> None:
        self.caminho = str(caminho)
        with self._conn() as c:
            c.execute(SCHEMA)

    def _conn(self) -> sqlite3.Connection:
        c = sqlite3.connect(self.caminho)
        c.row_factory = sqlite3.Row
        return c

    def salvar(self, prompt: str, caracteristicas: dict, modelo: str, confianca: float,
               resposta: str | None = None, tokens_in: int | None = None,
               tokens_out: int | None = None) -> int:
        with self._conn() as c:
            cur = c.execute(
                "INSERT INTO execucoes (data, prompt, caracteristicas, modelo_escolhido, "
                "confianca, resposta, tokens_in, tokens_out) VALUES (?,?,?,?,?,?,?,?)",
                (datetime.now(timezone.utc).isoformat(), prompt,
                 json.dumps(caracteristicas, ensure_ascii=False), modelo, confianca,
                 resposta, tokens_in, tokens_out),
            )
            return cur.lastrowid

    def registrar_feedback(self, id_: int, acertou: bool,
                           modelo_preferido: str | None = None) -> None:
        with self._conn() as c:
            cur = c.execute(
                "UPDATE execucoes SET feedback=?, modelo_preferido=? WHERE id=?",
                ("acertou" if acertou else "errou", modelo_preferido, id_),
            )
            if cur.rowcount == 0:
                raise KeyError(f"Execução {id_} não encontrada")

    def listar(self, limite: int = 20) -> list[dict]:
        with self._conn() as c:
            rows = c.execute("SELECT * FROM execucoes ORDER BY id DESC LIMIT ?", (limite,))
            return [dict(r) for r in rows]

    def taxa_acerto(self) -> dict[str, dict]:
        """Por modelo: total com feedback, acertos e taxa."""
        with self._conn() as c:
            rows = c.execute(
                "SELECT modelo_escolhido m, COUNT(*) n, "
                "SUM(feedback='acertou') a FROM execucoes "
                "WHERE feedback IS NOT NULL GROUP BY modelo_escolhido"
            )
            return {r["m"]: {"total": r["n"], "acertos": r["a"], "taxa": r["a"] / r["n"]}
                    for r in rows}
