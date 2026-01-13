"""
Data loading utilities for the Chess Challenge.

This module provides functions to load and process chess game data
from the Lichess dataset on Hugging Face.
"""

from __future__ import annotations

from typing import Dict, Iterator, List, Optional

import torch
from torch.utils.data import Dataset


class ChessDataset(Dataset):
    """
    PyTorch Dataset for chess games.
    
    This dataset loads games from a Hugging Face dataset and prepares
    them for language modeling training.
    
    Each game is tokenized and truncated/padded to max_length.
    The labels are shifted by one position for next-token prediction.
    
    Example:
        >>> from src.tokenizer import ChessTokenizer
        >>> tokenizer = ChessTokenizer.build_vocab_from_dataset()
        >>> dataset = ChessDataset(tokenizer, max_length=256)
        >>> sample = dataset[0]
        >>> print(sample["input_ids"].shape)  # (256,)
    """
    
    def __init__(
        self,
        tokenizer,
        dataset_name: str = "dlouapre/lichess_2025-01_1M",
        split: str = "train",
        column: str = "text",
        max_length: int = 256,
        max_samples: Optional[int] = None,
    ):
        """
        Initialize the chess dataset.
        
        Args:
            tokenizer: The chess tokenizer to use.
            dataset_name: Name of the dataset on Hugging Face Hub.
            split: Dataset split to use.
            column: Column containing the game strings.
            max_length: Maximum sequence length.
            max_samples: Maximum number of samples to load.
        """
        from datasets import load_dataset
        
        self.tokenizer = tokenizer
        self.max_length = max_length
        self.column = column
        
        # Load dataset
        dataset = load_dataset(dataset_name, split=split)
        
        if max_samples is not None:
            dataset = dataset.select(range(min(max_samples, len(dataset))))
        
        self.data = dataset
    
    def __len__(self) -> int:
        return len(self.data)
    
    def __getitem__(self, idx: int) -> Dict[str, torch.Tensor]:
        game = self.data[idx][self.column]
        
        # Prepend BOS token for proper language modeling
        game_with_bos = self.tokenizer.bos_token + " " + game
        
        # Tokenize
        encoding = self.tokenizer(
            game_with_bos,
            truncation=True,
            max_length=self.max_length,
            padding="max_length",
            return_tensors="pt",
        )
        
        # Squeeze batch dimension
        input_ids = encoding["input_ids"].squeeze(0)
        attention_mask = encoding["attention_mask"].squeeze(0)
        
        # Labels are the same as input_ids (model will shift internally)
        labels = input_ids.clone()
        
        # Set padding tokens to -100 to ignore in loss
        labels[attention_mask == 0] = -100
        
        return {
            "input_ids": input_ids,
            "attention_mask": attention_mask,
            "labels": labels,
        }


class ChessDataCollator:
    """
    Data collator for chess games.
    
    This collator pads sequences to the same length within a batch
    and creates the appropriate attention masks.
    """
    
    def __init__(self, tokenizer, max_length: int = 256):
        self.tokenizer = tokenizer
        self.max_length = max_length
    
    def __call__(self, features: List[Dict]) -> Dict[str, torch.Tensor]:
        # Stack tensors
        input_ids = torch.stack([f["input_ids"] for f in features])
        attention_mask = torch.stack([f["attention_mask"] for f in features])
        labels = torch.stack([f["labels"] for f in features])
        
        return {
            "input_ids": input_ids,
            "attention_mask": attention_mask,
            "labels": labels,
        }


def create_train_val_datasets(
    tokenizer,
    dataset_name: str = "dlouapre/lichess_2025-01_1M",
    max_length: int = 256,
    train_samples: Optional[int] = None,
    val_samples: int = 5000,
    val_ratio: float = 0.05,
):
    """
    Create training and validation datasets.
    
    Args:
        tokenizer: The chess tokenizer.
        dataset_name: Name of the dataset.
        max_length: Maximum sequence length.
        train_samples: Maximum training samples (None for all).
        val_samples: Number of validation samples.
        val_ratio: Ratio of validation samples (used if train_samples is None).
    
    Returns:
        Tuple of (train_dataset, val_dataset).
    """
    from datasets import load_dataset
    
    # Load full dataset
    full_dataset = load_dataset(dataset_name, split="train")
    
    # Determine split sizes
    total = len(full_dataset)
    
    if train_samples is not None:
        n_train = min(train_samples, total - val_samples)
    else:
        n_train = int(total * (1 - val_ratio))
    
    n_val = min(val_samples, total - n_train)
    
    # Split dataset
    train_data = full_dataset.select(range(n_train))
    val_data = full_dataset.select(range(n_train, n_train + n_val))
    
    # Create dataset objects
    train_dataset = ChessDataset(
        tokenizer=tokenizer,
        dataset_name=dataset_name,
        max_length=max_length,
    )
    train_dataset.data = train_data
    
    val_dataset = ChessDataset(
        tokenizer=tokenizer,
        dataset_name=dataset_name,
        max_length=max_length,
    )
    val_dataset.data = val_data
    
    return train_dataset, val_dataset


def stream_games(
    dataset_name: str = "dlouapre/lichess_2025-01_1M",
    split: str = "train",
    column: str = "text",
) -> Iterator[str]:
    """
    Stream games from the dataset for memory-efficient processing.
    
    Args:
        dataset_name: Name of the dataset on Hugging Face Hub.
        split: Dataset split to use.
        column: Column containing the game strings.
    
    Yields:
        Game strings one at a time.
    """
    from datasets import load_dataset
    
    dataset = load_dataset(dataset_name, split=split, streaming=True)
    
    for example in dataset:
        yield example[column]


def analyze_dataset_statistics(
    dataset_name: str = "dlouapre/lichess_2025-01_1M",
    max_samples: int = 10000,
) -> Dict:
    """
    Analyze statistics of the chess dataset.
    
    Args:
        dataset_name: Name of the dataset.
        max_samples: Maximum number of samples to analyze.
    
    Returns:
        Dictionary containing dataset statistics.
    """
    from collections import Counter
    from datasets import load_dataset
    
    dataset = load_dataset(dataset_name, split="train")
    dataset = dataset.select(range(min(max_samples, len(dataset))))
    
    game_lengths = []
    move_counts = Counter()
    opening_moves = Counter()
    
    for example in dataset:
        moves = example["text"].strip().split()
        game_lengths.append(len(moves))
        move_counts.update(moves)
        
        # Track common openings (first 4 moves)
        if len(moves) >= 4:
            opening = " ".join(moves[:4])
            opening_moves[opening] += 1
    
    return {
        "total_games": len(dataset),
        "avg_game_length": sum(game_lengths) / len(game_lengths),
        "min_game_length": min(game_lengths),
        "max_game_length": max(game_lengths),
        "unique_moves": len(move_counts),
        "most_common_moves": move_counts.most_common(20),
        "most_common_openings": opening_moves.most_common(10),
    }
