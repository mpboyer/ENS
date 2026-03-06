#!/usr/bin/env python3
"""
Submission script for the Chess Challenge.

This script pushes your trained model to the Hugging Face Hub under the
LLM-course organization, with metadata tracking who submitted it.

Usage:
    python submit.py --model_path ./my_model/final_model --model_name my-chess-model
"""

import argparse
import os
import tempfile
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description="Submit your chess model to Hugging Face Hub")
    parser.add_argument(
        "--model_path", type=str, default="./my_model/final_model",
        help="Path to your trained model directory"
    )
    parser.add_argument(
        "--model_name", type=str, required=True,
        help="Name for your model on the Hub (e.g., 'my-chess-model')"
    )
    args = parser.parse_args()

    # Fixed organization
    organization = "LLM-course"

    # Check model path exists
    if not os.path.exists(args.model_path):
        print(f"Error: Model path '{args.model_path}' does not exist.")
        print("Train a model first with: python -m src.train --output_dir ./my_model")
        return 1

    # Import here to avoid slow startup
    from huggingface_hub import HfApi, HfFolder, whoami
    from transformers import AutoModelForCausalLM

    # Ensure user is logged in and get their info
    print("=" * 60)
    print("CHESS CHALLENGE - MODEL SUBMISSION")
    print("=" * 60)

    try:
        user_info = whoami()
        username = user_info["name"]
        print(f"\nLogged in as: {username}")
    except Exception:
        print("\nYou need to log in to Hugging Face first.")
        print("Run: huggingface-cli login")
        return 1

    # Import custom classes to register them
    from src.model import ChessConfig, ChessForCausalLM
    from src.tokenizer import ChessTokenizer

    # Load model and tokenizer
    print(f"\nLoading model from: {args.model_path}")
    model = AutoModelForCausalLM.from_pretrained(args.model_path)
    tokenizer = ChessTokenizer.from_pretrained(args.model_path)

    # Count parameters
    n_params = sum(p.numel() for p in model.parameters())
    print(f"Model parameters: {n_params:,}")

    if n_params > 1_000_000:
        print(f"WARNING: Model exceeds 1M parameter limit ({n_params:,} params)")

    # Prepare repo name
    repo_id = f"{organization}/{args.model_name}"
    print(f"\nSubmitting to: {repo_id}")

    # Create a temporary directory to prepare submission
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir)

        # Save model and tokenizer
        model.save_pretrained(tmp_path)
        tokenizer.save_pretrained(tmp_path)
        
        # Copy tokenizer.py to allow loading with trust_remote_code=True
        # This ensures the custom ChessTokenizer can be loaded from the Hub
        tokenizer_src = Path(__file__).parent / "src" / "tokenizer.py"
        if tokenizer_src.exists():
            import shutil
            shutil.copy(tokenizer_src, tmp_path / "tokenizer.py")
            print("   Included tokenizer.py for remote loading")

        # Create model card with submitter info
        model_card = f"""---
library_name: transformers
tags:
- chess
- llm-course
- chess-challenge
license: mit
---

# {args.model_name}

Chess model submitted to the LLM Course Chess Challenge.

## Submission Info

- **Submitted by**: [{username}](https://huggingface.co/{username})
- **Parameters**: {n_params:,}
- **Organization**: {organization}

## Model Details

- **Architecture**: Chess Transformer (GPT-style)
- **Vocab size**: {tokenizer.vocab_size}
- **Embedding dim**: {model.config.n_embd}
- **Layers**: {model.config.n_layer}
- **Heads**: {model.config.n_head}
"""
        (tmp_path / "README.md").write_text(model_card)

        # Push to Hub
        print("\nUploading to Hugging Face Hub...")
        api = HfApi()

        # Create repo if it doesn't exist
        api.create_repo(
            repo_id=repo_id,
            exist_ok=True,
        )

        # Upload all files
        api.upload_folder(
            folder_path=tmp_path,
            repo_id=repo_id,
            commit_message=f"Chess Challenge submission by {username}",
        )

    print("\n" + "=" * 60)
    print("SUBMISSION COMPLETE!")
    print("=" * 60)
    print(f"\nYour model is now available at:")
    print(f"  https://huggingface.co/{repo_id}")
    print(f"\nSubmitted by: {username}")
    print(f"Parameters: {n_params:,}")

    return 0


if __name__ == "__main__":
    exit(main())
