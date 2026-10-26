"""
Testes automatizados para validação de prompts.
"""
import pytest
import re
import yaml
import sys
from pathlib import Path

# Adicionar src ao path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from utils import validate_prompt_structure

PROMPTS_DIR = Path(__file__).parent.parent / "prompts"
V2_PATH = PROMPTS_DIR / "bug_to_user_story_v2.yml"
V1_PATH = PROMPTS_DIR / "bug_to_user_story_v1.yml"


def load_prompts(file_path: str):
    """Carrega prompts do arquivo YAML."""
    with open(file_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


@pytest.fixture(scope="module")
def prompt():
    return load_prompts(str(V2_PATH))["bug_to_user_story_v2"]


class TestPrompts:
    def test_prompt_has_system_prompt(self, prompt):
        """Verifica se o campo 'system_prompt' existe e não está vazio."""
        assert "system_prompt" in prompt
        assert prompt["system_prompt"].strip()

    def test_prompt_has_role_definition(self, prompt):
        """Verifica se o prompt define uma persona (ex: "Você é um Product Manager")."""
        text = prompt["system_prompt"]
        assert re.search(r"Você é (um|uma) \w+", text)
        assert "Product Manager" in text

    def test_prompt_mentions_format(self, prompt):
        """Verifica se o prompt exige formato Markdown ou User Story padrão."""
        text = prompt["system_prompt"]
        assert "Como [persona]" in text and "eu quero" in text and "para que" in text
        assert "Critérios de Aceitação" in text

    def test_prompt_has_few_shot_examples(self, prompt):
        """Verifica se o prompt contém exemplos de entrada/saída (técnica Few-shot)."""
        text = prompt["system_prompt"]
        assert len(re.findall(r"^Relato:", text, re.MULTILINE)) >= 2
        assert len(re.findall(r"^Como (um|uma|o) ", text, re.MULTILINE)) >= 2

    def test_prompt_no_todos(self, prompt):
        """Garante que você não esqueceu nenhum `[TODO]` no texto."""
        text = prompt["system_prompt"] + prompt.get("user_prompt", "")
        assert "[TODO]" not in text
        assert "TODO" not in text

    def test_minimum_techniques(self, prompt):
        """Verifica (através dos metadados do yaml) se pelo menos 2 técnicas foram listadas."""
        techniques = prompt.get("techniques_applied", [])
        assert len(techniques) >= 2

    def test_structure_is_valid(self, prompt):
        """Usa o validador do projeto (campos, TODOs, técnicas)."""
        is_valid, errors = validate_prompt_structure(prompt)
        assert is_valid, errors

    def test_user_prompt_has_single_variable(self, prompt):
        """O relato entra só pelo user prompt, via {bug_report}."""
        assert "{bug_report}" in prompt["user_prompt"]
        assert "{bug_report}" not in prompt["system_prompt"]

    def test_v1_fails_quality_checks(self):
        """Garante que os testes discriminam: o v1 não tem persona de PM nem few-shot."""
        v1 = load_prompts(str(V1_PATH))["bug_to_user_story_v1"]
        assert "Product Manager" not in v1["system_prompt"]
        assert "Relato:" not in v1["system_prompt"]
        assert not validate_prompt_structure(v1)[0]

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])