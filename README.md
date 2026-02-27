# MLOps Engineering Internship – Task 0

## Overview

This project implements a deterministic, config-driven, Dockerized batch pipeline that processes cryptocurrency OHLCV data and computes a rolling-mean-based trading signal metric.

The solution demonstrates core MLOps principles:

- Reproducibility via configuration-driven execution
- Structured JSON metrics output
- Comprehensive logging and observability
- Robust error handling
- Containerized deployment using Docker

---

## Architecture

The pipeline follows this execution flow:

1. Load configuration (`config.yaml`)
2. Ingest dataset (`data.csv`)
3. Validate schema and inputs
4. Compute rolling mean on `close` column
5. Generate binary trading signal
6. Compute metrics (`signal_rate`)
7. Emit structured JSON output
8. Log full execution lifecycle

---

## Configuration

`config.yaml`

```yaml
seed: 42
window: 5
version: "v1"
```

- `seed` → ensures deterministic behavior
- `window` → rolling mean window size
- `version` → embedded into metrics output

---

## Local Setup

### Create Virtual Environment (Optional)

```bash
python -m venv venv
venv\Scripts\activate   # Windows
```

### Install Dependencies

```bash
python -m pip install -r requirements.txt
```

---

## Run Locally

```bash
python run.py \
  --input data.csv \
  --config config.yaml \
  --output metrics.json \
  --log-file run.log
```

---

## Docker Deployment (Mandatory Requirement)

### Build Image

```bash
docker build -t mlops-task .
```

### Run Container

```bash
docker run --rm mlops-task
```

The container:

- Includes `data.csv` and `config.yaml`
- Generates `metrics.json`
- Generates `run.log`
- Prints final metrics to stdout
- Exits with code 0 on success

---

## Example Output (`metrics.json`)

```json
{
  "version": "v1",
  "rows_processed": 10000,
  "metric": "signal_rate",
  "value": 0.4989,
  "latency_ms": 38,
  "seed": 42,
  "status": "success"
}
```

---

## Error Handling

The pipeline gracefully handles:

- Missing input file
- Invalid CSV format
- Empty dataset
- Missing required columns
- Invalid configuration structure

On failure, a structured error JSON is produced:

```json
{
  "version": "v1",
  "status": "error",
  "error_message": "Description of error"
}
```

---

## Logging

Execution lifecycle events are logged:

- Job start
- Configuration validation
- Data ingestion
- Rolling mean calculation
- Signal generation
- Metrics summary
- Job completion
- Error events (if any)

Logs are written to `run.log`.

---

## Dependencies

- pandas
- numpy
- pyyaml

---

## Key Design Decisions

- Config-driven reproducibility
- CLI-based execution (no hardcoded paths)
- Deterministic computation via seeded configuration
- Robust CSV parsing (handles quoted rows)
- Structured metrics output for observability
- Dockerized execution for deployment parity

---

## Reproducibility

Running the pipeline multiple times with the same configuration produces identical `signal_rate` values.

---

## Author

Shreya Singh
