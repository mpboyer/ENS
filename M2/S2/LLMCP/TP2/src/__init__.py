"""
Chess Challenge - LLM Training Exercise

Train a 1M parameter model to play chess using custom tokenizers and architectures.
"""

from src.tokenizer import ChessTokenizer
from src.model import ChessConfig, ChessForCausalLM
from src.utils import count_parameters, print_parameter_budget

__version__ = "0.1.0"
__all__ = [
    "ChessTokenizer",
    "ChessConfig", 
    "ChessForCausalLM",
    "count_parameters",
    "print_parameter_budget",
]
