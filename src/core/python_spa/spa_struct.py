import json
from dataclasses import asdict, dataclass, field
from typing import List, Optional


@dataclass(slots=True)
class TimeRange:
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


@dataclass(slots=True)
class Products:
    po: Optional[str] = None
    fa_code: Optional[str] = None
    time: Optional[str] = None


@dataclass(slots=True)
class ProductByPO:
    products: List[Products] = field(default_factory=list)


@dataclass(slots=True)
class LinePerformance:
    line_failure: Optional[str] = None
    run_time: Optional[str] = None
    line_mtbf: Optional[str] = None
    reject: Optional[str] = None
    total_reject: Optional[str] = None


@dataclass(slots=True)
class Losses:
    time: Optional[str] = None
    stops: Optional[str] = None
    downtime: Optional[str] = None
    uptime_loss: Optional[str] = None
    mtbf: Optional[str] = None
    mttr: Optional[str] = None
    details: Optional[str] = None


@dataclass(slots=True)
class RateLoss:
    dsl: Optional[Losses] = None
    trl: Optional[Losses] = None
    natr: Optional[Losses] = None
    ramp_up_down: Optional[Losses] = None


@dataclass(slots=True)
class QualityLoss:
    reject_loss: Optional[Losses] = None


@dataclass(slots=True)
class PlannedStopReason:
    description: Optional[str] = None
    time: Optional[str] = None
    stops: Optional[str] = None
    downtime: Optional[str] = None
    uptime_loss: Optional[str] = None
    mtbf: Optional[str] = None
    mttr: Optional[str] = None
    details: Optional[str] = None


@dataclass(slots=True)
class Planned:
    pdt: Optional[Losses] = None
    pdt_reason: List[PlannedStopReason] = field(default_factory=list)


@dataclass(slots=True)
class UnplannedStopReason:
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


@dataclass(slots=True)
class UPDT:
    category: Optional[str] = None
    losses: Optional[Losses] = None


@dataclass(slots=True)
class Unplanned:
    updt: Losses = field(default_factory=Losses)
    updt_shift: List[UPDT] = field(default_factory=list)
    updt_category: List[UPDT] = field(default_factory=list)
    bde: List[UPDT] = field(default_factory=list)
    pf: List[UPDT] = field(default_factory=list)
    updt_reason: List[UnplannedStopReason] = field(default_factory=list)


@dataclass(slots=True)
class SPALossTree:
    equipment: Optional[str] = None
    period: Optional[str] = None
    time_range: Optional[TimeRange] = None
    product_by_po: Optional[ProductByPO] = None
    line_performance: Optional[LinePerformance] = None
    rate_loss: Optional[RateLoss] = None
    quality_loss: Optional[QualityLoss] = None
    planned: Optional[Planned] = None
    unplanned: Optional[Unplanned] = None


@dataclass(slots=True)
class StopReason:
    description: Optional[str] = None
    stops: Optional[str] = None
    downtime_min: Optional[str] = None
    oee_percent: Optional[str] = None
    rejects_percent: Optional[str] = None
    stops_per_shift: List[str] = field(default_factory=list)


@dataclass(slots=True)
class Machine:
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
    stop_reasons: List[StopReason] = field(default_factory=list)

    def to_dict(self):
        return asdict(self)


@dataclass(slots=True)
class StopStatistics:
    factory: Optional[str] = None
    line: Optional[str] = None
    design_speed: Optional[str] = None
    target_speed: Optional[str] = None
    time_period: Optional[str] = None
    machines: List[Machine] = field(default_factory=list)

    def to_dict(self):
        return asdict(self)
