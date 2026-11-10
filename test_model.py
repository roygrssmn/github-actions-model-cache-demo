"""Download (or reuse) a tiny public GPT-2 model and run CPU inference."""

import os
from pathlib import Path

from transformers import AutoModelForCausalLM, AutoTokenizer

MODEL_ID = "sshleifer/tiny-gpt2"


def main() -> None:
    cache_dir = Path(os.environ.get("HF_HOME", "~/.cache/huggingface")).expanduser()
    print(f"Hugging Face cache root: {cache_dir}")
    print(f"Loading model: {MODEL_ID}")

    tokenizer = AutoTokenizer.from_pretrained(MODEL_ID)
    model = AutoModelForCausalLM.from_pretrained(MODEL_ID)
    model.eval()

    inputs = tokenizer("GitHub Actions caching", return_tensors="pt")
    output = model.generate(
        **inputs,
        max_new_tokens=8,
        do_sample=False,
        pad_token_id=tokenizer.eos_token_id,
    )
    result = tokenizer.decode(output[0], skip_special_tokens=True)
    print("Generated text:", repr(result))
    assert len(output[0][0:]) > inputs["input_ids"].shape[1], "No tokens generated"
    print("PASS: model loaded and generated tokens")


if __name__ == "__main__":
    main()
