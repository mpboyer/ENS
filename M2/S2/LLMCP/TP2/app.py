"""
Play Chess like a Honey Bee

This Gradio app provides:
1. Interactive demo to test models
2. Leaderboard of submitted models
3. Live game visualization

Instructions:
The goal is to train a language model to play chess, under a strict constraint:
less than 1M parameters! This is approximately the number of neurons of a honey bee.

Leaderboard data is stored in a private HuggingFace dataset for persistence.
"""

import io
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

import gradio as gr
import pandas as pd

# Configuration
ORGANIZATION = os.environ.get("HF_ORGANIZATION", "LLM-course")
LEADERBOARD_DATASET = os.environ.get("LEADERBOARD_DATASET", f"{ORGANIZATION}/chess-challenge-leaderboard")
LEADERBOARD_FILENAME = "leaderboard.csv"
HF_TOKEN = os.environ.get("HF_TOKEN")  # Required for private dataset access

# Evaluation settings
EVAL_SEED = 42
EVAL_N_POSITIONS = 500

STOCKFISH_LEVELS = {
    "Beginner (Level 0)": 0,
    "Easy (Level 1)": 1,
    "Medium (Level 3)": 3,
    "Hard (Level 5)": 5,
}

# CSV columns for the leaderboard
LEADERBOARD_COLUMNS = [
    "model_id",
    "user_id",
    "legal_rate",
    "legal_rate_first_try",
    # "elo",
    # "win_rate",
    # "draw_rate",
    # "games_played",
    "last_updated",
]


def load_leaderboard() -> list:
    """Load leaderboard from private HuggingFace dataset."""
    try:
        from huggingface_hub import hf_hub_download
        
        # Download the CSV file from the dataset
        csv_path = hf_hub_download(
            repo_id=LEADERBOARD_DATASET,
            filename=LEADERBOARD_FILENAME,
            repo_type="dataset",
            token=HF_TOKEN,
        )
        
        df = pd.read_csv(csv_path)
        return df.to_dict(orient="records")
    
    except Exception as e:
        print(f"Could not load leaderboard from dataset: {e}")
        # Return empty list if dataset doesn't exist yet
        return []


