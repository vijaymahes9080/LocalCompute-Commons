"""
Carbon-Aware and Renewable Energy Scheduling Optimization Engine
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Any, Optional

@dataclass
class CarbonIntensityMetrics:
    region_code: str
    carbon_intensity_gco2_per_kwh: float  # grams of CO2 per kWh
    is_solar_peak: bool
    is_renewable_surplus: bool

class CarbonAwareScheduler:
    """
    Computes green energy score adjustments to prioritize nodes running on
    renewable/solar power or during low grid carbon intensity windows.
    """
    @staticmethod
    def calculate_green_energy_bonus(
        power_state: str,
        is_charging: bool,
        carbon_metrics: Optional[CarbonIntensityMetrics] = None
    ) -> float:
        bonus = 0.0
        # If node is grid-powered during solar peak or renewable surplus
        if carbon_metrics and carbon_metrics.is_renewable_surplus:
            bonus += 15.0
        elif carbon_metrics and carbon_metrics.is_solar_peak:
            bonus += 10.0
            
        # If regional carbon intensity is low (<150 gCO2/kWh)
        if carbon_metrics and carbon_metrics.carbon_intensity_gco2_per_kwh < 150.0:
            bonus += 10.0
            
        return round(bonus, 2)
