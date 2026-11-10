# GitHub Actions AI Model Cache Demo

Two CPU demos show how to cache Hugging Face model files across GitHub Actions runs. Use [`sshleifer/tiny-gpt2`](https://huggingface.co/sshleifer/tiny-gpt2) for a quick check or [Qwen2.5-1.5B-Instruct Q4_K_M](https://huggingface.co/Qwen/Qwen2.5-1.5B-Instruct-GGUF) to test a 4-bit model under 1.5 GB. See [cache-test.md](cache-test.md) for measured sizes and run logs.

## Try Tiny GPT-2 on GitHub

1. Create a GitHub repository named `github-actions-model-cache-demo` (without auto-generating a README).
2. Upload the files in this project, preserving `.github/workflows/model-cache.yml` (or push them using Git).
3. Open **Actions → Hugging Face model cache demo → Run workflow**.
4. Inspect the **Display cache status** step. The first successful run should show `CACHE MISS` and save the model cache at the end of the job.
5. Use **Run workflow** again on `main`. The same cache key should show `CACHE HIT` and model files should be restored. On a hit, the inference step sets `HF_HUB_OFFLINE=1` and must generate tokens using only the restored model files.

> Important: the cache is only saved after the job finishes successfully. A push-triggered run can also populate the cache before your first manual run. If you want to demonstrate a miss again, change the key in `.github/workflows/model-cache.yml` from `v1` to `v2`, then rerun twice.

## Why Qwen uses a prebuilt runtime

The original Python workflow took **4 min 16 s with the Qwen model cache enabled and the pip wheel cache disabled**. It restored the GGUF in 8 s, then spent 3 min 59 s building and installing `llama-cpp-python`. With the model cache also enabled and the compiled wheel available in pip's cache, the original workflow installed the runtime in 3 s. Reusing the wheel saved about 4 minutes on that step. See the [wheel-cache benchmark](cache-test.md#wheel-cache-benchmark-with-the-model-cache-enabled).

A Python wheel (`.whl`) is a ready-to-install package. The old `llama-cpp-python` wheel bundled the Python wrapper and the compiled C++ inference library. The GGUF model weights were cached separately. The old install command built from source whenever pip had no compatible cached wheel. Eviction, a Python or runner platform change, or a workflow edit that changed the pip cache key could trigger a build when no usable fallback was available.

The Qwen workflow now downloads a pinned Ubuntu CPU release of [llama.cpp](https://github.com/ggml-org/llama.cpp/releases), verifies its checksum, and runs `llama-completion` against the local GGUF. Both model-cache modes use the same prebuilt runtime.

## Try Qwen on GitHub

1. Open **Actions → Quantized model cache demo → Run workflow** and choose the branch you want to test.
2. Run once with **Restore and save the model cache** checked and once with it unchecked. With caching enabled, a hit restores the model and skips the download. A miss downloads the model and saves it after a successful test. With caching disabled, the runner downloads the GGUF file and skips both cache restore and save.
3. Check **Verify model size and checksum** and **Run offline inference from the local GGUF file**. The workflow enforces a 1.5 GB model file limit, checks SHA-256, and runs CPU inference in a Linux network namespace without external connectivity.

The workflow also runs on pushes that change its YAML. The model cache key includes the pinned Hugging Face revision and runner OS.

In the [paired model-cache comparison](cache-test.md#same-commit-with-and-without-the-model-cache), both jobs took 20 s and passed offline inference. Model retrieval took 11 s with the cache and 13 s without it.

## What does the Tiny GPT-2 workflow cache?

- `HF_HOME` is set to `${{ github.workspace }}/.cache/huggingface`.
- `actions/cache@v6` caches `.cache/huggingface/hub`, which is where Transformers and `huggingface_hub` keep downloaded model artifacts.
- The key `hf-tiny-gpt2-v1-${{ runner.os }}` deliberately stays stable across workflow runs.
- `actions/setup-python` separately caches pip downloads; that cache is not the model cache.

This demo caches *model downloads*, not generated outputs or model state in memory. GitHub-hosted jobs still recreate the Python environment each run.

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