def save_leaderboard(data: list):
    """Save leaderboard to private HuggingFace dataset."""
    try:
        from huggingface_hub import HfApi
        
        # Convert to DataFrame
        df = pd.DataFrame(data, columns=LEADERBOARD_COLUMNS)
        
        # Fill missing columns with defaults
        for col in LEADERBOARD_COLUMNS:
            if col not in df.columns:
                df[col] = None
        
        # Reorder columns
        df = df[LEADERBOARD_COLUMNS]
        
        # Convert to CSV bytes
        csv_buffer = io.BytesIO()
        df.to_csv(csv_buffer, index=False)
        csv_buffer.seek(0)
        
        # Upload to HuggingFace dataset
        api = HfApi(token=HF_TOKEN)
        api.upload_file(
            path_or_fileobj=csv_buffer,
            path_in_repo=LEADERBOARD_FILENAME,
            repo_id=LEADERBOARD_DATASET,
            repo_type="dataset",
            commit_message=f"Update leaderboard - {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        )
        print(f"Leaderboard saved to {LEADERBOARD_DATASET}")
        
    except Exception as e:
        print(f"Error saving leaderboard to dataset: {e}")
        raise


def get_available_models() -> list:
    """Fetch available models from the organization."""
    try:
        from huggingface_hub import list_models
        
        models = list_models(author=ORGANIZATION)
        return [m.id for m in models if "chess" in m.id.lower()]
    except Exception as e:
        print(f"Error fetching models: {e}")
        return ["No models available"]


def format_leaderboard_html(data: list) -> str:
    """Format leaderboard data as HTML table."""
    if not data:
        return "<p>No models evaluated yet. Be the first to submit!</p>"
    
    # Sort by legal_rate
    sorted_data = sorted(data, key=lambda x: x.get("legal_rate", 0), reverse=True)
    
    html = """
    <style>
        .leaderboard-table {
            width: 100%;
            border-collapse: collapse;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }
        .leaderboard-table th {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 12px;
            text-align: left;
        }
        .leaderboard-table td {
            padding: 10px 12px;
            border-bottom: 1px solid var(--border-color-primary, #ddd);
        }
        .rank-1 { color: #ffd700; font-weight: bold; }
        .rank-2 { color: #c0c0c0; font-weight: bold; }
        .rank-3 { color: #cd7f32; font-weight: bold; }
        .model-link { color: #667eea; text-decoration: none; }
        .model-link:hover { text-decoration: underline; }
        .legal-good { color: #28a745; }
        .legal-medium { color: #ffc107; }
        .legal-bad { color: #dc3545; }
    </style>
    <table class="leaderboard-table">
        <thead>
            <tr>
                <th>Rank</th>
                <th>User</th>
                <th>Model</th>
                <th>Legal Rate</th>
                <th>Legal Rate (1st try)</th>
                <!-- <th>ELO</th> -->
                <!-- <th>Win Rate</th> -->
                <!-- <th>Games</th> -->
                <th>Last Updated</th>
            </tr>
        </thead>
        <tbody>
    """
    
    for i, entry in enumerate(sorted_data, 1):
        rank_class = f"rank-{i}" if i <= 3 else ""
        rank_display = ["🥇", "🥈", "🥉"][i-1] if i <= 3 else str(i)
        
        model_url = f"https://huggingface.co/{entry['model_id']}"
        
        # Color code legal rate
        legal_rate = entry.get('legal_rate', 0)
        if legal_rate >= 0.9:
            legal_class = "legal-good"
        elif legal_rate >= 0.7:
            legal_class = "legal-medium"
        else:
            legal_class = "legal-bad"
        
        legal_rate_first_try = entry.get('legal_rate_first_try', 0)
        user_id = entry.get('user_id', 'unknown')
        user_url = f"https://huggingface.co/{user_id}"
        html += f"""
            <tr>
                <td class="{rank_class}">{rank_display}</td>
                <td><a href="{user_url}" target="_blank" class="model-link">{user_id}</a></td>
                <td><a href="{model_url}" target="_blank" class="model-link">{entry['model_id'].split('/')[-1]}</a></td>
                <td class="{legal_class}">{legal_rate*100:.1f}%</td>
                <td>{legal_rate_first_try*100:.1f}%</td>
                <!-- <td><strong>{entry.get('elo', 'N/A')}</strong></td> -->
                <!-- <td>{entry.get('win_rate', 0)*100:.1f}%</td> -->
                <!-- <td>{entry.get('games_played', 0)}</td> -->
                <td>{entry.get('last_updated', 'N/A')}</td>
            </tr>
        """
    
    html += "</tbody></table>"
    return html


def render_board_svg(fen: str = "startpos") -> str:
    """Render a chess board as SVG."""
    try:
        import chess
        import chess.svg
        
        if fen == "startpos":
            board = chess.Board()
        else:
            board = chess.Board(fen)
        
        return chess.svg.board(board, size=400)
    except ImportError:
        return "<p>Install python-chess to see the board</p>"


def play_move(
    model_id: str,
    current_fen: str,
    move_history: str,
    temperature: float,
) -> tuple:
    """Play a move with the selected model."""
    try:
        import chess
        import torch
        import sys
        sys.path.insert(0, str(Path(__file__).parent))
        
        from src.evaluate import load_model_from_hub
        
        # Load model using the same method as evaluation
        model, tokenizer = load_model_from_hub(model_id)
        model.eval()
        
        # Setup board
        board = chess.Board(current_fen) if current_fen != "startpos" else chess.Board()
        
        # Tokenize history
        if move_history:
            inputs = tokenizer(move_history, return_tensors="pt")
        else:
            inputs = tokenizer(tokenizer.bos_token, return_tensors="pt")
        
        # Generate move
        with torch.no_grad():
            outputs = model(**inputs)
            logits = outputs.logits[:, -1, :] / temperature
            probs = torch.softmax(logits, dim=-1)
            next_token = torch.multinomial(probs, num_samples=1)
        
        move_token = tokenizer.decode(next_token[0])
        
        # Parse move
        if len(move_token) >= 6:
            uci_move = move_token[2:4] + move_token[4:6]
            try:
                move = chess.Move.from_uci(uci_move)
                if move in board.legal_moves:
                    board.push(move)
                    new_history = f"{move_history} {move_token}".strip()
                    return (
                        render_board_svg(board.fen()),
                        board.fen(),
                        new_history,
                        f"Model played: {move_token} ({uci_move})",
                    )
            except:
                pass
        
        return (
            render_board_svg(current_fen if current_fen != "startpos" else None),
            current_fen,
            move_history,
            f"Model generated illegal move: {move_token}",
        )
        
    except Exception as e:
        return (
            render_board_svg(),
            "startpos",
            "",
            f"Error: {str(e)}",
        )


def get_model_submitter(model_id: str) -> Optional[str]:
    """Extract the submitter's username from the model's README on HuggingFace.
    
    Returns None if the submitter cannot be determined.
    """
    try:
        from huggingface_hub import hf_hub_download
        import re
        
        # Download the README.md from the model repo
        readme_path = hf_hub_download(
            repo_id=model_id,
            filename="README.md",
            token=HF_TOKEN,
        )
        
        with open(readme_path, "r") as f:
            readme_content = f.read()
        
        # Look for the pattern: **Submitted by**: [username](https://huggingface.co/username)
        match = re.search(r'\*\*Submitted by\*\*:\s*\[([^\]]+)\]', readme_content)
        if match:
            return match.group(1)
        
        # Fallback: try to get from model info
        from huggingface_hub import model_info
        info = model_info(model_id, token=HF_TOKEN)
        if info.author:
            return info.author
            
    except Exception as e:
        print(f"Could not extract submitter from model: {e}")
    
    return None


def evaluate_legal_moves(
    model_id: str,
    progress: gr.Progress = gr.Progress(),
) -> str:
    """Evaluate a model's legal move generation."""
    try:
        import sys
        sys.path.insert(0, str(Path(__file__).parent))
        
        from src.evaluate import ChessEvaluator, load_model_from_hub
        
        progress(0, desc="Loading model...")
        model, tokenizer = load_model_from_hub(model_id)
        
        progress(0.1, desc="Setting up evaluator...")
        evaluator = ChessEvaluator(
            model=model,
            tokenizer=tokenizer,
            stockfish_level=1,  # Not used for legal move eval
        )
        
        progress(0.2, desc=f"Testing {EVAL_N_POSITIONS} positions...")
        results = evaluator.evaluate_legal_moves(
            n_positions=EVAL_N_POSITIONS,
            verbose=False,
            seed=EVAL_SEED,
        )
        
        # Extract user_id from model's README (submitted by field)
        user_id = get_model_submitter(model_id)
        if user_id is None:
            return f"""## Evaluation Failed

Could not determine the submitter for model `{model_id}`.

Please ensure your model was submitted using the official submission script (`submit.py`), 
which adds the required metadata to the README.md file.
"""
        
        # Update leaderboard - only if improved
        leaderboard = load_leaderboard()
        entry = next((e for e in leaderboard if e["model_id"] == model_id), None)
        
        new_legal_rate = results.get("legal_rate_with_retry", 0)
        new_legal_rate_first_try = results.get("legal_rate_first_try", 0)
        
        if entry is None:
            # New model - add to leaderboard
            entry = {
                "model_id": model_id,
                "user_id": user_id,
                "legal_rate": new_legal_rate,
                "legal_rate_first_try": new_legal_rate_first_try,
                "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M"),
            }
            leaderboard.append(entry)
            save_leaderboard(leaderboard)
            update_message = "New entry added to leaderboard!"
        else:
            # Existing model - only update if improved
            old_legal_rate = entry.get("legal_rate", 0)
            if new_legal_rate > old_legal_rate:
                entry.update({
                    "user_id": user_id,
                    "legal_rate": new_legal_rate,
                    "legal_rate_first_try": new_legal_rate_first_try,
                    "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M"),
                })
                save_leaderboard(leaderboard)
                update_message = f"Improved! Previous: {old_legal_rate*100:.1f}% → New: {new_legal_rate*100:.1f}%"
            else:
                update_message = f"ℹNo improvement. Current best: {old_legal_rate*100:.1f}%, This run: {new_legal_rate*100:.1f}%"
        
        progress(1.0, desc="Done!")
        
        return f"""
## Legal Move Evaluation for {model_id.split('/')[-1]}

| Metric | Value |
|--------|-------|
| **Positions Tested** | {results['total_positions']} |
| **Legal (1st try)** | {results['legal_first_try']} ({results['legal_rate_first_try']*100:.1f}%) |
| **Legal (with retries)** | {results['legal_first_try'] + results['legal_with_retry']} ({results['legal_rate_with_retry']*100:.1f}%) |
| **Always Illegal** | {results['illegal_all_retries']} ({results['illegal_rate']*100:.1f}%) |

### Leaderboard Update
{update_message}

### Interpretation
- **>90% legal rate**: Great! Model has learned chess rules well.
- **70-90% legal rate**: Decent, but room for improvement.
- **<70% legal rate**: Model struggles with legal move generation.
"""
        
    except Exception as e:
        return f"Evaluation failed: {str(e)}"


