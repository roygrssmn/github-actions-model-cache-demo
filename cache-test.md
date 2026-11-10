# GitHub Actions model cache test

Tested on 10 November 2026 on GitHub-hosted Linux runners with the `sshleifer/tiny-gpt2` model. The workflow caches `.cache/huggingface/hub` under `hf-tiny-gpt2-v1-Linux`. GitHub listed the cache at 1.27 MiB.

| Run | Result |
| --- | --- |
| [Cold run on main](https://github.com/roygrssmn/github-actions-model-cache-demo/actions/runs/42862743152/job/129992916704) | The model cache missed. The runner downloaded the model, generated tokens, and saved the cache after the test passed. |
| [First warm run on main](https://github.com/roygrssmn/github-actions-model-cache-demo/actions/runs/42862944111/job/129993634479) | A fresh runner restored the same key, ran with `HF_HUB_OFFLINE=1`, and generated tokens. |
| [Warm rerun on main](https://github.com/roygrssmn/github-actions-model-cache-demo/actions/runs/42863525738/job/129995673093) | A fresh runner logged `CACHE HIT` and `HF_HUB_OFFLINE=1` and generated eight tokens from the restored files. |
| [Warm run with upgraded actions](https://github.com/roygrssmn/github-actions-model-cache-demo/actions/runs/42863592302/job/129995909995) | The upgrade branch restored the same cache key and generated tokens with `HF_HUB_OFFLINE=1`. |

The warm runs confirm that the restored model files were sufficient for inference without contacting the Hugging Face Hub. The workflow installs Python dependencies separately and uses a separate pip cache.

## Qwen2.5-1.5B-Instruct Q4_K_M on main

Tested on 10 November 2026 on GitHub-hosted Linux runners. The 4-bit GGUF file was **1,117,320,736 bytes (1.117 GB)**. GitHub reported a compressed model cache of **1,092,088,856 bytes (1.092 GB)** on `main`. Both sizes are below 1.5 GB.

Cache key: `hf-qwen2.5-1.5b-q4_k_m-91cad51170dc346986eccefdc2dd33a9da36ead9-Linux`.

| Run | Model cache | Offline CPU inference |
| --- | --- | --- |
| [Merge-triggered run](https://github.com/roygrssmn/github-actions-model-cache-demo/actions/runs/42865704148/job/130003333994) | Cold. Downloaded the GGUF file and saved the cache after the test passed. | SHA-256 matched. Generated 7 tokens. |
| [Manual dispatch 1](https://github.com/roygrssmn/github-actions-model-cache-demo/actions/runs/42866619726/job/130006562394) | Warm. Restored the same key and skipped the download. | SHA-256 matched. Generated 7 tokens. |
| [Manual dispatch 2](https://github.com/roygrssmn/github-actions-model-cache-demo/actions/runs/42866627073/job/130006586627) | Warm. Restored the same key and skipped the download. | SHA-256 matched. Generated 7 tokens. |

Each inference step ran in a Linux network namespace without external connectivity. The two manual runs therefore verified that the restored GGUF file was sufficient to generate tokens. The reported model cache size excludes the separate pip cache.
