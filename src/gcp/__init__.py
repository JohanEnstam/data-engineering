"""
GCP (Google Cloud Platform) module for IGDB ML Pipeline project.

This module provides functionality for:
- Budget monitoring and cost tracking
- Resource usage monitoring
- GCP service integration
- Cost optimization recommendations
"""

from .budget_monitor import (
    BudgetInfo,
    CostAlert,
    GCPBudgetMonitor,
    create_budget_monitor,
)

__all__ = ["GCPBudgetMonitor", "BudgetInfo", "CostAlert", "create_budget_monitor"]
