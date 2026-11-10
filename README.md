# GitHub Actions AI Model Cache Demo

Two CPU demos show how to cache Hugging Face model files across GitHub Actions runs. Use [`sshleifer/tiny-gpt2`](https://huggingface.co/sshleifer/tiny-gpt2) for a quick check or [Qwen2.5-1.5B-Instruct Q4_K_M](https://huggingface.co/Qwen/Qwen2.5-1.5B-Instruct-GGUF) to test a 4-bit model under 1.5 GB. See [cache-test.md](cache-test.md) for measured sizes and run logs.

## Try Tiny GPT-2 on GitHub

1. Create a GitHub repository named `github-actions-model-cache-demo` (without auto-generating a README).
2. Upload the files in this project, preserving `.github/workflows/model-cache.yml` (or push them using Git).
3. Open **Actions → Hugging Face model cache demo → Run workflow**.
4. Inspect the **Display cache status** step. The first successful run should show `CACHE MISS` and save the model cache at the end of the job.
5. Use **Run workflow** again on `main`. The same cache key should show `CACHE HIT` and model files should be restored. On a hit, the inference step sets `HF_HUB_OFFLINE=1` and must generate tokens using only the restored model files.

> Important: the cache is only saved after the job finishes successfully. A push-triggered run can also populate the cache before your first manual run. If you want to demonstrate a miss again, change the key in `.github/workflows/model-cache.yml` from `v1` to `v2`, then rerun twice.

## Try Qwen on GitHub

1. Open **Actions → Quantized model cache demo → Run workflow** and choose `main`.
2. In **Restore quantized model cache**, look for a restored `hf-qwen2.5-1.5b-q4_k_m-…-Linux` key. On a hit, **Download model on cache miss** is skipped. On a miss, the job downloads the GGUF file and saves it after the test passes.
3. Check **Verify model size and checksum** and **Run offline inference from the local GGUF file**. The workflow enforces a 1.5 GB model file limit, checks SHA-256, and runs CPU inference in a Linux network namespace without external connectivity.

The workflow also runs on pushes that change its YAML or inference script. On `main`, the cold job took 4 min 43 s and the two hot jobs took 35 s and 23 s. The workflow uses two caches.

- **Model cache.** Stores the Qwen GGUF weights under a key that includes the pinned Hugging Face revision and runner OS. Restoring the file took 7–12 s, saving 5–10 s compared with the 17 s download.
- **Pip cache.** Stores the compiled Python wheel for `llama-cpp-python`, which loads the GGUF file and generates tokens on the CPU. The **Install CPU inference runtime** step built the wheel from source in the cold run and reused it in the hot runs. That step fell from 4 min 7 s to 3 s, accounting for most of the overall speedup.

See [the step timings](cache-test.md#qwen-job-timing-by-step).

## What does the Tiny GPT-2 workflow cache?

- `HF_HOME` is set to `${{ github.workspace }}/.cache/huggingface`.
- `actions/cache@v6` caches `.cache/huggingface/hub`, which is where Transformers and `huggingface_hub` keep downloaded model artifacts.
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

## Why Tiny GPT-2?

`sshleifer/tiny-gpt2` is a small public test model. It runs on a normal CPU runner; output quality is intentionally poor. No tokens or GPU are needed.

## Limitations

- GitHub Actions cache is best-effort, subject to quotas, eviction, visibility rules, and retention policies; it is not long-term model storage.
- The Tiny GPT-2 cache uses an explicit version in its key. The Qwen cache uses the pinned model revision.
- Pip and PyTorch installation can take longer than model download for such a tiny example.
- For large LLMs, use persistent storage or a self-hosted runner rather than relying on Actions cache.
