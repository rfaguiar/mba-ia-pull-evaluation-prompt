"""
Script para fazer pull de prompts do LangSmith Prompt Hub.

Este script:
1. Conecta ao LangSmith usando credenciais do .env
2. Faz pull dos prompts do Hub
3. Salva localmente em prompts/bug_to_user_story_v1.yml

SIMPLIFICADO: Usa serialização nativa do LangChain para extrair prompts.
"""

import inspect
import sys
from pathlib import Path
from dotenv import load_dotenv
from langsmith import Client
from langchain_core.prompts import ChatPromptTemplate
from utils import save_yaml, check_env_vars, print_section_header

load_dotenv()

PROMPT_NAME = "leonanluppi/bug_to_user_story_v1"
OUTPUT_KEY = "bug_to_user_story_v1"
OUTPUT_PATH = Path(__file__).resolve().parent.parent / "prompts" / "bug_to_user_story_v1.yml"


def pull_prompts_from_langsmith() -> bool:
    """Faz pull do prompt v1 e salva em prompts/bug_to_user_story_v1.yml."""
    print(f"Fazendo pull de {PROMPT_NAME}...")
    try:
        client = Client()
        kwargs = {}
        # Versões novas do langsmith bloqueiam o pull de prompts públicos sem esta flag;
        # as antigas (ex.: 0.2.7 do requirements.txt) nem aceitam o parâmetro.
        if "dangerously_pull_public_prompt" in inspect.signature(client.pull_prompt).parameters:
            kwargs["dangerously_pull_public_prompt"] = True
        prompt = client.pull_prompt(PROMPT_NAME, **kwargs)
    except Exception as e:
        print(f"❌ Erro ao fazer pull do prompt: {e}")
        return False

    if not isinstance(prompt, ChatPromptTemplate):
        print(f"❌ Tipo de prompt inesperado: {type(prompt).__name__}")
        return False

    system_prompt = ""
    user_prompt = ""
    for message in prompt.messages:
        kind = type(message).__name__
        if kind == "SystemMessagePromptTemplate":
            system_prompt = message.prompt.template
        elif kind == "HumanMessagePromptTemplate":
            user_prompt = message.prompt.template

    if not system_prompt:
        print("❌ Prompt sem system message")
        return False

    data = {
        OUTPUT_KEY: {
            "description": "Prompt para converter relatos de bugs em User Stories",
            "system_prompt": system_prompt,
            "user_prompt": user_prompt,
            "version": "v1",
            "tags": ["bug-analysis", "user-story", "product-management"],
        }
    }

    if not save_yaml(data, str(OUTPUT_PATH)):
        return False

    print(f"✅ Prompt salvo em {OUTPUT_PATH}")
    return True


def main():
    """Função principal"""
    sys.stdout.reconfigure(encoding="utf-8")
    print_section_header("Pull de prompts do LangSmith Hub")
    if not check_env_vars(["LANGSMITH_API_KEY"]):
        return 1
    return 0 if pull_prompts_from_langsmith() else 1


if __name__ == "__main__":
    sys.exit(main())
