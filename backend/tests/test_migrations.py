from __future__ import annotations

import unittest
from pathlib import Path

from alembic.config import Config
from alembic.script import ScriptDirectory


class MigrationGraphTests(unittest.TestCase):
    def test_alembic_revision_graph_has_single_resolvable_head(self):
        backend_dir = Path(__file__).resolve().parents[1]
        config = Config(str(backend_dir / "alembic.ini"))
        config.set_main_option("script_location", str(backend_dir / "alembic"))
        script = ScriptDirectory.from_config(config)

        revisions = list(script.walk_revisions())

        self.assertEqual(script.get_heads(), ["0005_repair_documents_metadata_column"])
        self.assertIn("0004_add_documents_table", {revision.revision for revision in revisions})


if __name__ == "__main__":
    unittest.main()
