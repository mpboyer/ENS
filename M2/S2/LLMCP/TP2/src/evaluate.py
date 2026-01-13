"""
Evaluation script for the Chess Challenge.

This script evaluates a trained chess model by playing games against
Stockfish and computing ELO ratings.
"""

from __future__ import annotations

import argparse
import random
from dataclasses import dataclass
from typing import List, Optional, Tuple

import torch


@dataclass
class GameResult:
    """Result of a single game."""
    moves: List[str]
    result: str  # "1-0", "0-1", or "1/2-1/2"
    model_color: str  # "white" or "black"
    termination: str  # "checkmate", "stalemate", "illegal_move", "max_moves", etc.
    illegal_move_count: int


class ChessEvaluator:
    """
    Evaluator for chess models.
    
    This class handles playing games between a trained model and Stockfish,
    tracking results, and computing ELO ratings.
    """
    
    def __init__(
        self,
        model,
        tokenizer,
        stockfish_path: Optional[str] = None,
        stockfish_level: int = 1,
        max_retries: int = 3,
        device: str = "cuda" if torch.cuda.is_available() else "cpu",
    ):
        """
        Initialize the evaluator.
        
        Args:
            model: The trained chess model.
            tokenizer: The chess tokenizer.
            stockfish_path: Path to Stockfish executable.
            stockfish_level: Stockfish skill level (0-20).
            max_retries: Maximum retries for illegal moves.
            device: Device to run the model on.
        """
        self.model = model.to(device)
        self.tokenizer = tokenizer
        self.max_retries = max_retries
        self.device = device
        
        # Initialize Stockfish
        try:
            import chess
            import chess.engine
            
            self.chess = chess
            
            if stockfish_path is None:
                # Try common paths
                import shutil
                stockfish_path = shutil.which("stockfish")
            
            if stockfish_path:
                self.engine = chess.engine.SimpleEngine.popen_uci(stockfish_path)
                self.engine.configure({"Skill Level": stockfish_level})
            else:
                print("WARNING: Stockfish not found. Install it for full evaluation.")
                self.engine = None
                
        except ImportError:
            raise ImportError(
                "python-chess is required for evaluation. "
                "Install it with: pip install python-chess"
            )
    
    def __del__(self):
        """Clean up Stockfish engine."""
        if hasattr(self, 'engine') and self.engine:
            self.engine.quit()
    
    def _convert_board_to_moves(self, board) -> str:
        """Convert board move history to model input format."""
        moves = []
        temp_board = self.chess.Board()
        
        for move in board.move_stack:
            # Get piece and color
            color = "W" if temp_board.turn == self.chess.WHITE else "B"
            piece = temp_board.piece_at(move.from_square)
            piece_letter = piece.symbol().upper() if piece else "P"
            
            # Get squares
            from_sq = self.chess.square_name(move.from_square)
            to_sq = self.chess.square_name(move.to_square)
            
            move_str = f"{color}{piece_letter}{from_sq}{to_sq}"
            
            # Add promotion
            if move.promotion:
                move_str += f"={self.chess.piece_symbol(move.promotion).upper()}"
            
            # Add capture suffix
            if temp_board.is_capture(move):
                move_str += "(x)"
            
            # Add check/checkmate suffix
            temp_board.push(move)
            if temp_board.is_checkmate():
                move_str = move_str.replace("(x)", "(x+*)") if "(x)" in move_str else move_str + "(+*)"
            elif temp_board.is_check():
                move_str = move_str.replace("(x)", "(x+)") if "(x)" in move_str else move_str + "(+)"
            
            # Handle castling
            if piece_letter == "K" and abs(ord(from_sq[0]) - ord(to_sq[0])) > 1:
                if to_sq[0] == 'g':  # Kingside
                    move_str = move_str.split("(")[0] + "(o)"
                else:  # Queenside
                    move_str = move_str.split("(")[0] + "(O)"
            
            moves.append(move_str)
        
        return " ".join(moves)
    
    def _get_model_move(
        self,
        board,
        temperature: float = 0.7,
        top_k: int = 10,
    ) -> Tuple[Optional[str], int]:
        """
        Get the model's next move prediction.
        
        Returns:
            Tuple of (UCI move string, number of retries used).
        """
        self.model.eval()
        
        # Convert board to input format
        moves_str = self._convert_board_to_moves(board)
        
        # Add BOS token if no moves yet
        if not moves_str:
            input_text = self.tokenizer.bos_token
        else:
            input_text = self.tokenizer.bos_token + " " + moves_str
        
        # Tokenize
        inputs = self.tokenizer(
            input_text,
            return_tensors="pt",
            truncation=True,
            max_length=self.model.config.n_ctx - 1,
        ).to(self.device)
        
        # Try to generate a legal move
        for retry in range(self.max_retries):
            with torch.no_grad():
                outputs = self.model(**inputs)
                logits = outputs.logits[:, -1, :] / temperature
                
                # Apply top-k filtering
                if top_k > 0:
                    indices_to_remove = logits < torch.topk(logits, top_k)[0][..., -1, None]
                    logits[indices_to_remove] = float("-inf")
                
                # Sample
                probs = torch.softmax(logits, dim=-1)
                next_token = torch.multinomial(probs, num_samples=1)
            
            # Decode the move
            move_token = self.tokenizer.decode(next_token[0])
            
            # Convert to UCI
            if len(move_token) >= 6:
                uci_move = move_token[2:4] + move_token[4:6]
                
                # Handle promotion
                if "=" in move_token:
                    promo_idx = move_token.index("=")
                    uci_move += move_token[promo_idx + 1].lower()
                
                try:
                    move = self.chess.Move.from_uci(uci_move)
                    if move in board.legal_moves:
                        return uci_move, retry
                except (ValueError, self.chess.InvalidMoveError):
                    pass
            
            # Mask out the tried token for next retry
            logits[0, next_token[0]] = float("-inf")
        
        return None, self.max_retries
    
    def _get_stockfish_move(self, board, time_limit: float = 0.1) -> str:
        """Get Stockfish's move."""
        if self.engine is None:
            raise RuntimeError("Stockfish engine not initialized")
        
        result = self.engine.play(board, self.chess.engine.Limit(time=time_limit))
        return result.move.uci()
    
    def play_game(
        self,
        model_color: str = "white",
        max_moves: int = 200,
        temperature: float = 0.7,
    ) -> GameResult:
        """
        Play a single game between the model and Stockfish.
        
        Args:
            model_color: "white" or "black".
            max_moves: Maximum number of moves before draw.
            temperature: Sampling temperature for model.
        
        Returns:
            GameResult with the game details.
        """
        board = self.chess.Board()
        moves = []
        illegal_move_count = 0
        
        model_is_white = model_color == "white"
        
        while not board.is_game_over() and len(moves) < max_moves:
            is_model_turn = (board.turn == self.chess.WHITE) == model_is_white
            
            if is_model_turn:
                # Model's turn
                uci_move, retries = self._get_model_move(board, temperature)
                illegal_move_count += retries
                
                if uci_move is None:
                    # Model couldn't find a legal move
                    return GameResult(
                        moves=moves,
                        result="0-1" if model_is_white else "1-0",
                        model_color=model_color,
                        termination="illegal_move",
                        illegal_move_count=illegal_move_count + 1,
                    )
                
                move = self.chess.Move.from_uci(uci_move)
            else:
                # Stockfish's turn
                if self.engine:
                    uci_move = self._get_stockfish_move(board)
                    move = self.chess.Move.from_uci(uci_move)
                else:
                    # Random move if no engine
                    move = random.choice(list(board.legal_moves))
            
            board.push(move)
            moves.append(move.uci())
        
        # Determine result
        if board.is_checkmate():
            if board.turn == self.chess.WHITE:
                result = "0-1"  # Black wins
            else:
                result = "1-0"  # White wins
            termination = "checkmate"
        elif board.is_stalemate():
            result = "1/2-1/2"
            termination = "stalemate"
        elif board.is_insufficient_material():
            result = "1/2-1/2"
            termination = "insufficient_material"
        elif board.can_claim_draw():
            result = "1/2-1/2"
            termination = "draw_claim"
        elif len(moves) >= max_moves:
            result = "1/2-1/2"
            termination = "max_moves"
        else:
            result = "1/2-1/2"
            termination = "unknown"
        
        return GameResult(
            moves=moves,
            result=result,
            model_color=model_color,
            termination=termination,
            illegal_move_count=illegal_move_count,
        )
    
    def evaluate_legal_moves(
        self,
        n_positions: int = 1000,
        temperature: float = 0.7,
        verbose: bool = True,
    ) -> dict:
        """
        Evaluate the model's ability to generate legal moves.
        
        This evaluation only checks if the model generates legal moves,
        without playing full games. Useful as a first-pass evaluation.
        
        Args:
            n_positions: Number of positions to test.
            temperature: Sampling temperature.
            verbose: Whether to print progress.
        
        Returns:
            Dictionary with legal move statistics.
        """
        results = {
            "total_positions": 0,
            "legal_first_try": 0,
            "legal_with_retry": 0,
            "illegal_all_retries": 0,
            "positions": [],
        }
        
        # Generate random positions by playing random moves
        for i in range(n_positions):
            board = self.chess.Board()
            
            # Play random number of moves (5-40) to get varied positions
            n_random_moves = random.randint(5, 40)
            for _ in range(n_random_moves):
                if board.is_game_over():
                    break
                move = random.choice(list(board.legal_moves))
                board.push(move)
            
            if board.is_game_over():
                continue  # Skip terminal positions
            
            results["total_positions"] += 1
            
            # Test model's move generation
            uci_move, retries = self._get_model_move(board, temperature)
            
            position_result = {
                "fen": board.fen(),
                "move_number": len(board.move_stack),
                "legal": uci_move is not None,
                "retries": retries,
            }
            results["positions"].append(position_result)
            
            if uci_move is not None:
                if retries == 0:
                    results["legal_first_try"] += 1
                else:
                    results["legal_with_retry"] += 1
            else:
                results["illegal_all_retries"] += 1
            
            if verbose and (i + 1) % 100 == 0:
                legal_rate = (results["legal_first_try"] + results["legal_with_retry"]) / results["total_positions"]
                print(f"  Positions: {i + 1}/{n_positions} | Legal rate: {legal_rate:.1%}")
        
        # Calculate statistics
        total = results["total_positions"]
        if total > 0:
            results["legal_rate_first_try"] = results["legal_first_try"] / total
            results["legal_rate_with_retry"] = (results["legal_first_try"] + results["legal_with_retry"]) / total
            results["illegal_rate"] = results["illegal_all_retries"] / total
        else:
            results["legal_rate_first_try"] = 0
            results["legal_rate_with_retry"] = 0
            results["illegal_rate"] = 1
        
        return results
    
    def evaluate(
        self,
        n_games: int = 100,
        temperature: float = 0.7,
        verbose: bool = True,
    ) -> dict:
        """
        Run a full win-rate evaluation of the model against Stockfish.
        
        Args:
            n_games: Number of games to play.
            temperature: Sampling temperature.
            verbose: Whether to print progress.
        
        Returns:
            Dictionary with evaluation metrics.
        """
        results = {
            "wins": 0,
            "losses": 0,
            "draws": 0,
            "illegal_moves": 0,
            "total_moves": 0,
            "games": [],
        }
        
        for i in range(n_games):
            # Alternate colors
            model_color = "white" if i % 2 == 0 else "black"
            
            game = self.play_game(
                model_color=model_color,
                temperature=temperature,
            )
            
            results["games"].append(game)
            results["total_moves"] += len(game.moves)
            results["illegal_moves"] += game.illegal_move_count
            
            # Count result
            if game.result == "1/2-1/2":
                results["draws"] += 1
            elif (game.result == "1-0" and model_color == "white") or \
                 (game.result == "0-1" and model_color == "black"):
                results["wins"] += 1
            else:
                results["losses"] += 1
            
            if verbose and (i + 1) % 10 == 0:
                print(f"  Games: {i + 1}/{n_games} | "
                      f"W: {results['wins']} L: {results['losses']} D: {results['draws']}")
        
        # Calculate statistics
        total = results["wins"] + results["losses"] + results["draws"]
        results["win_rate"] = results["wins"] / total if total > 0 else 0
        results["draw_rate"] = results["draws"] / total if total > 0 else 0
        results["loss_rate"] = results["losses"] / total if total > 0 else 0

        total_attempts = results["total_moves"] + results["illegal_moves"]

        # Average length counts both legal moves and illegal attempts so early illegal terminations
        # don't show as near-zero length games.
        results["avg_game_length"] = total_attempts / total if total > 0 else 0

        # Illegal move rate: illegal attempts over total attempts
        results["illegal_move_rate"] = results["illegal_moves"] / total_attempts if total_attempts > 0 else 0
        
        # Estimate ELO (simplified)
        # Stockfish Level 1 is approximately 1350 ELO
        stockfish_elo = 1350
        if results["win_rate"] > 0 or results["loss_rate"] > 0:
            score = results["wins"] + 0.5 * results["draws"]
            expected = total * 0.5  # Expected score against equal opponent
            
            # Simple ELO estimation
            if score > 0:
                win_ratio = score / total
                if win_ratio > 0 and win_ratio < 1:
                    elo_diff = -400 * (1 - 2 * win_ratio) / (1 if win_ratio > 0.5 else -1)
                    results["estimated_elo"] = stockfish_elo + elo_diff
                else:
                    results["estimated_elo"] = stockfish_elo + (400 if win_ratio >= 1 else -400)
            else:
                results["estimated_elo"] = stockfish_elo - 400
        else:
            results["estimated_elo"] = None
        
        return results


