# GitHub Actions AI Model Cache Demo

This project uses [Qwen2.5-1.5B-Instruct Q4_K_M](https://huggingface.co/Qwen/Qwen2.5-1.5B-Instruct-GGUF) to compare CPU runtime setup and model caching in GitHub Actions with a 4-bit model under 1.5 GB. See [cache-test.md](cache-test.md) for the Qwen runtime benchmarks and run logs.

To run Qwen in your own repository, push this project with its [Qwen workflow](.github/workflows/quantized-model-cache.yml).

## Qwen and its prebuilt runtime

In the benchmark runs, the original Python workflow took **4 min 16 s with the Qwen model cache enabled and the pip wheel cache disabled**. It restored the GGUF in 8 s, then spent 3 min 59 s building and installing `llama-cpp-python`. With the model cache also enabled and the compiled wheel available in pip's cache, the original workflow installed the runtime in 3 s. Installing from the cached wheel was about four minutes faster in these runs. The prebuilt runtime took 1 s to set up and its job finished in 17 s with a model cache hit. See the [side-by-side runtime benchmark](cache-test.md#wheel-cache-benchmark-with-the-model-cache-enabled).

A Python wheel (`.whl`) is a ready-to-install package. The old `llama-cpp-python` wheel bundled the Python wrapper and the compiled C++ inference library. The GGUF model weights were cached separately. The old install command built from source whenever pip had no compatible cached wheel. Eviction, a Python or runner platform change, or a workflow edit that changed the pip cache key could trigger a build when no usable fallback was available.

The Qwen workflow now downloads a pinned Ubuntu CPU release of [llama.cpp](https://github.com/ggml-org/llama.cpp/releases), verifies its checksum, and runs `llama-completion` against the local GGUF. Both model-cache modes use the same prebuilt runtime.

### Run Qwen on GitHub

1. Open **Actions → Quantized model cache demo → Run workflow** and choose the branch you want to test.
2. Run once with **Restore and save the model cache** checked and once with it unchecked. With caching enabled, a hit restores the model and skips the download. A miss downloads the model and saves it after a successful test. With caching disabled, the runner downloads the GGUF file and skips both cache restore and save.
3. Check **Verify model size and checksum** and **Run offline inference from the local GGUF file**. The workflow enforces a 1.5 GB model file limit, checks SHA-256, and runs CPU inference in a Linux network namespace without external connectivity.

The workflow also runs on pushes that change its YAML. The model cache key includes the pinned Hugging Face revision and runner OS.

In the [paired model-cache comparison](cache-test.md#same-commit-with-and-without-the-model-cache), both jobs took 20 s and passed offline inference. Model retrieval took 11 s with the cache and 13 s without it.

## Limitations

- GitHub Actions caches are subject to quotas, eviction, branch access rules, and retention policies.
- For large LLMs, use persistent storage or a self-hosted runner rather than relying on Actions cache.

See also the [standalone Tiny GPT-2 cache demo](tiny-gpt2.md).
