# TenderLens evaluation baseline

TenderLens includes a small, deterministic evaluation fixture under
`backend/app/evaluation.py`. It is intended to make changes to retrieval and
compliance rules measurable without requiring paid APIs or a hosted model.

Run it from `backend/`:

```powershell
.\.venv\Scripts\python.exe -m app.evaluation
```

The fixture currently measures:

- Confident retrieval accuracy using a conservative score threshold of `0.5`.
- Rule accuracy for clear evidence, amount thresholds, missing amounts and
  expired dates.

Cases below the threshold are intentionally labeled as not confidently
retrieved, even when a human may recognize a weak topical relationship. The
fixture is deliberately small and is not a substitute for a labeled
production dataset. For the course project, new anonymized tender/evidence
pairs can be added to `CASES`, with the expected retrieval and rule outcomes
recorded explicitly.
