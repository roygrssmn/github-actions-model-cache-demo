# GitHub Actions model cache test

## Tiny GPT-2 baseline

The cold run saved a 1.27 MiB model cache in 43 s. Cache hits took 42–47 s and generated tokens with `HF_HUB_OFFLINE=1`. The observed job times were similar across cache states. [Cold run](https://github.com/roygrssmn/github-actions-model-cache-demo/actions/runs/42862743152/job/129992916704) · [Hot run](https://github.com/roygrssmn/github-actions-model-cache-demo/actions/runs/42863525738/job/129995673093)

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

The wheel was a `.whl` package containing the Python wrapper and compiled C++ inference library for Python 3.11 on Linux x86-64. The first run restored a fallback pip cache that lacked this wheel. With `--no-binary=llama-cpp-python`, pip compiled the package from source when no compatible locally cached wheel was available. In that workflow, eviction, a Python or runner platform change, or a workflow edit that changed the pip cache key could trigger another build if no usable wheel remained available. The GGUF cache held the model weights independently, so its hit or miss did not determine whether pip rebuilt the wheel.

## Wheel-cache benchmark with the model cache enabled

The original Python workflow ran on a separate benchmark branch with **the Qwen model cache enabled and the pip wheel cache disabled**. The model cache hit, the model download was skipped, and pip built the runtime from source. For comparison, the earlier runs below used the same Python runtime with the model cache enabled and a cached wheel available.

| Qwen runtime | Model cache | Runtime setup | Total job time |
| --- | --- | ---: | ---: |
| [Python with wheel cache](https://github.com/roygrssmn/github-actions-model-cache-demo/actions/runs/42866627073/job/130006586627) | Hit | 3 s | 23 s |
| [Python without wheel cache](https://github.com/roygrssmn/github-actions-model-cache-demo/actions/runs/42904712831/job/130139567011) | Hit | 3 min 59 s | 4 min 16 s |
| [Prebuilt llama.cpp](https://github.com/roygrssmn/github-actions-model-cache-demo/actions/runs/42868298866/job/130012439450) | Hit | 1 s | 17 s |

Runtime setup covers installing the Python package or downloading, verifying, and unpacking the prebuilt binary. Total job time excludes queueing. All three runs passed offline inference. A second [Python run with a cached wheel](https://github.com/roygrssmn/github-actions-model-cache-demo/actions/runs/42866619726/job/130006562394) also took 3 s to install the runtime and finished in 35 s.

The wheel-cache-disabled job restored the GGUF in 8 s and generated seven tokens offline. The runtime install was **3 min 56 s shorter** in both jobs that reused the cached wheel. The runtime build accounts for most of the difference between these jobs. The prebuilt runtime removes the source build even when no wheel cache is available.

## Qwen with the prebuilt llama.cpp runtime

In the [prebuilt runtime branch run](https://github.com/roygrssmn/github-actions-model-cache-demo/actions/runs/42868298866/job/130012439450), the job finished in **17 s**. Restoring the existing model cache took **10 s**, and the job skipped the GGUF download. Downloading, verifying, and unpacking the pinned Ubuntu CPU runtime took **1 s**. The CLI generated the expected completion with networking disabled.

The previous hot jobs on `main` took **23 s and 35 s** with the compiled wheel already in the pip cache. The prebuilt workflow removes the cold runtime build, which previously took **4 min 7 s**. The branch run measured a model cache hit.

### Same commit with and without the model cache

Both manual runs used commit `87ab6db`, the same Qwen model and pinned runtime, and the same prompt. Each verified both checksums and produced the same answer with networking disabled.

| Run | Cache behavior | Model retrieval | Job time | Offline inference |
| --- | --- | ---: | ---: | --- |
| [With cache](https://github.com/roygrssmn/github-actions-model-cache-demo/actions/runs/42871089114/job/130022259010) | Restored the existing cache and skipped the model download. | 11 s | 20 s | Pass |
| [Without cache](https://github.com/roygrssmn/github-actions-model-cache-demo/actions/runs/42871094268/job/130022277850) | Skipped cache restore and save. Downloaded the GGUF from Hugging Face. | 13 s | 20 s | Pass |

Cache restore saved 2 s on model retrieval in this pair. Total job time was the same at GitHub's whole-second precision.

### Ten randomized trials

The [benchmark run](https://github.com/roygrssmn/github-actions-model-cache-demo/actions/runs/42869313207) shuffled ten capital-city prompts and randomly assigned five to each cache state using fixed seeds. Each trial ran on a separate GitHub-hosted runner with the same model and prebuilt runtime. All checked their expected cache state, verified both checksums, and generated the expected city with networking disabled.

| Trial | Cache | Expected city | Model retrieval | Runtime setup | Job time | Offline result |
| --- | --- | --- | ---: | ---: | ---: | --- |
| [1](https://github.com/roygrssmn/github-actions-model-cache-demo/actions/runs/42869313207/job/130015987086) | Cold | Tokyo | 14 s | 0 s | 20 s | Pass |
| [2](https://github.com/roygrssmn/github-actions-model-cache-demo/actions/runs/42869313207/job/130015986995) | Hot | Madrid | 12 s | 1 s | 21 s | Pass |
| [3](https://github.com/roygrssmn/github-actions-model-cache-demo/actions/runs/42869313207/job/130015986932) | Hot | Paris | 6 s | 1 s | 12 s | Pass |
| [4](https://github.com/roygrssmn/github-actions-model-cache-demo/actions/runs/42869313207/job/130015986920) | Cold | Rome | 7 s | 1 s | 16 s | Pass |
| [5](https://github.com/roygrssmn/github-actions-model-cache-demo/actions/runs/42869313207/job/130015987071) | Cold | Helsinki | 15 s | 1 s | 24 s | Pass |
| [6](https://github.com/roygrssmn/github-actions-model-cache-demo/actions/runs/42869313207/job/130015987127) | Cold | Oslo | 6 s | 1 s | 15 s | Pass |
| [7](https://github.com/roygrssmn/github-actions-model-cache-demo/actions/runs/42869313207/job/130015987177) | Hot | Lisbon | 11 s | 1 s | 20 s | Pass |
| [8](https://github.com/roygrssmn/github-actions-model-cache-demo/actions/runs/42869313207/job/130015987442) | Hot | Berlin | 5 s | 1 s | 12 s | Pass |
| [9](https://github.com/roygrssmn/github-actions-model-cache-demo/actions/runs/42869313207/job/130015987455) | Hot | Vienna | 8 s | 1 s | 17 s | Pass |
| [10](https://github.com/roygrssmn/github-actions-model-cache-demo/actions/runs/42869313207/job/130015987052) | Cold | Athens | 14 s | 0 s | 22 s | Pass |

- **Cold.** Job time was 20 s median (15–24 s). Model download was 14 s median (6–15 s).
- **Hot.** Job time was 17 s median (12–21 s). Model restore was 8 s median (5–12 s).
- **Runtime setup.** Cold trials took 1 s median (0–1 s) and hot trials took 1 s median (1–1 s).

The hot median job took 3 s less. The ranges overlapped, so the cache benefit varied across runners. Cold trials used unique keys and a restore-only action to avoid writing five duplicate caches. Their times exclude cache upload, and all job times exclude queueing.
