# Official Usage Notes for Repositories

Ниже собраны **реальные паттерны использования** репозиториев, на которые опирается проект.

## 1. Promptfoo

Что берем из официальной документации:
- `llm-rubric` как generic LLM-as-a-judge
- `g-eval` как structured evaluation mode
- `model-graded-closedqa` как reference-like judging

Пример запуска:
```bash
promptfoo eval -c configs/promptfoo_llm_rubric.yaml --output outputs/promptfoo/llm_rubric.json
promptfoo eval -c configs/promptfoo_geval.yaml --output outputs/promptfoo/geval.json
promptfoo eval -c configs/promptfoo_closedqa.yaml --output outputs/promptfoo/closedqa.json
```

Docs:
- https://www.promptfoo.dev/docs/configuration/expected-outputs/model-graded/
- https://www.promptfoo.dev/docs/configuration/expected-outputs/model-graded/llm-rubric/
- https://www.promptfoo.dev/docs/configuration/expected-outputs/model-graded/model-graded-closedqa/

## 2. LLAMATOR

Что берем из официальной документации:
- `ClientOpenAI` для OpenAI-compatible API
- `judge_model` как отдельная judge-модель
- `start_testing(...)` как единая точка входа
- `get_test_preset(...)` для выбора готовых attack suites

Пример паттерна:
```python
import llamator

client = llamator.ClientOpenAI(
    api_key="dummy",
    base_url="http://localhost:8000/v1",
    model="mock-judge-target",
)

judge = llamator.ClientOpenAI(
    api_key="dummy",
    base_url="http://localhost:1234/v1",
    model="qwen2.5-7b-instruct",
)

result = llamator.start_testing(
    attack_model=client,
    tested_model=client,
    judge_model=judge,
    config={"enable_logging": True, "enable_reports": True, "artifacts_path": "./outputs/llamator"},
    basic_tests=[("harmbench", {"num_attempts": 1})],
)
```

Docs:
- https://llamator-core.github.io/llamator/
- https://llamator-core.github.io/llamator/howtos.html
- https://llamator-core.github.io/llamator/code_documentation.html

## 3. HiveTrace Red

Что берем из GitHub:
- framework для систематического red teaming
- 80+ attacks across multiple categories
- WildGuard evaluators
- multilang support

Пример идеи запуска:
```bash
hivetracered --config configs/hivetrace.yaml
```

Repo:
- https://github.com/HiveTrace/HiveTraceRed

## 4. garak

Что берем из официальной документации:
- garak = LLM vulnerability scanner
- probes -> detectors -> evaluators
- detector quality metrics

В проекте мы используем detector-style baseline, чтобы честно противопоставить rules/detectors против semantic judges.

Docs:
- https://reference.garak.ai/en/latest/
- https://docs.garak.ai/
- https://reference.garak.ai/en/stable/evaluators.html

## 5. Почему здесь есть mock target

Чтобы все фреймворки оценивали **один и тот же output**, проект использует `frameworks/common/mock_target.py`.
Он возвращает заранее зафиксированный `model_output` по `user_prompt`. Благодаря этому вы сравниваете judge-логику, а не качество разных target-моделей.

