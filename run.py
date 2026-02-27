import argparse
import pandas as pd
import numpy as np
import yaml
import json
import logging
import os
import sys
import time


def setup_logger(log_file):
    logging.basicConfig(
        filename=log_file,
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s"
    )


def write_error(output_path, version, message):
    error_output = {
        "version": version,
        "status": "error",
        "error_message": message
    }

    with open(output_path, "w") as f:
        json.dump(error_output, f, indent=4)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--config", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--log-file", required=True)

    args = parser.parse_args()

    start_time = time.time()
    config = {}

    try:
        # ---------------------------
        # Setup Logging
        # ---------------------------
        setup_logger(args.log_file)
        logging.info("Job started")

        # ---------------------------
        # Load Configuration
        # ---------------------------
        if not os.path.exists(args.config):
            raise FileNotFoundError("Config file not found")

        with open(args.config, "r") as f:
            config = yaml.safe_load(f)

        if not all(k in config for k in ["seed", "window", "version"]):
            raise ValueError("Invalid configuration file structure")

        seed = config["seed"]
        window = config["window"]
        version = config["version"]

        np.random.seed(seed)

        logging.info(
            f"Config loaded: seed={seed}, window={window}, version={version}"
        )

        # ---------------------------
        # Load CSV (Handle fully quoted rows)
        # ---------------------------
        if not os.path.exists(args.input):
            raise FileNotFoundError("Input CSV file not found")

        with open(args.input, "r", encoding="utf-8") as f:
            lines = f.readlines()

        cleaned_lines = [line.strip().strip('"') for line in lines]

        from io import StringIO
        cleaned_data = StringIO("\n".join(cleaned_lines))

        df = pd.read_csv(cleaned_data, sep=",")

        if df.empty:
            raise ValueError("Input CSV file is empty")

        df.columns = df.columns.str.strip().str.lower()

        if "close" not in df.columns:
            raise ValueError("Missing required column: close")

        rows_processed = len(df)
        logging.info(f"Data loaded: {rows_processed} rows")
        # ---------------------------
        # Rolling Mean Calculation
        # ---------------------------
        df["rolling_mean"] = df["close"].rolling(window=window).mean()

        logging.info(f"Rolling mean calculated with window={window}")

        # ---------------------------
        # Signal Generation
        # ---------------------------
        df["signal"] = np.where(
            df["close"] > df["rolling_mean"], 1, 0
        )

        logging.info("Signals generated")

        # ---------------------------
        # Metrics Calculation
        # ---------------------------
        signal_rate = float(df["signal"].mean())
        latency_ms = int((time.time() - start_time) * 1000)

        metrics = {
            "version": version,
            "rows_processed": rows_processed,
            "metric": "signal_rate",
            "value": round(signal_rate, 4),
            "latency_ms": latency_ms,
            "seed": seed,
            "status": "success"
        }

        with open(args.output, "w") as f:
            json.dump(metrics, f, indent=4)

        logging.info(
            f"Metrics: signal_rate={signal_rate:.4f}, rows_processed={rows_processed}"
        )

        logging.info(
            f"Job completed successfully in {latency_ms}ms"
        )

        print(json.dumps(metrics, indent=4))

        sys.exit(0)

    except Exception as e:
        version = config.get("version", "unknown")

        logging.error(str(e))

        write_error(args.output, version, str(e))

        print("Error:", str(e))

        sys.exit(1)


if __name__ == "__main__":
    main()