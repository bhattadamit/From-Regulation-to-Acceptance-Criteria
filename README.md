# Replication package
Prepared for submission to *Information and Software Technology* (Elsevier). Cite as: [Author(s)], Replication package for "From Regulation to Acceptance Criteria", [repository], 2026, [DOI].

From Regulation to Acceptance Criteria: How Complete Are LLM-Generated Specifications for US Payments Rules?

## Folder structure
| Folder | Contents |
|---|---|
| `data/prompts/` | The six prompts (C1 title-only, C2 text-grounded) for 12 CFR 1005.11, 1005.6 and 229.10 |
| `data/raw_outputs/` | 72 verbatim model outputs (3 models x 2 conditions x 3 provisions x 4 runs) |
| `data/run_log.xlsx` | Run log: model, version label, date, run, condition, rule, file |
| `data/coding/` | Second coder's original workbook (Coder B), Coder B codes, reconciliation table with reasons, agreed codes |
| `code/` | Obligation inventory, frozen scoring signatures, analysis, reliability and figure scripts |
| `results/` | All computed outputs (obligation-level scores, metrics, tests, validation, reliability) |
| `figures/` | Figures 1-4 as PDF (vector) and 600 dpi PNG. 600 dpi TIFF versions are inside `Replication_Package_IST.zip` (too large for browsing on GitHub) |
| `model_evidence/` | Screenshots identifying the models: Gemini 4 Hydrogen selected in the Gemini model picker; GPT-6 identified in-session in ChatGPT. Run dates and labels are in `data/run_log.xlsx`. |
| `tables/` | Tables 1-15 exactly as in the manuscript: `All_Tables.xlsx` (one sheet per table) and one CSV per table |

## Reproducing the results
Requires Python 3.10+ with pandas, numpy, scipy, matplotlib and openpyxl. Run from this folder:
```
python code/run_scoring.py      # 4,032 obligation scores from the 72 outputs
python code/analysis2.py        # metrics, tests, robustness -> results/summary2.json
python code/sens_v21.py         # notation-tolerant sensitivity analysis
python code/reliability.py      # inter-coder agreement (Coder A vs Coder B, before reconciliation)
python code/figs2.py            # Figures 1-4
```
`code/scoring.py` is the frozen scorer; its SHA-256 hash is recorded in `results/scoring_sha256.txt`.
`code/inventory_original.py` holds the first coder's codes before reconciliation; `code/inventory.py` applies the agreed codes in `data/coding/reconciled_codes.csv`.

## Notes
- Manual validation sample (36 obligation-output pairs, automated label vs author's manual label): `results/validation_sample_adjudicated.csv`.
- Coder B is identified only by role in the manuscript.
- Regulatory text: eCFR, current text as accessed on 19-20 November 2026.

## Licence and deposit
Suggested: deposit on Zenodo or Mendeley Data to obtain a DOI, and quote it in the manuscript's Data availability statement. Suggested licences: CC BY 4.0 for data and tables, MIT for code. Regulatory text is a US government work; model outputs are included verbatim for research reproducibility.

## Models tested (20 November 2026)
| Model | Vendor | Interface | Label in run log / file names |
|---|---|---|---|
| GPT-6 | OpenAI | ChatGPT web app, Temporary Chat (unpersonalized) | `CHGPT_Chatgpt 6` |
| Claude Sonnet 5.5 | Anthropic | Claude web app, incognito chat | `Claude_Sonnet 5.5` |
| Gemini 4 Hydrogen | Google | Gemini web app, "Hydrogen" selected in model picker | `Google_Hydrogen` |

## Licence
Code is released under the MIT License (see LICENSE). Data, tables and figures are released under CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/).