# def evaluate_winrate(
#     model_id: str,
#     stockfish_level: str,
#     n_games: int,
#     progress: gr.Progress = gr.Progress(),
# ) -> str:
#     """Evaluate a model's win rate against Stockfish."""
#     try:
#         import sys
#         sys.path.insert(0, str(Path(__file__).parent))
#         
#         from src.evaluate import ChessEvaluator, load_model_from_hub
#         
#         progress(0, desc="Loading model...")
#         model, tokenizer = load_model_from_hub(model_id)
#         
#         progress(0.1, desc="Setting up Stockfish...")
#         level = STOCKFISH_LEVELS.get(stockfish_level, 1)
#         evaluator = ChessEvaluator(
#             model=model,
#             tokenizer=tokenizer,
#             stockfish_level=level,
#         )
#         
#         progress(0.2, desc=f"Playing {n_games} games...")
#         results = evaluator.evaluate(n_games=n_games, verbose=False)
#         
#         # Update leaderboard
#         leaderboard = load_leaderboard()
#         entry = next((e for e in leaderboard if e["model_id"] == model_id), None)
#         if entry is None:
#             entry = {"model_id": model_id}
#             leaderboard.append(entry)
#         
#         entry.update({
#             "elo": results.get("estimated_elo", 1000),
#             "win_rate": results.get("win_rate", 0),
#             "games_played": entry.get("games_played", 0) + n_games,
#             "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M"),
#         })
#         
#         save_leaderboard(leaderboard)
#         progress(1.0, desc="Done!")
#         
#         return f"""
# ## Win Rate Evaluation for {model_id.split('/')[-1]}
# 
# | Metric | Value |
# |--------|-------|
# | **Estimated ELO** | {results.get('estimated_elo', 'N/A'):.0f} |
# | **Win Rate** | {results.get('win_rate', 0)*100:.1f}% |
# | **Draw Rate** | {results.get('draw_rate', 0)*100:.1f}% |
# | **Loss Rate** | {results.get('loss_rate', 0)*100:.1f}% |
# | **Avg Game Length** | {results.get('avg_game_length', 0):.1f} moves |
# | **Illegal Move Rate** | {results.get('illegal_move_rate', 0)*100:.2f}% |
# 
# Games played: {n_games} against Stockfish {stockfish_level}
# """
#         
#     except Exception as e:
#         return f"Evaluation failed: {str(e)}"


