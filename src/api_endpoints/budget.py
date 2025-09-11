"""
Budget Monitoring API Endpoints
Provides REST API endpoints for budget tracking and cost monitoring.
"""

import logging
import os
from datetime import datetime
from typing import Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from gcp.budget_monitor import (BudgetInfo, CostAlert, GCPBudgetMonitor,
                                create_budget_monitor)

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/api/budget", tags=["budget"])


# Pydantic models for API responses
class BudgetInfoResponse(BaseModel):
    project_id: str
    project_name: str
    project_number: str
    billing_account_id: Optional[str]
    monthly_budget_limit: float
    current_month_cost: float
    budget_utilization_percent: float
    days_remaining_in_month: int
    projected_monthly_cost: float
    is_over_budget: bool
    is_approaching_limit: bool
    last_updated: str


class CostAlertResponse(BaseModel):
    alert_type: str
    message: str
    severity: str
    current_cost: float
    threshold: float
    timestamp: str


class ResourceUsageResponse(BaseModel):
    compute_instances: int
    storage_gb: float
    api_requests: int
    data_processed_gb: float
    last_updated: str


class BudgetSummaryResponse(BaseModel):
    budget_info: BudgetInfoResponse
    alerts: List[CostAlertResponse]
    resource_usage: ResourceUsageResponse
    status: str  # 'healthy', 'warning', 'critical'


# Dependency to get budget monitor
def get_budget_monitor() -> GCPBudgetMonitor:
    """Dependency to get budget monitor instance"""
    return create_budget_monitor()


@router.get("/info", response_model=BudgetInfoResponse)
async def get_budget_info(
    budget_limit: float = 100.0, monitor: GCPBudgetMonitor = Depends(get_budget_monitor)
):
    """
    Get current budget information for the project.

    Args:
        budget_limit: Monthly budget limit in USD (default: 100.0)

    Returns:
        BudgetInfoResponse: Current budget status and utilization
    """
    try:
        budget_info = monitor.get_budget_info(monthly_budget_limit=budget_limit)

        return BudgetInfoResponse(
            project_id=budget_info.project_id,
            project_name=budget_info.project_name,
            project_number=budget_info.project_number,
            billing_account_id=budget_info.billing_account_id,
            monthly_budget_limit=budget_info.monthly_budget_limit,
            current_month_cost=budget_info.current_month_cost,
            budget_utilization_percent=budget_info.budget_utilization_percent,
            days_remaining_in_month=budget_info.days_remaining_in_month,
            projected_monthly_cost=budget_info.projected_monthly_cost,
            is_over_budget=budget_info.is_over_budget,
            is_approaching_limit=budget_info.is_approaching_limit,
            last_updated=datetime.now().isoformat(),
        )

    except Exception as e:
        logger.error(f"Error getting budget info: {e}")
        raise HTTPException(
            status_code=500, detail=f"Failed to get budget info: {str(e)}"
        )


@router.get("/alerts", response_model=List[CostAlertResponse])
async def get_cost_alerts(
    budget_limit: float = 100.0, monitor: GCPBudgetMonitor = Depends(get_budget_monitor)
):
    """
    Get current cost alerts for the project.

    Args:
        budget_limit: Monthly budget limit in USD (default: 100.0)

    Returns:
        List[CostAlertResponse]: Current cost alerts
    """
    try:
        budget_info = monitor.get_budget_info(monthly_budget_limit=budget_limit)
        alerts = monitor.check_cost_alerts(budget_info)

        return [
            CostAlertResponse(
                alert_type=alert.alert_type,
                message=alert.message,
                severity=alert.severity,
                current_cost=alert.current_cost,
                threshold=alert.threshold,
                timestamp=alert.timestamp.isoformat(),
            )
            for alert in alerts
        ]

    except Exception as e:
        logger.error(f"Error getting cost alerts: {e}")
        raise HTTPException(
            status_code=500, detail=f"Failed to get cost alerts: {str(e)}"
        )