def load_model_from_hub(model_id: str, device: str = "auto"):
    """
    Load a model from the Hugging Face Hub.
    
    Args:
        model_id: Model ID on Hugging Face Hub.
        device: Device to load the model on.
    
    Returns:
        Tuple of (model, tokenizer).
    """
    from transformers import AutoModelForCausalLM, AutoTokenizer
    
    # Import to register custom classes
    from src.model import ChessConfig, ChessForCausalLM
    
    tokenizer = AutoTokenizer.from_pretrained(model_id, trust_remote_code=True)
    model = AutoModelForCausalLM.from_pretrained(
        model_id,
        trust_remote_code=True,
        device_map=device,
    )
    
    return model, tokenizer


def main():
    """Main evaluation function."""
    parser = argparse.ArgumentParser(description="Evaluate a chess model")
    
    parser.add_argument(
        "--model_path", type=str, required=True,
        help="Path to the model or Hugging Face model ID"
    )
    parser.add_argument(
        "--mode", type=str, default="legal", choices=["legal", "winrate", "both"],
        help="Evaluation mode: 'legal' for legal move rate, 'winrate' for games, 'both' for both"
    )
    parser.add_argument(
        "--stockfish_path", type=str, default=None,
        help="Path to Stockfish executable"
    )
    parser.add_argument(
        "--stockfish_level", type=int, default=1,
        help="Stockfish skill level (0-20)"
    )
    parser.add_argument(
        "--n_positions", type=int, default=500,
        help="Number of positions for legal move evaluation"
    )
    parser.add_argument(
        "--n_games", type=int, default=100,
        help="Number of games to play for win rate evaluation"
    )
    parser.add_argument(
        "--temperature", type=float, default=0.7,
        help="Sampling temperature"
    )
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("CHESS CHALLENGE - EVALUATION")
    print("=" * 60)
    
    # Load model
    print(f"\nLoading model from: {args.model_path}")
    
    if "/" in args.model_path and not args.model_path.startswith("."):
        # Assume Hugging Face model ID
        model, tokenizer = load_model_from_hub(args.model_path)
    else:
        # Local path
        from transformers import AutoModelForCausalLM
        from src.tokenizer import ChessTokenizer
        from src.model import ChessConfig, ChessForCausalLM
        
        tokenizer = ChessTokenizer.from_pretrained(args.model_path)
        model = AutoModelForCausalLM.from_pretrained(args.model_path)
    
    # Create evaluator
    print(f"\nSetting up evaluator...")
    evaluator = ChessEvaluator(
        model=model,
        tokenizer=tokenizer,
        stockfish_path=args.stockfish_path,
        stockfish_level=args.stockfish_level,
    )
    
    # Run legal move evaluation
    if args.mode in ["legal", "both"]:
        print(f"\n" + "=" * 60)
        print("PHASE 1: LEGAL MOVE EVALUATION")
        print("=" * 60)
        print(f"Testing {args.n_positions} random positions...")
        
        legal_results = evaluator.evaluate_legal_moves(
            n_positions=args.n_positions,
            temperature=args.temperature,
            verbose=True,
        )
        
        print("\n" + "-" * 40)
        print("LEGAL MOVE RESULTS")
        print("-" * 40)
        print(f"  Positions tested:     {legal_results['total_positions']}")
        print(f"  Legal (1st try):      {legal_results['legal_first_try']} ({legal_results['legal_rate_first_try']:.1%})")
        print(f"  Legal (with retry):   {legal_results['legal_first_try'] + legal_results['legal_with_retry']} ({legal_results['legal_rate_with_retry']:.1%})")
        print(f"  Always illegal:       {legal_results['illegal_all_retries']} ({legal_results['illegal_rate']:.1%})")
    
    # Run win rate evaluation
    if args.mode in ["winrate", "both"]:
        print(f"\n" + "=" * 60)
        print("PHASE 2: WIN RATE EVALUATION")
        print("=" * 60)
        print(f"Playing {args.n_games} games against Stockfish (Level {args.stockfish_level})...")
        
        winrate_results = evaluator.evaluate(
            n_games=args.n_games,
            temperature=args.temperature,
            verbose=True,
        )
        
        print("\n" + "-" * 40)
        print("WIN RATE RESULTS")
        print("-" * 40)
        print(f"  Wins:   {winrate_results['wins']}")
        print(f"  Losses: {winrate_results['losses']}")
        print(f"  Draws:  {winrate_results['draws']}")
        print(f"\n  Win Rate:  {winrate_results['win_rate']:.1%}")
        print(f"  Draw Rate: {winrate_results['draw_rate']:.1%}")
        print(f"  Loss Rate: {winrate_results['loss_rate']:.1%}")
        print(f"\n  Avg Game Length: {winrate_results['avg_game_length']:.1f} moves")
        print(f"  Illegal Move Rate: {winrate_results['illegal_move_rate']:.2%}")
        
        if winrate_results["estimated_elo"]:
            print(f"\n  Estimated ELO: {winrate_results['estimated_elo']:.0f}")
    
    print("\n" + "=" * 60)
    print("EVALUATION COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    main()
