# Chess Challenge

Train a 1M parameter LLM to play chess!

## Objective

Design and train a transformer-based language model to predict chess moves. Your model must:

1. **Stay under 1M parameters** - This is the hard constraint!
2. **Use a custom tokenizer** - Design an efficient move-level tokenizer
3. **Play legal chess** - The model should learn to generate valid moves
4. **Beat Stockfish** - Your ELO will be measured against Stockfish Level 1

## Dataset

We use the Lichess dataset: [`dlouapre/lichess_2025-01_1M`](https://huggingface.co/datasets/dlouapre/lichess_2025-01_1M)

The dataset uses an extended UCI notation:
- `W`/`B` prefix for White/Black
- Piece letter: `P`=Pawn, `N`=Knight, `B`=Bishop, `R`=Rook, `Q`=Queen, `K`=King
- Source and destination squares (e.g., `e2e4`)
- Special suffixes: `(x)`=capture, `(+)`=check, `(+*)`=checkmate, `(o)`/`(O)`=castling

Example game:
```
WPe2e4 BPe7e5 WNg1f3 BNb8c6 WBf1b5 BPa7a6 WBb5c6(x) BPd7c6(x) ...
```

## Quick Start

### Train a Model

```bash
# Basic training
python -m src.train \
    --output_dir ./my_model \
    --num_train_epochs 3 \
    --per_device_train_batch_size 32
```

### Evaluate Your Model

Evaluation happens in two phases:

```bash
# Phase 1: Legal Move Evaluation (quick sanity check)
python -m src.evaluate \
    --model_path ./my_model \
    --mode legal \
    --n_positions 500

# Phase 2: Win Rate Evaluation (full games against Stockfish)
python -m src.evaluate \
    --model_path ./my_model \
    --mode winrate \
    --n_games 100 \
    --stockfish_level 1

# Or run both phases:
python -m src.evaluate \
    --model_path ./my_model \
    --mode both
```

## Parameter Budget

Use the utility function to check your budget:

```python
from src import ChessConfig, print_parameter_budget

config = ChessConfig(
    vocab_size=1200,
    n_embd=128,
    n_layer=4,
    n_head=4,
)
print_parameter_budget(config)
```

### Pro Tips

1. **Weight Tying**: The default config ties the embedding and output layer weights, saving ~154k parameters
2. **Vocabulary Size**: Keep it small! ~1200 tokens covers all moves
3. **Depth vs Width**: With limited parameters, experiment with shallow-but-wide vs deep-but-narrow

## Customization

### Custom Tokenizer

The template provides a move-level tokenizer that builds vocabulary from the actual dataset.
Feel free to try different approaches!

### Custom Architecture

Modify the model in `src/model.py`:

```python
from src import ChessConfig, ChessForCausalLM

# Customize configuration
config = ChessConfig(
    vocab_size=1200,
    n_embd=128,      # Try 96, 128, or 192
    n_layer=4,       # Try 3, 4, or 6
    n_head=4,        # Try 4 or 8
    n_inner=384,     # Feed-forward dimension (default: 3*n_embd)
    dropout=0.1,
    tie_weights=True,
)

model = ChessForCausalLM(config)
```

## Evaluation Metrics

### Phase 1: Legal Move Evaluation

Tests if your model generates valid chess moves:

| Metric | Description |
|--------|-------------|
| **Legal Rate (1st try)** | % of legal moves on first attempt |
| **Legal Rate (with retry)** | % of legal moves within 3 attempts |

> **Target**: >90% legal rate before proceeding to Phase 2

### Phase 2: Win Rate Evaluation

Full games against Stockfish to measure playing strength:

| Metric | Description |
|--------|-------------|
| **Win Rate** | % of games won against Stockfish |
| **ELO Rating** | Estimated rating based on game results |
| **Avg Game Length** | Average number of moves per game |
| **Illegal Move Rate** | % of illegal moves during games |


## Submission

1. Train your model
2. Log in to Hugging Face: `hf auth login`
3. Submit your model using the submission script:

```bash
python submit.py --model_path ./my_model/final_model --model_name your-model-name
```

The script will:
- Upload your model to the LLM-course organization
- Include your HF username in the model card for tracking
