"""
Utility functions for the Chess Challenge.

This module provides helper functions for:
- Parameter counting and budget analysis
- Model registration with Hugging Face
- Move validation with python-chess
"""

from __future__ import annotations

from typing import Dict, Optional, TYPE_CHECKING

import torch.nn as nn

if TYPE_CHECKING:
    from src.model import ChessConfig


def count_parameters(model: nn.Module, trainable_only: bool = True) -> int:
    """
    Count the number of parameters in a model.
    
    Args:
        model: The PyTorch model.
        trainable_only: If True, only count trainable parameters.
    
    Returns:
        Total number of parameters.
    """
    if trainable_only:
        return sum(p.numel() for p in model.parameters() if p.requires_grad)
    return sum(p.numel() for p in model.parameters())


def count_parameters_by_component(model: nn.Module) -> Dict[str, int]:
    """
    Count parameters broken down by model component.
    
    Args:
        model: The PyTorch model.
    
    Returns:
        Dictionary mapping component names to parameter counts.
    """
    counts = {}
    for name, module in model.named_modules():
        if len(list(module.children())) == 0:  # Leaf module
            param_count = sum(p.numel() for p in module.parameters(recurse=False))
            if param_count > 0:
                counts[name] = param_count
    return counts


def estimate_parameters(config: "ChessConfig") -> Dict[str, int]:
    """
    Estimate the parameter count for a given configuration.
    
    This is useful for planning your architecture before building the model.
    
    Args:
        config: Model configuration.
    
    Returns:
        Dictionary with estimated parameter counts by component.
    """
    V = config.vocab_size
    d = config.n_embd
    L = config.n_layer
    n_ctx = config.n_ctx
    n_inner = config.n_inner
    
    estimates = {
        "token_embeddings": V * d,
        "position_embeddings": n_ctx * d,
        "attention_qkv_per_layer": 3 * d * d,
        "attention_proj_per_layer": d * d,
        "ffn_per_layer": 2 * d * n_inner,
        "layernorm_per_layer": 4 * d,  # 2 LayerNorms, each with weight and bias
        "final_layernorm": 2 * d,
    }
    
    # Calculate totals
    per_layer = (
        estimates["attention_qkv_per_layer"] +
        estimates["attention_proj_per_layer"] +
        estimates["ffn_per_layer"] +
        estimates["layernorm_per_layer"]
    )
    
    estimates["total_transformer_layers"] = L * per_layer
    
    # LM head (tied with embeddings by default)
    if config.tie_weights:
        estimates["lm_head"] = 0
        estimates["lm_head_note"] = "Tied with token embeddings"
    else:
        estimates["lm_head"] = V * d
    
    # Grand total
    estimates["total"] = (
        estimates["token_embeddings"] +
        estimates["position_embeddings"] +
        estimates["total_transformer_layers"] +
        estimates["final_layernorm"] +
        estimates["lm_head"]
    )
    
    return estimates


def print_parameter_budget(config: "ChessConfig", limit: int = 1_000_000) -> None:
    """
    Print a formatted parameter budget analysis.
    
    Args:
        config: Model configuration.
        limit: Parameter limit to compare against.
    """
    estimates = estimate_parameters(config)
    
    print("=" * 60)
    print("PARAMETER BUDGET ANALYSIS")
    print("=" * 60)
    print(f"\nConfiguration:")
    print(f"  vocab_size (V) = {config.vocab_size}")
    print(f"  n_embd (d)     = {config.n_embd}")
    print(f"  n_layer (L)    = {config.n_layer}")
    print(f"  n_head         = {config.n_head}")
    print(f"  n_ctx          = {config.n_ctx}")
    print(f"  n_inner        = {config.n_inner}")
    print(f"  tie_weights    = {config.tie_weights}")
    
    print(f"\nParameter Breakdown:")
    print(f"  Token Embeddings:    {estimates['token_embeddings']:>10,}")
    print(f"  Position Embeddings: {estimates['position_embeddings']:>10,}")
    print(f"  Transformer Layers:  {estimates['total_transformer_layers']:>10,}")
    print(f"  Final LayerNorm:     {estimates['final_layernorm']:>10,}")
    
    if config.tie_weights:
        print(f"  LM Head:             {'(tied)':>10}")
    else:
        print(f"  LM Head:             {estimates['lm_head']:>10,}")
    
    print(f"  " + "-" * 30)
    print(f"  TOTAL:               {estimates['total']:>10,}")
    
    print(f"\nBudget Status:")
    print(f"  Limit:    {limit:>10,}")
    print(f"  Used:     {estimates['total']:>10,}")
    print(f"  Remaining:{limit - estimates['total']:>10,}")
    
    if estimates['total'] <= limit:
        print(f"\n Within budget! ({estimates['total'] / limit * 100:.1f}% used)")
    else:
        print(f"\n OVER BUDGET by {estimates['total'] - limit:,} parameters!")
    
    print("=" * 60)


