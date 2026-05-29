"""
NL2SQL Dataset Loaders

Provides standardized loading methods for importing and parsing benchmark datasets,
specifically Spider, Spider Realistic, and Spider SYN.
"""

import os
import json
import logging
from typing import List

from evaluation.metrics import BenchmarkCase

logger = logging.getLogger(__name__)

# Directory mapping for benchmark datasets
DATASETS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "datasets")

def load_dataset(dataset_name: str) -> List[BenchmarkCase]:
    """
    Loads and parses a specified benchmark dataset JSON file into a list of
    validated Pydantic BenchmarkCase objects.
    
    Args:
        dataset_name: The dataset identifier: 'spider', 'spider_realistic', or 'spider_syn'.
        
    Returns:
        A list of Pydantic BenchmarkCase models representing the test suite.
        
    Raises:
        ValueError: If the dataset name is invalid or the file is missing/corrupted.
    """
    valid_names = {
        "spider": "spider.json",
        "spider_realistic": "spider_realistic.json",
        "spider_syn": "spider_syn.json"
    }
    
    if dataset_name not in valid_names:
        raise ValueError(
            f"Invalid dataset name: '{dataset_name}'. "
            f"Supported datasets: {list(valid_names.keys())}"
        )
        
    file_name = valid_names[dataset_name]
    file_path = os.path.join(DATASETS_DIR, file_name)
    
    if not os.path.exists(file_path):
        raise FileNotFoundError(
            f"Benchmark dataset file not found at: {file_path}. "
            f"Ensure the dataset has been generated/seeded correctly."
        )
        
    logger.info(f"Loading benchmark dataset: {dataset_name} from {file_path}")
    
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            
        if not isinstance(data, list):
            raise ValueError(f"Invalid dataset format in {file_name}: expected a list of cases.")
            
        cases = []
        for index, item in enumerate(data):
            try:
                if hasattr(BenchmarkCase, "model_validate"):
                    case = BenchmarkCase.model_validate(item)
                else:
                    case = BenchmarkCase.parse_obj(item)
                cases.append(case)
            except Exception as item_err:
                logger.error(f"Failed to validate case at index {index} in {file_name}: {item_err}")
                raise item_err
                
        logger.info(f"Successfully loaded {len(cases)} benchmark cases for dataset '{dataset_name}'.")
        return cases
        
    except json.JSONDecodeError as jde:
        logger.error(f"Failed to parse JSON file {file_path}: {jde}")
        raise ValueError(f"Corrupted or invalid JSON dataset file: {jde}")
    except Exception as e:
        logger.exception(f"Unexpected error loading dataset '{dataset_name}': {e}")
        raise e
