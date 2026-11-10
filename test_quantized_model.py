"""Run CPU inference using a local quantized GGUF model."""

import argparse
from pathlib import Path

from llama_cpp import Llama


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("model_path", type=Path)
    args = parser.parse_args()

    model = Llama(model_path=str(args.model_path), n_ctx=512, n_gpu_layers=0, verbose=False)
    result = model.create_chat_completion(
        messages=[{"role": "user", "content": "Name the capital of France."}],
        max_tokens=16,
        temperature=0,
    )
    completion_tokens = result["usage"]["completion_tokens"]
    if completion_tokens <= 0 or not result["choices"][0]["message"]["content"]:
        raise RuntimeError("Model did not generate a response")

    print(f"PASS: generated {completion_tokens} tokens from the local GGUF file")


if __name__ == "__main__":
    main()
