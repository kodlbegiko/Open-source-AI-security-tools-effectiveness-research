#!/usr/bin/env bash
set -euo pipefail

: "${GITLEAKS_BIN:?GITLEAKS_BIN is required}"
: "${TRUFFLEHOG_BIN:?TRUFFLEHOG_BIN is required}"
: "${DETECT_SECRETS_BIN:?DETECT_SECRETS_BIN is required}"

mkdir -p results/raw results/normalized results/metrics evidence/evaluation reports
exec > >(tee -a evidence/evaluation/command-log.txt) 2>&1

echo "evaluation_started_utc=$(date -u +%FT%TZ)"
echo "git_sha=${GITHUB_SHA:-LOCAL}"
python --version
"$GITLEAKS_BIN" version
"$TRUFFLEHOG_BIN" --version
"$DETECT_SECRETS_BIN" --version

python benchmark/generate_benchmark.py --output generated/benchmark
python baselines/run_baselines.py --benchmark-root generated/benchmark --output-dir results/normalized

set +e
/usr/bin/time -f '{"elapsed_seconds":%e,"max_rss_kb":%M,"cpu_percent":"%P","exit_status":%x}' \
  -o results/metrics/gitleaks-batch-resource.json \
  timeout 180 "$GITLEAKS_BIN" dir generated/benchmark/cases \
    --no-banner --exit-code 0 --redact=100 --report-format json --report-path results/raw/gitleaks.json \
    > results/raw/gitleaks-stdout.txt 2> results/raw/gitleaks-stderr.txt
gitleaks_status=$?

touch results/raw/trufflehog.jsonl
/usr/bin/time -f '{"elapsed_seconds":%e,"max_rss_kb":%M,"cpu_percent":"%P","exit_status":%x}' \
  -o results/metrics/trufflehog-batch-resource.json \
  timeout 180 "$TRUFFLEHOG_BIN" filesystem generated/benchmark/cases \
    --no-verification --redact --json \
    > results/raw/trufflehog.jsonl 2> results/raw/trufflehog-stderr.txt
trufflehog_status=$?

mapfile -d '' benchmark_files < <(find generated/benchmark/cases -type f -print0 | sort -z)
/usr/bin/time -f '{"elapsed_seconds":%e,"max_rss_kb":%M,"cpu_percent":"%P","exit_status":%x}' \
  -o results/metrics/detect-secrets-batch-resource.json \
  timeout 180 "$DETECT_SECRETS_BIN" scan --all-files "${benchmark_files[@]}" \
    > results/raw/detect-secrets.json 2> results/raw/detect-secrets-stderr.txt
detect_secrets_status=$?
set -e

[[ -s results/raw/gitleaks.json ]] || echo '[]' > results/raw/gitleaks.json
[[ -s results/raw/trufflehog.jsonl ]] || : > results/raw/trufflehog.jsonl
[[ -s results/raw/detect-secrets.json ]] || echo '{"results":{}}' > results/raw/detect-secrets.json

printf '%s\n' "$gitleaks_status" > results/raw/gitleaks-exit-code.txt
printf '%s\n' "$trufflehog_status" > results/raw/trufflehog-exit-code.txt
printf '%s\n' "$detect_secrets_status" > results/raw/detect-secrets-exit-code.txt

python adapters/normalize_results.py --tool gitleaks --raw results/raw/gitleaks.json \
  --manifest generated/benchmark/manifest.jsonl --output results/normalized/gitleaks.jsonl --exit-code "$gitleaks_status"
python adapters/normalize_results.py --tool trufflehog --raw results/raw/trufflehog.jsonl \
  --manifest generated/benchmark/manifest.jsonl --output results/normalized/trufflehog.jsonl --exit-code "$trufflehog_status"
python adapters/normalize_results.py --tool detect-secrets --raw results/raw/detect-secrets.json \
  --manifest generated/benchmark/manifest.jsonl --output results/normalized/detect-secrets.jsonl --exit-code "$detect_secrets_status"

python analysis/compute_metrics.py --manifest generated/benchmark/manifest.jsonl \
  --results-dir results/normalized --output results/metrics/metrics.json
python analysis/measure_latency.py --manifest generated/benchmark/manifest.jsonl \
  --benchmark-root generated/benchmark --gitleaks "$GITLEAKS_BIN" --trufflehog "$TRUFFLEHOG_BIN" \
  --detect-secrets "$DETECT_SECRETS_BIN" --output results/metrics/latency.json

find generated/benchmark results evidence/evaluation -type f ! -name SHA256SUMS -print0 \
  | sort -z | xargs -0 sha256sum > evidence/evaluation/SHA256SUMS

echo "evaluation_finished_utc=$(date -u +%FT%TZ)"
