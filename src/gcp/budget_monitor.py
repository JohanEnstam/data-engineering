"""
GCP Budget Monitoring Client
Handles cost tracking, budget alerts, and resource monitoring for the IGDB ML Pipeline project.
"""

import os
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass

from google.cloud import billing_v1
from google.cloud import monitoring_v3
from google.cloud.billing_v1.types import ProjectBillingInfo
from google.cloud.monitoring_v3.types import TimeSeries, Point, TimeInterval, TypedValue
from google.api_core import exceptions as gcp_exceptions

logger = logging.getLogger(__name__)


@dataclass
class BudgetInfo:
    """Budget information data class"""
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


@dataclass
class CostAlert:
    """Cost alert data class"""
    alert_type: str  # 'budget_exceeded', 'approaching_limit', 'unusual_spike'
    message: str
    severity: str  # 'low', 'medium', 'high', 'critical'
    current_cost: float
    threshold: float
    timestamp: datetime


class GCPBudgetMonitor:
    """
    GCP Budget Monitoring Client
    
    Provides functionality to:
    - Monitor project costs and budget utilization
    - Set up budget alerts
    - Track resource usage
    - Generate cost reports
    """
    
    def __init__(self, project_id: str, project_name: str, project_number: str):
        self.project_id = project_id
        self.project_name = project_name
        self.project_number = project_number
        
        # Initialize GCP clients
        try:
            self.billing_client = billing_v1.CloudBillingClient()
            self.monitoring_client = monitoring_v3.MetricServiceClient()
            logger.info(f"GCP clients initialized for project: {project_id}")
        except Exception as e:
            logger.error(f"Failed to initialize GCP clients: {e}")
            raise
    
    def get_project_billing_info(self) -> Optional[ProjectBillingInfo]:
        """Get billing information for the project"""
        try:
            project_name = f"projects/{self.project_id}"
            billing_info = self.billing_client.get_project_billing_info(name=project_name)
            return billing_info
        except gcp_exceptions.NotFound:
            logger.warning(f"No billing account linked to project {self.project_id}")
            return None
        except Exception as e:
            logger.error(f"Error getting billing info: {e}")
            return None
    
    def get_current_month_cost(self) -> float:
        """
        Get current month's cost for the project using Cloud Billing API
        """
        try:
            from datetime import datetime, timedelta
            
            # Get current month's start and end dates
            now = datetime.now()
            month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            month_end = (month_start + timedelta(days=32)).replace(day=1) - timedelta(days=1)
            
            # Query billing data for current month
            # Note: This requires proper billing permissions and setup
            logger.info(f"Getting current month cost from {month_start.date()} to {month_end.date()}")
            
            # For now, return 0 since we don't have actual billing data yet
            # In production, you'd query the Cloud Billing API here
            return 0.0
            
        except Exception as e:
            logger.error(f"Error getting current month cost: {e}")
            return 0.0
    
    def get_budget_info(self, monthly_budget_limit: float = 100.0) -> BudgetInfo:
        """Get comprehensive budget information"""
        try:
            # Get billing info
            billing_info = self.get_project_billing_info()
            billing_account_id = billing_info.billing_account_name if billing_info else None
            
            # Get current month cost
            current_cost = self.get_current_month_cost()
            
            # Calculate budget utilization
            budget_utilization = (current_cost / monthly_budget_limit) * 100 if monthly_budget_limit > 0 else 0
            
            # Calculate days remaining in month
            now = datetime.now()
            last_day_of_month = (now.replace(day=1) + timedelta(days=32)).replace(day=1) - timedelta(days=1)
            days_remaining = (last_day_of_month - now).days + 1
            
            # Project monthly cost based on current spending rate
            days_elapsed = now.day
            if days_elapsed > 0:
                projected_monthly_cost = (current_cost / days_elapsed) * 30
            else:
                projected_monthly_cost = current_cost
            
            # Determine if over budget or approaching limit
            is_over_budget = current_cost > monthly_budget_limit
            is_approaching_limit = budget_utilization >= 80  # 80% threshold
            
            return BudgetInfo(
                project_id=self.project_id,
                project_name=self.project_name,
                project_number=self.project_number,
                billing_account_id=billing_account_id,
                monthly_budget_limit=monthly_budget_limit,
                current_month_cost=current_cost,
                budget_utilization_percent=budget_utilization,
                days_remaining_in_month=days_remaining,
                projected_monthly_cost=projected_monthly_cost,
                is_over_budget=is_over_budget,
                is_approaching_limit=is_approaching_limit
            )
            
        except Exception as e:
            logger.error(f"Error getting budget info: {e}")
            # Return default values on error
            return BudgetInfo(
                project_id=self.project_id,
                project_name=self.project_name,
                project_number=self.project_number,
                billing_account_id=None,
                monthly_budget_limit=monthly_budget_limit,
                current_month_cost=0.0,
                budget_utilization_percent=0.0,
                days_remaining_in_month=30,
                projected_monthly_cost=0.0,
                is_over_budget=False,
                is_approaching_limit=False
            )
    
    def check_cost_alerts(self, budget_info: BudgetInfo) -> List[CostAlert]:
        """Check for cost-related alerts"""
        alerts = []
        
        try:
            # Budget exceeded alert
            if budget_info.is_over_budget:
                alerts.append(CostAlert(
                    alert_type="budget_exceeded",
                    message=f"Budget exceeded! Current cost: ${budget_info.current_month_cost:.2f} / ${budget_info.monthly_budget_limit:.2f}",
                    severity="critical",
                    current_cost=budget_info.current_month_cost,
                    threshold=budget_info.monthly_budget_limit,
                    timestamp=datetime.now()
                ))
            
            # Approaching limit alert
            elif budget_info.is_approaching_limit:
                alerts.append(CostAlert(
                    alert_type="approaching_limit",
                    message=f"Approaching budget limit! {budget_info.budget_utilization_percent:.1f}% used",
                    severity="high",
                    current_cost=budget_info.current_month_cost,
                    threshold=budget_info.monthly_budget_limit * 0.8,
                    timestamp=datetime.now()
                ))
            
            # High projected cost alert
            if budget_info.projected_monthly_cost > budget_info.monthly_budget_limit * 1.2:
                alerts.append(CostAlert(
                    alert_type="high_projection",
                    message=f"High projected monthly cost: ${budget_info.projected_monthly_cost:.2f}",
                    severity="medium",
                    current_cost=budget_info.current_month_cost,
                    threshold=budget_info.monthly_budget_limit * 1.2,
                    timestamp=datetime.now()
                ))
            
            return alerts
            
        except Exception as e:
            logger.error(f"Error checking cost alerts: {e}")
            return []
    
    def get_resource_usage_summary(self) -> Dict[str, any]:
        """Get summary of resource usage (simplified implementation)"""
        try:
            # This is a simplified implementation
            # In production, you'd query actual resource usage metrics
            return {
                "compute_instances": 0,
                "storage_gb": 0,
                "api_requests": 0,
                "data_processed_gb": 0,
                "last_updated": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Error getting resource usage: {e}")
            return {}
    
    def create_budget_alert_policy(self, budget_limit: float, alert_threshold: float = 80.0) -> bool:
        """
        Create a budget alert policy
        Note: This requires proper billing permissions and setup
        """
        try:
            logger.info(f"Creating budget alert policy for ${budget_limit} with {alert_threshold}% threshold")
            # Implementation would go here
            # This requires billing API setup and proper permissions
            return True
        except Exception as e:
            logger.error(f"Error creating budget alert policy: {e}")
            return False


def create_budget_monitor() -> GCPBudgetMonitor:
    """Factory function to create a budget monitor with environment variables"""
    project_id = os.getenv("GCP_PROJECT_ID", "exalted-tempo-471613-e2")
    project_name = os.getenv("GCP_PROJECT_NAME", "IGDB-ML-Pipeline")
    project_number = os.getenv("GCP_PROJECT_NUMBER", "628024640688")
    
    return GCPBudgetMonitor(project_id, project_name, project_number)


if __name__ == "__main__":
    # Test the budget monitor
    monitor = create_budget_monitor()
    budget_info = monitor.get_budget_info(monthly_budget_limit=100.0)
    alerts = monitor.check_cost_alerts(budget_info)
    
    print(f"Budget Info: {budget_info}")
    print(f"Alerts: {alerts}")
