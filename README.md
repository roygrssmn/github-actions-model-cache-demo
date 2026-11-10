# GitHub Actions AI Model Cache Demo

A small demo of caching Hugging Face model files across GitHub Actions runs. It loads [`sshleifer/tiny-gpt2`](https://huggingface.co/sshleifer/tiny-gpt2) on CPU and generates a few tokens.

## Try it on GitHub

1. Create a GitHub repository named `github-actions-model-cache-demo` (without auto-generating a README).
2. Upload the files in this project, preserving `.github/workflows/model-cache.yml` (or push them using Git).
3. Open **Actions → Hugging Face model cache demo → Run workflow**.
4. Inspect the **Display cache status** step. The first successful run should show `CACHE MISS` and save the model cache at the end of the job.
5. Use **Run workflow** again on `main`. The same cache key should show `CACHE HIT` and model files should be restored. On a hit, the inference step sets `HF_HUB_OFFLINE=1` and must generate tokens using only the restored model files.

> Important: the cache is only saved after the job finishes successfully. A push-triggered run can also populate the cache before your first manual run. If you want to demonstrate a miss again, change the key in `.github/workflows/model-cache.yml` from `v1` to `v2`, then rerun twice.

## What is cached?

- `HF_HOME` is set to `${{ github.workspace }}/.cache/huggingface`.
- `actions/cache@v4` caches `.cache/huggingface/hub`, which is where Transformers and `huggingface_hub` keep downloaded model artifacts.
- The key `hf-tiny-gpt2-v1-${{ runner.os }}` deliberately stays stable across workflow runs.
- `actions/setup-python` separately caches pip downloads; that cache is not the model cache.

This demo caches *model downloads*, not generated outputs or model state in memory. Github-hosted jobs still recreate the Python environment each run.

## Run locally

```bash
python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python test_model.py
```

## Why this model?

`sshleifer/tiny-gpt2` is a small public test model. It runs on a normal CPU runner; output quality is intentionally poor. No tokens or GPU are needed.

## Limitations

- GitHub Actions cache is best-effort, subject to quotas, eviction, visibility rules, and retention policies; it is not long-term model storage.
- Cache keys should include a model revision or version if you need controlled reproducibility. This demo keeps a single explicit version for clarity.
- Pip and PyTorch installation can take longer than model download for such a tiny example.
- For large LLMs, use persistent storage or a self-hosted runner rather than relying on Actions cache.
