# Tiny GPT-2 cache demo

`sshleifer/tiny-gpt2` is a small public test model. It runs on a standard CPU runner without a Hugging Face access token.

The cold job took 43 s and saved a 1.27 MiB model cache. Jobs with cache hits took 42–47 s and generated tokens with `HF_HUB_OFFLINE=1`. The observed job times were similar across cache states. [Cold run](https://github.com/roygrssmn/github-actions-model-cache-demo/actions/runs/42862743152/job/129992916704) · [Hot run](https://github.com/roygrssmn/github-actions-model-cache-demo/actions/runs/42863525738/job/129995673093)

## Run Tiny GPT-2 on GitHub

1. In a GitHub repository containing [the Tiny GPT-2 workflow](.github/workflows/model-cache.yml), open **Actions → Hugging Face model cache demo → Run workflow** and choose `main`.
2. Inspect the **Display cache status** step. With an empty cache, the first successful run shows `CACHE MISS` and saves the model cache at the end of the job.
3. Use **Run workflow** again on `main`. The same cache key should show `CACHE HIT` and model files should be restored. On a hit, the inference step sets `HF_HUB_OFFLINE=1` and must generate tokens using only the restored model files.

> Important: the cache is only saved after the job finishes successfully. A push-triggered run can also populate the cache before your first manual run. If you want to demonstrate a miss again, change the key in `.github/workflows/model-cache.yml` from `v1` to `v2`, then rerun twice.

## What the Tiny GPT-2 workflow caches

- `HF_HOME` is set to `${{ github.workspace }}/.cache/huggingface`.
- `actions/cache@v6` caches `.cache/huggingface/hub`, which is where Transformers and `huggingface_hub` keep downloaded model artifacts.
- The key `hf-tiny-gpt2-v1-${{ runner.os }}` deliberately stays stable across workflow runs.
- `actions/setup-python` separately caches pip downloads; that cache is not the model cache.

GitHub-hosted jobs recreate the Python environment each run. For this small model, pip and PyTorch installation can take longer than the model download.

## Run Tiny GPT-2 locally

```bash
python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python test_model.py
```