@router.get("/resources", response_model=ResourceUsageResponse)
async def get_resource_usage(monitor: GCPBudgetMonitor = Depends(get_budget_monitor)):
    """
    Get current resource usage summary.

    Returns:
        ResourceUsageResponse: Current resource usage metrics
    """
    try:
        usage = monitor.get_resource_usage_summary()

        return ResourceUsageResponse(
            compute_instances=usage.get("compute_instances", 0),
            storage_gb=usage.get("storage_gb", 0.0),
            api_requests=usage.get("api_requests", 0),
            data_processed_gb=usage.get("data_processed_gb", 0.0),
            last_updated=usage.get("last_updated", datetime.now().isoformat()),
        )

    except Exception as e:
        logger.error(f"Error getting resource usage: {e}")
        raise HTTPException(
            status_code=500, detail=f"Failed to get resource usage: {str(e)}"
        )


@router.get("/summary", response_model=BudgetSummaryResponse)
async def get_budget_summary(
    budget_limit: float = 100.0, monitor: GCPBudgetMonitor = Depends(get_budget_monitor)
):
    """
    Get comprehensive budget summary including info, alerts, and resource usage.

    Args:
        budget_limit: Monthly budget limit in USD (default: 100.0)

    Returns:
        BudgetSummaryResponse: Complete budget overview
    """
    try:
        # Get budget info
        budget_info = monitor.get_budget_info(monthly_budget_limit=budget_limit)

        # Get alerts
        alerts = monitor.check_cost_alerts(budget_info)

        # Get resource usage
        usage = monitor.get_resource_usage_summary()

        # Determine overall status
        if budget_info.is_over_budget:
            status = "critical"
        elif budget_info.is_approaching_limit:
            status = "warning"
        else:
            status = "healthy"

        return BudgetSummaryResponse(
            budget_info=BudgetInfoResponse(
                project_id=budget_info.project_id,
                project_name=budget_info.project_name,
                project_number=budget_info.project_number,
                billing_account_id=budget_info.billing_account_id,
                monthly_budget_limit=budget_info.monthly_budget_limit,
                current_month_cost=budget_info.current_month_cost,
                budget_utilization_percent=budget_info.budget_utilization_percent,
                days_remaining_in_month=budget_info.days_remaining_in_month,
                projected_monthly_cost=budget_info.projected_monthly_cost,
                is_over_budget=budget_info.is_over_budget,
                is_approaching_limit=budget_info.is_approaching_limit,
                last_updated=datetime.now().isoformat(),
            ),
            alerts=[
                CostAlertResponse(
                    alert_type=alert.alert_type,
                    message=alert.message,
                    severity=alert.severity,
                    current_cost=alert.current_cost,
                    threshold=alert.threshold,
                    timestamp=alert.timestamp.isoformat(),
                )
                for alert in alerts
            ],
            resource_usage=ResourceUsageResponse(
                compute_instances=usage.get("compute_instances", 0),
                storage_gb=usage.get("storage_gb", 0.0),
                api_requests=usage.get("api_requests", 0),
                data_processed_gb=usage.get("data_processed_gb", 0.0),
                last_updated=usage.get("last_updated", datetime.now().isoformat()),
            ),
            status=status,
        )

    except Exception as e:
        logger.error(f"Error getting budget summary: {e}")
        raise HTTPException(
            status_code=500, detail=f"Failed to get budget summary: {str(e)}"
        )


@router.post("/alerts/create")
async def create_budget_alert_policy(
    budget_limit: float,
    alert_threshold: float = 80.0,
    monitor: GCPBudgetMonitor = Depends(get_budget_monitor),
):
    """
    Create a budget alert policy.

    Args:
        budget_limit: Monthly budget limit in USD
        alert_threshold: Alert threshold percentage (default: 80.0)

    Returns:
        Dict: Success status and message
    """
    try:
        success = monitor.create_budget_alert_policy(budget_limit, alert_threshold)

        if success:
            return {
                "success": True,
                "message": f"Budget alert policy created for ${budget_limit} with {alert_threshold}% threshold",
            }
        else:
            return {"success": False, "message": "Failed to create budget alert policy"}

    except Exception as e:
        logger.error(f"Error creating budget alert policy: {e}")
        raise HTTPException(
            status_code=500, detail=f"Failed to create budget alert policy: {str(e)}"
        )


@router.get("/health")
async def budget_health_check():
    """
    Health check endpoint for budget monitoring service.

    Returns:
        Dict: Health status
    """
    return {
        "status": "healthy",
        "service": "budget-monitoring",
        "timestamp": datetime.now().isoformat(),
    }
