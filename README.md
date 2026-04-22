# JudgeBench for LLM Safety

Сравнение **LLM-as-a-Judge** на одном бенчмарке: jailbreak, refusal, hallucination. Фиксируем ответы модели через mock-сервер и смотрим, как по-разному оценивают **разные judge-стеки** (Promptfoo и Python-совместимый раннер, garak-style baseline, заготовки под LLAMATOR / HiveTrace).

---

## Что сделано в этой части

- **`benchmark/`** — единый `cases.jsonl` (id, task, language, промпт, `model_output`, эталон, `gold_label`), разметка и гайд.
- **`frameworks/common/mock_target.py`** — OpenAI-compatible сервер: по префиксу `<<JUDGEBENCH_ID:…>>` отдаёт заранее записанный `model_output`, чтобы сравнивать судей, а не разные target-модели.
- **`configs/promptfoo_*.yaml`** — три режима: `llm-rubric`, `g-eval`, `model-graded-closedqa`; судья через OpenAI-compatible API (в конфиге заданы base URL и модель).
- **`scripts/run_xai_judge_promptfoo_compat.py`** — те же три стека без установки `promptfoo`: вызовы к API, ретраи, `RUN_STACKS`, лимиты `MAX_CASES` / `JUDGE_MAX_OUTPUT_TOKENS`.
- **`scripts/run_promptfoo_eval.sh`** — при наличии `promptfoo`/`npx` запускает официальный CLI, иначе вызывает Python-раннер.
- **`frameworks/garak/run_garak.py`** — локальный rule-based baseline в духе detector.
- **`frameworks/llamator/run_llamator.py`** — обвязка под LLAMATOR с загрузкой `.env` и общими переменными судьи.
- **`scripts/normalize_results.py`**, **`score_metrics.py`**, **`plot_results.py`** — сводка предсказаний в одну таблицу, метрики по `(framework, task)`, графики в `results/plots/`.
- **`Makefile`** — `run-mock`, `garak`, `normalize`, `score`, `plots`, `all`.

---

## Структура каталогов

```
benchmark/           # кейсы и разметка
configs/             # Promptfoo, HiveTrace (заготовка)
frameworks/
  common/mock_target.py
  llamator/run_llamator.py
  garak/run_garak.py
  hivetrace/run_hivetrace.sh
outputs/             # сырые JSON/CSV прогонов
results/
  normalized_results.csv
  summary.csv
  plots/               # PNG после plot_results
scripts/
  run_xai_judge_promptfoo_compat.py
  run_promptfoo_eval.sh
  normalize_results.py
  score_metrics.py
  plot_results.py
```

---

## Установка и запуск

```bash
cd judgebench_archive
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env        # заполнить ключи судьи
```

Переменные — в **`.env.example`** (в т.ч. `LLM_JUDGE_*`, опционально `MAX_CASES`, `RUN_STACKS`, `JUDGE_REQUEST_SLEEP_MS`). Для официального Promptfoo параллельно поднимается mock:

```bash
uvicorn frameworks.common.mock_target:app --host 0.0.0.0 --port 8000
```

Конвейер после прогонов в `outputs/`:

```bash
python scripts/normalize_results.py
python scripts/score_metrics.py
python scripts/plot_results.py
```

Эквивалент: `make garak && make normalize && make score && make plots` (без внешних судейских вызовов для garak).

Официальный Promptfoo (если установлен Node и CLI):

```bash
bash scripts/run_promptfoo_eval.sh
```

---

## Метрики и метки

- **`gold_label` = 1** — эталонный «провал» (unsafe / ложный отказ / противоречие эталону).
- **`pred_label` = 1** — судья отнёс кейс к тому же классу риска.

Агрегаты: `results/summary.csv` (precision, recall, F1, balanced accuracy, Cohen’s kappa по паре framework × task).

---

## Документация инструментов

- [Promptfoo — model-graded](https://www.promptfoo.dev/docs/configuration/expected-outputs/model-graded/)  
- [LLAMATOR](https://llamator-core.github.io/llamator/)  
- [garak](https://reference.garak.ai/)  
- [HiveTrace Red](https://github.com/HiveTrace/HiveTraceRed)  

Дополнительно: `examples/official_usage_notes.md`.
