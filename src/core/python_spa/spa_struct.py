import json
from typing import List, Optional

from pydantic import BaseModel


class TimeRange(BaseModel):
    calendar_time: Optional[str] = None
    missing_data_time: Optional[str] = None
    valid_time: Optional[str] = None
    excluded_time: Optional[str] = None
    reference_run_time: Optional[str] = None
    theo_production_run_time: Optional[str] = None
    pr: Optional[str] = None
    uptime: Optional[str] = None
    mtbf: Optional[str] = None
    mttr: Optional[str] = None
    net_production: Optional[str] = None
    theo_production_target_speed: Optional[str] = None
    theo_production_design_speed: Optional[str] = None
    availability: Optional[str] = None
    efficiency: Optional[str] = None


class Products(BaseModel):
    po: Optional[str] = None
    fa_code: Optional[str] = None
    time: Optional[str] = None


class ProductByPO(BaseModel):
    products: List[Products] = []


class LinePerformance(BaseModel):
    line_failure: Optional[str] = None
    run_time: Optional[str] = None
    line_mtbf: Optional[str] = None
    reject: Optional[str] = None
    total_reject: Optional[str] = None


class Losses(BaseModel):
    time: Optional[str] = None
    stops: Optional[str] = None
    downtime: Optional[str] = None
    uptime_loss: Optional[str] = None
    mtbf: Optional[str] = None
    mttr: Optional[str] = None
    details: Optional[str] = None


class RateLoss(BaseModel):
    dsl: Optional[Losses] = None
    trl: Optional[Losses] = None
    natr: Optional[Losses] = None
    ramp_up_down: Optional[Losses] = None


class QualityLoss(BaseModel):
    reject_loss: Optional[Losses] = None


class PlannedStopReason(BaseModel):
    description: Optional[str] = None
    time: Optional[str] = None
    stops: Optional[str] = None
    downtime: Optional[str] = None
    uptime_loss: Optional[str] = None
    mtbf: Optional[str] = None
    mttr: Optional[str] = None
    details: Optional[str] = None


class Planned(BaseModel):
    pdt: Optional[Losses] = None
    pdt_reason: List[PlannedStopReason] = []


class UnplannedStopReason(BaseModel):
    description: Optional[str] = None
    stops: Optional[str] = None
    ramp_up: Optional[str] = None
    downtime: Optional[str] = None
    uptime_loss: Optional[str] = None
    mtbf: Optional[str] = None
    mttr: Optional[str] = None
    rejects_percent: Optional[str] = None
    stops_per_shift: Optional[str] = None
    causing_equipment: Optional[str] = None


class UPDT(BaseModel):
    category: Optional[str] = None
    losses: Optional[Losses] = None


class Unplanned(BaseModel):
    updt: Losses = Losses()
    updt_shift: List[UPDT] = []
    updt_category: List[UPDT] = []
    bde: List[UPDT] = []
    pf: List[UPDT] = []
    updt_reason: List[UnplannedStopReason] = []


class SPALossTree(BaseModel):
    equipment: Optional[str] = None
    period: Optional[str] = None
    time_range: Optional[TimeRange] = None
    product_by_po: Optional[ProductByPO] = None
    line_performance: Optional[LinePerformance] = None
    rate_loss: Optional[RateLoss] = None
    quality_loss: Optional[QualityLoss] = None
    planned: Optional[Planned] = None
    unplanned: Optional[Unplanned] = None


class StopReason(BaseModel):
    description: Optional[str] = None
    stops: Optional[str] = None
    downtime_min: Optional[str] = None
    oee_percent: Optional[str] = None
    rejects_percent: Optional[str] = None
    stops_per_shift: List[str] = []


class Machine(BaseModel):
    id: Optional[str] = None
    machine_type: Optional[str] = None
    total_downtime_min: Optional[str] = None
    total_stops: Optional[str] = None
    total_run_time_min: Optional[str] = None
    avg_speed_cig_per_min: Optional[str] = None
    production_mio_cig: Optional[str] = None
    total_rejects_percent: Optional[str] = None
    mtbf_min: Optional[str] = None
    mttr_min: Optional[str] = None
    stop_reasons: List[StopReason] = []

    def to_dict(self):
        return self.model_dump()


class StopStatistics(BaseModel):
    factory: Optional[str] = None
    line: Optional[str] = None
    design_speed: Optional[str] = None
    target_speed: Optional[str] = None
    time_period: Optional[str] = None
    machines: List[Machine] = []

    def to_dict(self):
        return self.model_dump()
