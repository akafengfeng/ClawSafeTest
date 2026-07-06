"""Tests for the two-tier package structure.

The contract: `import clawsafe` loads only the lite tier (zero third-party
dependencies, no LLM SDKs, no adapters); the full tier resolves lazily on
attribute access and is fully re-exported by `clawsafe.full`.
"""

import subprocess
import sys

import clawsafe


class TestLiteTierIsLight:
    def test_plain_import_does_not_load_full_tier(self):
        """A fresh `import clawsafe` must not pull in providers, adapters,
        the legacy agent, or any LLM SDK."""
        code = (
            "import sys, clawsafe\n"
            "heavy = ['anthropic', 'openai', 'together',"
            " 'clawsafe.core.provider', 'clawsafe.experimental',"
            " 'clawsafe.integrations', 'clawsafe.full']\n"
            "loaded = [m for m in heavy if m in sys.modules]\n"
            "assert not loaded, f'full tier loaded eagerly: {loaded}'\n"
            "print('lite import clean')\n"
        )
        result = subprocess.run(
            [sys.executable, "-c", code], capture_output=True, text=True
        )
        assert result.returncode == 0, result.stdout + result.stderr

    def test_lite_names_available_eagerly(self):
        code = (
            "import clawsafe\n"
            "for name in ('guarded', 'protect_agent', 'scan_messages',"
            " 'scan_output', 'configure'):\n"
            "    assert name in vars(clawsafe), name\n"
            "print('ok')\n"
        )
        result = subprocess.run(
            [sys.executable, "-c", code], capture_output=True, text=True
        )
        assert result.returncode == 0, result.stdout + result.stderr


class TestLazyFullTier:
    def test_lazy_attribute_resolves(self):
        assert clawsafe.AgentGuard.__name__ == "AgentGuard"
        assert clawsafe.OpenClawAdapter.__name__ == "OpenClawAdapter"
        assert clawsafe.MemoryGuard.__name__ == "MemoryGuard"

    def test_lazy_attribute_is_cached(self):
        first = clawsafe.ToolRegistry
        assert "ToolRegistry" in vars(clawsafe)
        assert clawsafe.ToolRegistry is first

    def test_unknown_attribute_raises(self):
        try:
            clawsafe.NoSuchThing
        except AttributeError as e:
            assert "NoSuchThing" in str(e)
        else:
            raise AssertionError("expected AttributeError")

    def test_dir_lists_both_tiers(self):
        names = dir(clawsafe)
        assert "guarded" in names
        assert "AgentGuard" in names
        assert "full" in names

    def test_all_exports_resolve(self):
        for name in clawsafe.__all__:
            assert getattr(clawsafe, name) is not None, name


class TestFullNamespace:
    def test_full_module_exports_everything(self):
        from clawsafe import full

        for name in full.__all__:
            assert getattr(full, name) is not None, name

    def test_full_includes_presets_and_memory_internals(self):
        from clawsafe import full

        assert full.secure_openclaw_adapter
        assert full.secure_hermes_adapter
        assert full.MemoryLearningLoop
        assert full.DEFAULT_DENYLIST

    def test_same_objects_in_both_paths(self):
        from clawsafe import full

        assert full.AgentGuard is clawsafe.AgentGuard
        assert full.ToolRegistry is clawsafe.ToolRegistry
