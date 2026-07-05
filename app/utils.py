"""Utility helper functions for the application."""

from typing import Dict, Any

def clean_input_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """Replace empty or whitespace-only strings in input dictionary with None."""
    return {k: (None if (isinstance(v, str) and not v.strip()) else v) for k, v in data.items()}


def generate_sequential_code(model: Any, id_attr: str, prefix: str) -> str:
    """Generate the next sequential code for a model class based on its primary key id."""
    last = model.query.order_by(getattr(model, id_attr).desc()).first()
    next_num = (getattr(last, id_attr) + 1) if last else 1
    return f"{prefix}{next_num}"

