# Pull, Otimização e Avaliação de Prompts com LangChain e LangSmith

Projeto que faz o pull de um prompt de baixa qualidade (`bug_to_user_story_v1`) do LangSmith Prompt Hub, o otimiza com técnicas de Prompt Engineering (v2), publica o resultado de volta no Hub e o avalia com métricas customizadas (Helpfulness, Correctness, F1-Score, Clarity e Precision), exigindo nota mínima de 0.8 em todas.

## Técnicas Aplicadas (Fase 2)

O prompt otimizado está em [prompts/bug_to_user_story_v2.yml](prompts/bug_to_user_story_v2.yml). O v1 era uma instrução genérica de poucas linhas, sem persona, formato, exemplos ou regras.

| Técnica | Por que foi escolhida | Como foi aplicada |
|---|---|---|
| **Role Prompting** | Define o nível de linguagem e o ponto de vista esperados de uma User Story. | O sistema assume a persona de "Product Manager sênior com background técnico", com 10 anos de experiência em produtos digitais. |
| **Few-shot Learning** | É a técnica que mais aproxima a saída do formato de referência e melhora Correctness e F1. | 3 exemplos completos (simples, médio e segurança) com o relato e a User Story esperada, incluindo "Contexto Técnico" e "Contexto de Segurança". |
| **Chain of Thought (interno)** | Ajuda a identificar persona, benefício, fatos e complexidade antes de escrever. | Passo a passo de raciocínio de 5 perguntas, com a instrução de **não** escrever o raciocínio na resposta. |
| **Skeleton of Thought** | Dá previsibilidade e clareza à saída. | Estrutura fixa: "Como… eu quero… para que…", "Critérios de Aceitação" em Dado/Quando/Então/E e seções opcionais por tipo de bug. |

Complementos: regras de comportamento (usar só fatos do relato, não inventar dados, critérios testáveis) e tratamento de casos especiais (relatos vagos, complexos, com logs ou sem relação com bug). O `{bug_report}` aparece apenas no `user_prompt`.

Limitação conhecida: os few-shots não incluem um bug complexo (vários problemas independentes). Esse caso é coberto apenas pelas regras de casos especiais.

## Resultados Finais

- **Prompt publicado no Hub (público):** `rfaguiar1-teste/bug_to_user_story_v2`
- **Dataset público no LangSmith (15 exemplos):** <https://smith.langchain.com/public/2f2518b1-25e2-42c7-9e8c-78290bb84c1f/d>
- **Projeto de tracing:** `desafio-prompts-langsmith`, no LangSmith (privado; veja os screenshots).

### Métricas (v2, avaliação aprovada)

| Métrica | v1 (referência do enunciado) | v2 | Mínimo |
|---|---|---|---|
| Helpfulness | ~0.45 | **0.91** | 0.80 |
| Correctness | ~0.52 | **0.90** | 0.80 |
| F1-Score | ~0.48 | **0.90** | 0.80 |
| Clarity | ~0.50 | **0.92** | 0.80 |
| Precision | ~0.46 | **0.89** | 0.80 |
| **Média** | ~0.48 | **0.906** | 0.80 |

Os valores do v1 são os do exemplo ilustrativo do enunciado; o v1 deste projeto não foi avaliado com o modelo final (o teste `test_v1_fails_quality_checks` confirma que ele falha nas verificações de qualidade). O v2 foi aprovado já na primeira avaliação válida, sem ajustes. Como o juiz é um LLM, as notas podem variar um pouco entre execuções.

### O que mudou do v1 para o v2

| Aspecto | v1 | v2 |
|---|---|---|
| Persona | Nenhuma ("assistente") | Product Manager sênior |
| Formato de saída | Livre | Fixo (Como/Quero/Para que + Critérios Dado/Quando/Então) |
| Exemplos | Nenhum | 3 few-shots |
| Regras e edge cases | Nenhuma | Não inventar dados, preservar fatos técnicos, casos vagos/complexos |
| Contexto técnico/segurança | Ausente | Seções condicionais |

### Evidências (screenshots)

Adicione as imagens em `docs/` e mantenha os links abaixo:

- `docs/avaliacao-cli.png`: saída do `evaluate.py` com `STATUS: APROVADO` e notas ≥ 0.8
- `docs/dataset.png`: dataset com 15 exemplos
- `docs/trace-1.png`, `docs/trace-2.png`, `docs/trace-3.png`: traces detalhados de 3 exemplos

### Observações sobre o ambiente

- O `src/evaluate.py` deste repositório não cria um experimento no LangSmith nem grava feedback: ele imprime as notas no console e envia os traces ao projeto `desafio-prompts-langsmith`. Por isso as notas aparecem no console (screenshot) e não em uma aba de experimentos.
- O plano gratuito do Gemini tem cota baixa e modelos instáveis. A execução final usou `LLM_MODEL=gemini-3.1-flash-lite` e `EVAL_MODEL=gemini-3.5-flash-lite`, e levou cerca de 20 minutos por causa dos limites por minuto.

## Como Executar

### Pré-requisitos

- Python 3.10+ e git
- Conta no [LangSmith](https://smith.langchain.com/) e uma API Key
- API Key do Google (Gemini) **ou** da OpenAI
- Handle público no LangSmith Hub (necessário para o `push_prompts.py`)

### Passo a passo

```bash
# 1. Clonar
git clone https://github.com/rfaguiar/mba-ia-pull-evaluation-prompt.git
cd mba-ia-pull-evaluation-prompt

# 2. Ambiente virtual e dependências
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt

# 3. Credenciais
cp .env.example .env            # Windows: copy .env.example .env
```

Preencha o `.env`:

| Variável | Descrição |
|---|---|
| `LANGSMITH_API_KEY` | API Key do LangSmith |
| `LANGSMITH_PROJECT` | Nome do projeto (ex.: `desafio-prompts-langsmith`) |
| `USERNAME_LANGSMITH_HUB` | Seu handle público no Hub |
| `LLM_PROVIDER` | `google` ou `openai` |
| `GOOGLE_API_KEY` / `OPENAI_API_KEY` | Chave do provedor escolhido |
| `LLM_MODEL` / `EVAL_MODEL` | Modelos de geração e de avaliação |

```bash
# 4. Testes de validação do prompt (offline)
pytest tests/test_prompts.py -v

# 5. Pull do prompt v1 (gera prompts/bug_to_user_story_v1.yml)
python src/pull_prompts.py

# 6. Push do prompt v2 para o Hub (público)
python src/push_prompts.py

# 7. Avaliação (todas as métricas devem ser >= 0.8)
python src/evaluate.py
```

No Windows, use `$env:PYTHONUTF8="1"` e `python -u` para evitar problemas de codificação e de buffer na saída.

### Resultado esperado

- Testes: `9 passed`
- Pull: `prompts/bug_to_user_story_v1.yml` criado
- Push: prompt `{handle}/bug_to_user_story_v2` publicado
- Avaliação: `STATUS: APROVADO`, com todas as métricas ≥ 0.8

### Estrutura

```
.
├── datasets/bug_to_user_story.jsonl   # 15 exemplos de avaliação
├── prompts/
│   ├── bug_to_user_story_v1.yml       # prompt original (pull)
│   └── bug_to_user_story_v2.yml       # prompt otimizado
├── src/
│   ├── pull_prompts.py                # pull do Hub
│   ├── push_prompts.py                # push do v2 para o Hub
│   ├── evaluate.py                    # avaliação
│   ├── metrics.py                     # métricas
│   └── utils.py
├── tests/test_prompts.py              # testes de validação
├── docs/                              # screenshots
└── requirements.txt
```
