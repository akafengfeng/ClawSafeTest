"""
Tests for the OpenClaw integration.
"""

from clawsafe.integrations.openclaw import get_skill_manifest, install


def test_get_skill_manifest_contains_required_fields():
    manifest = get_skill_manifest()
    assert "prompt_injection" in manifest
    assert "input_guard" in manifest
    assert "output_guard" in manifest
    assert "pip install clawsafe" in manifest
    assert "0.1.0" in manifest


def test_install_writes_skill_md(tmp_path):
    dest = install(openclaw_home=str(tmp_path))
    assert dest.exists()
    assert dest.name == "SKILL.md"
    assert dest.parent.name == "clawsafe"


def test_install_content_is_valid(tmp_path):
    dest = install(openclaw_home=str(tmp_path))
    content = dest.read_text()
    assert "ClawSafe" in content
    assert "Apache" in content


def test_install_creates_parent_dirs(tmp_path):
    deep = tmp_path / "does" / "not" / "exist"
    install(openclaw_home=str(deep))
    assert (deep / "workspace" / "skills" / "clawsafe" / "SKILL.md").exists()


def test_install_is_idempotent(tmp_path):
    install(openclaw_home=str(tmp_path))
    install(openclaw_home=str(tmp_path))  # second call must not raise
    files = list((tmp_path / "workspace" / "skills" / "clawsafe").iterdir())
    assert len(files) == 1
