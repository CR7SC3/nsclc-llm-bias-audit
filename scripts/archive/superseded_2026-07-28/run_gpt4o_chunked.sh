#!/bin/zsh
cd /Users/alvarocuervo/Documents/EquityGUIDE
CK="results/baseline/v2_genie_bpc_nsclc_n300_gpt-4o_checkpoint.json"
TARGET=196
for i in $(seq 1 16); do
  done=$(python3 -c "import json,os;print(len(json.load(open('$CK'))) if os.path.exists('$CK') else 0)")
  echo "[chunk $i] checkpoint has $done cases (target $TARGET)"
  if [ "$done" -ge "$TARGET" ]; then echo "reached target, stopping."; break; fi
  python3 scripts/nsclc/run_experiment_v2_batch.py --subset genie_bpc_nsclc_n300 --model gpt-4o --max-cases 14
done
echo "=== GPT-4o chunked run finished ==="