def validate_move_with_chess(move: str, board_fen: Optional[str] = None) -> bool:
    """
    Validate a move using python-chess.
    
    This function converts the dataset's extended UCI format to standard UCI
    and validates it against the current board state.
    
    Args:
        move: Move in extended UCI format (e.g., "WPe2e4", "BNg8f6(x)").
        board_fen: FEN string of the current board state (optional).
    
    Returns:
        True if the move is legal, False otherwise.
    """
    try:
        import chess
    except ImportError:
        raise ImportError("python-chess is required for move validation. "
                         "Install it with: pip install python-chess")
    
    # Parse the extended UCI format
    # Format: [W|B][Piece][from_sq][to_sq][suffix]
    # Example: WPe2e4, BNg8f6(x), WKe1g1(o)
    
    if len(move) < 6:
        return False
    
    # Extract components
    color = move[0]  # W or B
    piece = move[1]  # P, N, B, R, Q, K
    from_sq = move[2:4]  # e.g., "e2"
    to_sq = move[4:6]  # e.g., "e4"
    
    # Check for promotion
    promotion = None
    if "=" in move:
        promo_idx = move.index("=")
        promotion = move[promo_idx + 1].lower()
    
    # Create board
    board = chess.Board(board_fen) if board_fen else chess.Board()
    
    # Build UCI move string
    uci_move = from_sq + to_sq
    if promotion:
        uci_move += promotion
    
    try:
        move_obj = chess.Move.from_uci(uci_move)
        return move_obj in board.legal_moves
    except (ValueError, chess.InvalidMoveError):
        return False


def convert_extended_uci_to_uci(move: str) -> str:
    """
    Convert extended UCI format to standard UCI format.
    
    Args:
        move: Move in extended UCI format (e.g., "WPe2e4").
    
    Returns:
        Move in standard UCI format (e.g., "e2e4").
    """
    if len(move) < 6:
        return move
    
    # Extract squares
    from_sq = move[2:4]
    to_sq = move[4:6]
    
    # Check for promotion
    promotion = ""
    if "=" in move:
        promo_idx = move.index("=")
        promotion = move[promo_idx + 1].lower()
    
    return from_sq + to_sq + promotion


def convert_uci_to_extended(
    uci_move: str,
    board_fen: str,
) -> str:
    """
    Convert standard UCI format to extended UCI format.
    
    Args:
        uci_move: Move in standard UCI format (e.g., "e2e4").
        board_fen: FEN string of the current board state.
    
    Returns:
        Move in extended UCI format (e.g., "WPe2e4").
    """
    try:
        import chess
    except ImportError:
        raise ImportError("python-chess is required for move conversion.")
    
    board = chess.Board(board_fen)
    move = chess.Move.from_uci(uci_move)
    
    # Get color
    color = "W" if board.turn == chess.WHITE else "B"
    
    # Get piece
    piece = board.piece_at(move.from_square)
    piece_letter = piece.symbol().upper() if piece else "P"
    
    # Build extended UCI
    from_sq = chess.square_name(move.from_square)
    to_sq = chess.square_name(move.to_square)
    
    result = f"{color}{piece_letter}{from_sq}{to_sq}"
    
    # Add promotion
    if move.promotion:
        result += f"={chess.piece_symbol(move.promotion).upper()}"
    
    # Add suffix for captures
    if board.is_capture(move):
        result += "(x)"
    
    # Add suffix for check/checkmate
    board.push(move)
    if board.is_checkmate():
        if "(x)" in result:
            result = result.replace("(x)", "(x+*)")
        else:
            result += "(+*)"
    elif board.is_check():
        if "(x)" in result:
            result = result.replace("(x)", "(x+)")
        else:
            result += "(+)"
    board.pop()
    
    # Handle castling notation
    if board.is_castling(move):
        if move.to_square in [chess.G1, chess.G8]:  # Kingside
            result = result.replace("(x)", "").replace("(+)", "") + "(o)"
        else:  # Queenside
            result = result.replace("(x)", "").replace("(+)", "") + "(O)"
    
    return result
