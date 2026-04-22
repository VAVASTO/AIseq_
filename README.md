# JudgeBench for LLM Safety

Исследование: **насколько по-разному ведут себя разные judge-стеки** (Promptfoo, LLAMATOR, HiveTrace Red, garak) на **одном и том же** human-labeled бенчмарке. Сравниваем не атаки и не целевые модели в первую очередь, а **качество автоматической оценки** (jailbreak / refusal / hallucination).

---

## Что отдавать дальше (артефакты)

### Владимир → Никита / Данилу

| Артефакт | Путь | Зачем |
|----------|------|--------|
| Конфиги Promptfoo | `configs/promptfoo_*.yaml` | Воспроизводимый запуск через `promptfoo` |
| Сырые ответы судей (JSON) | `outputs/promptfoo/llm_rubric.json`, `geval.json`, `closedqa.json` | Разбор ошибок, пересчёт метрик |
| Раннер без npm | `scripts/run_xai_judge_promptfoo_compat.py` | То же три стека через OpenAI-compatible API |
| Раннер LLAMATOR | `frameworks/llamator/run_llamator.py` + `outputs/llamator/` (если есть) | Вторая половина твоей зоны |
| Mock target | `frameworks/common/mock_target.py` | Фиксированный `model_output` по кейсу |

**Никите:** передать `outputs/promptfoo/*.json` + согласованный `benchmark/cases.jsonl` (уже в репо). Он мержит с HiveTrace/garak через `scripts/normalize_results.py`.

**Данилу:** для слайдов — `results/summary.csv` + папка **`results/plots/`** (PNG).

### Денис (уже в репозитории)

- `benchmark/cases.jsonl`, `benchmark/human_labels.csv`, `benchmark/annotation_guide.md`

### Не пересылать в чатах

- Содержимое `.env` и любые API-ключи (см. `.gitignore`).

---

## Структура репозитория

```
benchmark/           # кейсы и разметка
configs/             # Promptfoo, HiveTrace (заготовки)
frameworks/
  common/mock_target.py   # replay model_output по id кейса
  llamator/run_llamator.py
  garak/run_garak.py
  hivetrace/run_hivetrace.sh
outputs/             # сырые прогоны (в git не кладём — см. .gitignore)
  promptfoo/
  garak/
results/
  normalized_results.csv  # пересборка — в git не кладём
  summary.csv             # агрегированные метрики — можно коммитить
  plots/                  # графики — можно коммитить
scripts/
  run_xai_judge_promptfoo_compat.py  # Python-аналог трёх Promptfoo-стеков
  run_promptfoo_eval.sh
  normalize_results.py
  score_metrics.py
  plot_results.py
```

---

## Быстрый старт

```bash
cd judgebench_archive
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env        # заполни ключи (не коммить .env)
```

### Переменные окружения (`.env`)

См. **`.env.example`**. Типичный вариант для OpenRouter:

- `LLM_JUDGE_API_KEY`, `LLM_JUDGE_BASE_URL`, `LLM_JUDGE_MODEL`
- опционально: `MAX_CASES`, `JUDGE_MAX_OUTPUT_TOKENS`, `JUDGE_REQUEST_SLEEP_MS`
- только часть стеков: `RUN_STACKS=geval,closedqa`
- mock для Promptfoo: поднять `uvicorn frameworks.common.mock_target:app --host 0.0.0.0 --port 8000`

### Конвейер метрик и графиков

```bash
python frameworks/garak/run_garak.py          # baseline (локально, без API)
python scripts/normalize_results.py
python scripts/score_metrics.py
python scripts/plot_results.py
```

Или через Makefile (без Promptfoo): `make garak && make normalize && make score && make plots`.

### Promptfoo (если установлены Node и `promptfoo`)

В одном терминале mock на `:8000`, затем:

```bash
bash scripts/run_promptfoo_eval.sh
```

---

## Метрики и смысл `gold_label`

- **`gold_label` = 1** — неуспех с точки зрения safety: unsafe / ложный отказ / несоответствие эталону.
- **`pred_label` = 1** — судья считает кейс «провальным» в той же логике.

Сводка по фреймворкам и задачам: `results/summary.csv` (precision, recall, F1, balanced accuracy, Cohen’s kappa).

---

## Роли (кратко)

| Участник | Зона |
|----------|------|
| Данил | презентация, narrative, защита |
| Денис | benchmark, gold labels, `annotation_guide.md` |
| Владимир | Promptfoo + LLAMATOR + raw outputs |
| Никита | HiveTrace Red + garak + нормализация + метрики + error analysis |

---

## Что не пушить в git

Список в **`.gitignore`**: `.env`, `.venv`, `outputs/`, `results/normalized_results.csv`, кэши Python, служебные папки IDE. В репозитории держим **`.env.example`** без секретов; графики и `summary.csv` можно коммитить как итог семинара.

---

## Доклад (скелет)

1. Зачем сравнивать judge, а не только модели.  
2. Дизайн бенчмарка (120 кейсов, три типа задач).  
3. Какие стеки сравнивали (Promptfoo: rubric / g-eval / closedqa; garak baseline; …).  
4. Метрики.  
5. Результаты + графики из `results/plots/`.  
6. Ошибки и ограничения.  
7. Практическая рекомендация: какой evaluator для какой задачи.

---

## Ссылки на документацию инструментов

- [Promptfoo — model-graded](https://www.promptfoo.dev/docs/configuration/expected-outputs/model-graded/)  
- [LLAMATOR](https://llamator-core.github.io/llamator/)  
- [garak](https://reference.garak.ai/)  
- [HiveTrace Red](https://github.com/HiveTrace/HiveTraceRed)  

Доп. заметки: `examples/official_usage_notes.md`.
