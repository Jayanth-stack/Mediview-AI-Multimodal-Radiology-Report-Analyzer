from __future__ import annotations

import unittest
from pathlib import Path


class MigrationGraphTests(unittest.TestCase):
    def test_alembic_graph_has_single_documents_head(self):
        from alembic.config import Config
        from alembic.script import ScriptDirectory

        backend_dir = Path(__file__).resolve().parents[1]
        config = Config(str(backend_dir / "alembic.ini"))
        config.set_main_option("script_location", str(backend_dir / "alembic"))
        script = ScriptDirectory.from_config(config)

        self.assertEqual(script.get_current_head(), "0004_add_documents_table")
        self.assertEqual(
            script.get_revision("0004_add_documents_table").down_revision,
            "2a5f7141d494",
        )


if __name__ == "__main__":
    unittest.main()