# def evaluate_model(
#     model_id: str,
#     stockfish_level: str,
#     n_games: int,
#     progress: gr.Progress = gr.Progress(),
# ) -> str:
#     """Evaluate a model against Stockfish."""
#     try:
#         # Import evaluation code
#         import sys
#         sys.path.insert(0, str(Path(__file__).parent))
#         
#         from src.evaluate import ChessEvaluator, load_model_from_hub
#         
#         progress(0, desc="Loading model...")
#         model, tokenizer = load_model_from_hub(model_id)
#         
#         progress(0.1, desc="Setting up Stockfish...")
#         level = STOCKFISH_LEVELS.get(stockfish_level, 1)
#         evaluator = ChessEvaluator(
#             model=model,
#             tokenizer=tokenizer,
#             stockfish_level=level,
#         )
#         
#         progress(0.2, desc=f"Playing {n_games} games...")
#         results = evaluator.evaluate(n_games=n_games, verbose=False)
#         
#         # Update leaderboard
#         leaderboard = load_leaderboard()
#         
#         # Find or create entry
#         entry = next((e for e in leaderboard if e["model_id"] == model_id), None)
#         if entry is None:
#             entry = {"model_id": model_id}
#             leaderboard.append(entry)
#         
#         entry.update({
#             "elo": results.get("estimated_elo", 1000),
#             "win_rate": results.get("win_rate", 0),
#             "games_played": entry.get("games_played", 0) + n_games,
#             "illegal_rate": results.get("illegal_move_rate", 0),
#             "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M"),
#         })
#         
#         save_leaderboard(leaderboard)
#         
#         progress(1.0, desc="Done!")
#         
#         return f"""
# ## Evaluation Results for {model_id.split('/')[-1]}
# 
# | Metric | Value |
# |--------|-------|
# | **Estimated ELO** | {results.get('estimated_elo', 'N/A'):.0f} |
# | **Win Rate** | {results.get('win_rate', 0)*100:.1f}% |
# | **Draw Rate** | {results.get('draw_rate', 0)*100:.1f}% |
# | **Loss Rate** | {results.get('loss_rate', 0)*100:.1f}% |
# | **Avg Game Length** | {results.get('avg_game_length', 0):.1f} moves |
# | **Illegal Move Rate** | {results.get('illegal_move_rate', 0)*100:.2f}% |
# 
# Games played: {n_games} against Stockfish {stockfish_level}
# """
#         
#     except Exception as e:
#         return f"Evaluation failed: {str(e)}"


