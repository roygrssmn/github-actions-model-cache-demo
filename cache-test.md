# GitHub Actions model cache test

Tested on 10 November 2026 on GitHub-hosted Linux runners with the `sshleifer/tiny-gpt2` model. The workflow caches `.cache/huggingface/hub` under `hf-tiny-gpt2-v1-Linux`. GitHub listed the cache at 1.27 MiB.

| Run | Job time | Result |
| --- | ---: | --- |
| [Cold run on main](https://github.com/roygrssmn/github-actions-model-cache-demo/actions/runs/42862743152/job/129992916704) | 43 s | The model cache missed. The runner downloaded the model, generated tokens, and saved the cache after the test passed. |
| [First hot run on main](https://github.com/roygrssmn/github-actions-model-cache-demo/actions/runs/42862944111/job/129993634479) | 47 s | A fresh runner restored the same key, ran with `HF_HUB_OFFLINE=1`, and generated tokens. |
| [Hot rerun on main](https://github.com/roygrssmn/github-actions-model-cache-demo/actions/runs/42863525738/job/129995673093) | 42 s | A fresh runner logged `CACHE HIT` and `HF_HUB_OFFLINE=1` and generated eight tokens from the restored files. |
| [Hot run with upgraded actions](https://github.com/roygrssmn/github-actions-model-cache-demo/actions/runs/42863592302/job/129995909995) | 47 s | The upgrade branch restored the same cache key and generated tokens with `HF_HUB_OFFLINE=1`. |

The hot runs confirm that the restored model files were sufficient for inference without contacting the Hugging Face Hub. The workflow installs Python dependencies separately and uses a separate pip cache. The measured Tiny GPT-2 job times were similar across cache states.

## Qwen2.5-1.5B-Instruct Q4_K_M baseline with the Python runtime

Tested on 10 November 2026 on GitHub-hosted Linux runners. The 4-bit GGUF file was **1,117,320,736 bytes (1.117 GB)**. GitHub reported a compressed model cache of **1,092,088,856 bytes (1.092 GB)** on `main`. Both sizes are below 1.5 GB.

Cache key: `hf-qwen2.5-1.5b-q4_k_m-91cad51170dc346986eccefdc2dd33a9da36ead9-Linux`.

| Run | Model cache | Job time | Offline CPU inference |
| --- | --- | ---: | --- |
| [Merge-triggered run](https://github.com/roygrssmn/github-actions-model-cache-demo/actions/runs/42865704148/job/130003333994) | Cold (miss). Downloaded the GGUF file and saved the cache after the test passed. | 4 min 43 s | SHA-256 matched. Generated 7 tokens. |
| [Manual dispatch 1](https://github.com/roygrssmn/github-actions-model-cache-demo/actions/runs/42866619726/job/130006562394) | Hot (hit). Restored the same key and skipped the download. | 35 s | SHA-256 matched. Generated 7 tokens. |
| [Manual dispatch 2](https://github.com/roygrssmn/github-actions-model-cache-demo/actions/runs/42866627073/job/130006586627) | Hot (hit). Restored the same key and skipped the download. | 23 s | SHA-256 matched. Generated 7 tokens. |

Each inference step ran in a Linux network namespace without external connectivity. The two manual runs therefore verified that the restored GGUF file was sufficient to generate tokens. The reported model cache size excludes the separate pip cache.

### Qwen job timing by step

Job times exclude queue time. Step durations use GitHub's whole-second timestamps, so subsecond steps can show as 0 s.

| GitHub Actions step | Cold | Hot 1 | Hot 2 |
| --- | ---: | ---: | ---: |
| Set up job | 1 s | 1 s | 1 s |
| Check out repository | 1 s | 1 s | 1 s |
| Set up Python | 2 s | 10 s | 5 s |
| Restore quantized model cache | 0 s (miss) | 12 s | 7 s |
| Download model on cache miss | 17 s | Skipped | Skipped |
| Verify model size and checksum | 1 s | 1 s | 1 s |
| Install CPU inference runtime | 4 min 7 s | 3 s | 3 s |
| Run offline inference from the local GGUF file | 2 s | 3 s | 1 s |
| Post Restore quantized model cache | 7 s (save) | 0 s | 0 s |
| Post Set up Python | 2 s | 0 s | 0 s |
| Post Check out repository | 0 s | 0 s | 1 s |
| Complete job | 0 s | 0 s | 0 s |

The hot jobs took **88–92% less time** than the cold job. The step timings show how each cache contributed.

- **Model cache.** GitHub restored the Qwen GGUF weights in 7–12 s and skipped the 17 s download, saving 5–10 s on model retrieval. Saving the cache added 7 s to the cold job.
- **Pip cache.** The **Install CPU inference runtime** step installed `llama-cpp-python`, which loads the GGUF file and generates tokens on the CPU. The cold run compiled its C++ code into a Python wheel and installed it in 4 min 7 s. The hot runs installed the same wheel from the pip cache in 3 s each, saving 4 min 4 s on that step. This accounted for most of the overall speedup.

## Qwen with the prebuilt llama.cpp runtime

In the [prebuilt runtime branch run](https://github.com/roygrssmn/github-actions-model-cache-demo/actions/runs/42868298866/job/130012439450), the job finished in **17 s**. Restoring the existing model cache took **10 s**, and the job skipped the GGUF download. Downloading, verifying, and unpacking the pinned Ubuntu CPU runtime took **1 s**. The CLI generated the expected completion with networking disabled.

The previous hot jobs on `main` took **23 s and 35 s** with the compiled wheel already in the pip cache. The prebuilt workflow removes the cold runtime build, which previously took **4 min 7 s**. The branch run measured a model cache hit. A cold-model end-to-end comparison remains unmeasured.
