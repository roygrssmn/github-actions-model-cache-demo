# GitHub Actions model cache test

Tested on 10 November 2026 on GitHub-hosted Linux runners with the `sshleifer/tiny-gpt2` model. The workflow caches `.cache/huggingface/hub` under `hf-tiny-gpt2-v1-Linux`. GitHub listed the cache at 1.27 MiB.

| Run | Result |
| --- | --- |
| [Cold run on main](https://github.com/roygrssmn/github-actions-model-cache-demo/actions/runs/42862743152/job/129992916704) | The model cache missed. The runner downloaded the model, generated tokens, and saved the cache after the test passed. |
| [First warm run on main](https://github.com/roygrssmn/github-actions-model-cache-demo/actions/runs/42862944111/job/129993634479) | A fresh runner restored the same key, ran with `HF_HUB_OFFLINE=1`, and generated tokens. |
| [Warm rerun on main](https://github.com/roygrssmn/github-actions-model-cache-demo/actions/runs/42863525738/job/129995673093) | A fresh runner logged `CACHE HIT` and `HF_HUB_OFFLINE=1` and generated eight tokens from the restored files. |
| [Warm run with upgraded actions](https://github.com/roygrssmn/github-actions-model-cache-demo/actions/runs/42863592302/job/129995909995) | The upgrade branch restored the same cache key and generated tokens with `HF_HUB_OFFLINE=1`. |

The warm runs confirm that the restored model files were sufficient for inference without contacting the Hugging Face Hub. The workflow installs Python dependencies separately and uses a separate pip cache.