def refresh_leaderboard() -> str:
    """Refresh and return the leaderboard HTML."""
    return format_leaderboard_html(load_leaderboard())


# Build Gradio Interface
with gr.Blocks(
    title="Play Chess like a Honey Bee",
    theme=gr.themes.Soft(),
) as demo:
    gr.Markdown("""
    # 🐝 Play Chess like a Honey Bee
    
    Welcome to the Chess Challenge! The goal is to train a language model to play chess,
    under a strict constraint: **less than 1M parameters!**
    
    This is approximately the number of neurons of a honey bee 🐝
    """)
    
    with gr.Tabs():
        # Submission Guide Tab
        with gr.TabItem("How to Submit"):
            gr.Markdown(f"""
            ### Submitting Your Model
                        
            The goal is to create a chess-playing language model with **under 1 million parameters**, which is roughly the number of neurons in a honey bee's brain.
            At this scale, efficiency and clever architecture choices are key! We are not targetting superhuman performance, but rather exploring how well small models can learn the rules of chess, the goal being (only) to play **legal moves**.
            
            0. **Clone this repository**: 
                ```bash
                git clone https://huggingface.co/spaces/LLM-course/Chess1MChallenge
                ```
                and check the `TEMPLATE_README.md` for detailed instructions.
                        
            1. **Train your model**
            
            2. **Push to Hugging Face Hub** using the `submit.py` script provided in the template to make sure that your model is registered correctly.
            
            3. **Verify your submission** by checking the model page on Hugging Face
            
            4. **Run evaluations**:            
            ### Requirements
            
            - Model must be under **1M parameters**
            - Model must use the `ChessConfig` and `ChessForCausalLM` classes
            - Include the tokenizer with your submission
            
            ### Tips for Better Performance
            
            - Experiment with different architectures (layers, heads, dimensions)
            - Try weight tying to save parameters
            """)
        
        # Interactive Demo Tab (commented out for now)
        # with gr.TabItem("🎮 Interactive Demo"):
        #     gr.Markdown("### Test a Model")
        #     
        #     with gr.Row():
        #         with gr.Column(scale=1):
        #             with gr.Row():
        #                 model_dropdown = gr.Dropdown(
        #                     choices=get_available_models(),
        #                     label="Select Model",
        #                     value=None,
        #                     scale=4,
        #                 )
        #                 refresh_models_btn = gr.Button("🔄", scale=1)
        #             temperature_slider = gr.Slider(
        #                 minimum=0.1,
        #                 maximum=2.0,
        #                 value=0.7,
        #                 step=0.1,
        #                 label="Temperature",
        #             )
        #             
        #             with gr.Row():
        #                 play_btn = gr.Button("Model Move", variant="primary")
        #                 reset_btn = gr.Button("Reset")
        #             
        #             status_text = gr.Textbox(label="Status", interactive=False)
        #         
        #         with gr.Column(scale=1):
        #             board_display = gr.HTML(value=render_board_svg())
        #     
        #     # Hidden state
        #     current_fen = gr.State("startpos")
        #     move_history = gr.State("")
        #     
        #     def refresh_models():
        #         return gr.update(choices=get_available_models())
        #     
        #     refresh_models_btn.click(
        #         refresh_models,
        #         outputs=[model_dropdown],
        #     )
        #     
        #     play_btn.click(
        #         play_move,
        #         inputs=[model_dropdown, current_fen, move_history, temperature_slider],
        #         outputs=[board_display, current_fen, move_history, status_text],
        #     )
        #     
        #     def reset_game():
        #         return render_board_svg(), "startpos", "", "Game reset!"
        #     
        #     reset_btn.click(
        #         reset_game,
        #         outputs=[board_display, current_fen, move_history, status_text],
        #     )
        
        # Legal Move Evaluation Tab
        with gr.TabItem("Legal Move Eval"):
            gr.Markdown("""
            ### Phase 1: Legal Move Evaluation
            
            Test if your model can generate **legal chess moves** in random positions.
            
            - Tests the model on random board positions
            - Measures how often it generates legal moves
            """)
            
            with gr.Row():
                legal_model = gr.Dropdown(
                    choices=get_available_models(),
                    label="Model to Evaluate",
                )
                refresh_legal_models_btn = gr.Button("🔄", scale=0, min_width=40)
            
            def refresh_legal_models():
                return gr.update(choices=get_available_models())
            
            refresh_legal_models_btn.click(
                refresh_legal_models,
                outputs=[legal_model],
            )
            
            legal_btn = gr.Button("Run Legal Move Evaluation", variant="primary")
            legal_results = gr.Markdown()
            
            legal_btn.click(
                evaluate_legal_moves,
                inputs=[legal_model],
                outputs=legal_results,
            )
        
        # Win Rate Evaluation Tab (commented out for now)
        # with gr.TabItem("🏆 Win Rate Eval"):
        #     gr.Markdown("""
        #     ### Phase 2: Win Rate Evaluation
        #     
        #     Play full games against Stockfish and measure win rate.
        #     This evaluation computes your model's **ELO rating**.
        #     
        #     - Plays complete games against Stockfish
        #     - Measures win/draw/loss rates
        #     - Estimates ELO rating
        #     """)
        #     
        #     with gr.Row():
        #         eval_model = gr.Dropdown(
        #             choices=get_available_models(),
        #             label="Model to Evaluate",
        #         )
        #         eval_level = gr.Dropdown(
        #             choices=list(STOCKFISH_LEVELS.keys()),
        #             value="Easy (Level 1)",
        #             label="Stockfish Level",
        #         )
        #         eval_games = gr.Slider(
        #             minimum=10,
        #             maximum=100,
        #             value=50,
        #             step=10,
        #             label="Number of Games",
        #         )
        #     
        #     eval_btn = gr.Button("Run Win Rate Evaluation", variant="primary")
        #     eval_results = gr.Markdown()
        #     
        #     eval_btn.click(
        #         evaluate_winrate,
        #         inputs=[eval_model, eval_level, eval_games],
        #         outputs=eval_results,
        #     )
        
        # Leaderboard Tab (moved to the end)
        with gr.TabItem("🏆 Leaderboard"):
            gr.Markdown("### Current Rankings")
            leaderboard_html = gr.HTML(value=format_leaderboard_html(load_leaderboard()))
            refresh_btn = gr.Button("Refresh Leaderboard")
            refresh_btn.click(refresh_leaderboard, outputs=leaderboard_html)


if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860)
