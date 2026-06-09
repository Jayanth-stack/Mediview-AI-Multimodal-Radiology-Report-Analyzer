from __future__ import annotations

import ast
import subprocess
import sys
import unittest
from pathlib import Path


BACKEND_DIR = Path(__file__).resolve().parents[1]
MIGRATIONS_DIR = BACKEND_DIR / "alembic" / "versions"


def _string_assignment(module_path: Path, name: str) -> str:
    tree = ast.parse(module_path.read_text())
    for node in tree.body:
        if isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
            if node.target.id == name and isinstance(node.value, ast.Constant):
                return str(node.value.value)
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == name and isinstance(node.value, ast.Constant):
                    return str(node.value.value)
    raise AssertionError(f"{name} assignment not found in {module_path.name}")


class CriticalMigrationTests(unittest.TestCase):
    def test_documents_migration_revises_user_model_revision(self):
        user_model_revision = _string_assignment(
            MIGRATIONS_DIR / "2a5f7141d494_add_user_model.py",
            "revision",
        )
        documents_down_revision = _string_assignment(
            MIGRATIONS_DIR / "0004_add_documents_table.py",
            "down_revision",
        )

        self.assertEqual(documents_down_revision, user_model_revision)

    def test_alembic_has_single_head(self):
        result = subprocess.run(
            [sys.executable, "-m", "alembic", "heads"],
            cwd=BACKEND_DIR,
            check=True,
            capture_output=True,
            text=True,
        )

        heads = [line for line in result.stdout.splitlines() if "(head)" in line]
        self.assertEqual(heads, ["0004_add_documents_table (head)"])


if __name__ == "__main__":
    unittest.main()
