import json
from dataclasses import asdict, dataclass, field
from typing import List, Optional


@dataclass
class TimeRange:
    calendar_time: str = ""
    missing_data_time: str = ""
    valid_time: str = ""
    excluded_time: str = ""
    reference_run_time: str = ""
    theo_production_run_time: str = ""
    pr: str = ""
    uptime: str = ""
    mtbf: str = ""
    mttr: str = ""
    net_production: str = ""
    theo_production_target_speed: str = ""
    theo_production_design_speed: str = ""
    availability: str = ""
    efficiency: str = ""


@dataclass
class Products:
    po: str = ""
    fa_code: str = ""
    time: str = ""


@dataclass
class ProductByPO:
    products: Optional[List[Products]] = None


@dataclass
class LinePerformance:
    line_failure: str = ""
    run_time: str = ""
    line_mtbf: str = ""
    reject: str = ""
    total_reject: str = ""


@dataclass
class Losses:
    time: str = ""
    stops: str = ""
    downtime: str = ""
    uptime_loss: str = ""
    mtbf: str = ""
    mttr: str = ""
    details: str = ""


@dataclass
class RateLoss:
    dsl: Optional[Losses] = None
    trl: Optional[Losses] = None
    natr: Optional[Losses] = None
    ramp_up_down: Optional[Losses] = None


@dataclass
class QualityLoss:
    reject_loss: Optional[Losses] = None


@dataclass
class PlannedStopReason:
    description: str = ""
    time: str = ""
    stops: str = ""
    downtime: str = ""
    uptime_loss: str = ""
    mtbf: str = ""
    mttr: str = ""
    details: str = ""


@dataclass
class Planned:
    pdt: Optional[Losses] = None
    pdt_reason: Optional[List[PlannedStopReason]] = None


@dataclass
class UnplannedStopReason:
    description: str = ""
    stops: str = ""
    ramp_up: str = ""
    downtime: str = ""
    uptime_loss: str = ""
    mtbf: str = ""
    mttr: str = ""
    rejects_percent: str = ""
    stops_per_shift: str = ""
    causing_equipment: str = ""


@dataclass
class UPDT:
    category: str = ""
    losses: Optional[Losses] = None


@dataclass
class Unplanned:
    updt: Losses = field(default_factory=Losses)
    updt_shift: Optional[List[UPDT]] = None
    updt_category: Optional[List[UPDT]] = None
    bde: Optional[List[UPDT]] = None
    pf: Optional[List[UPDT]] = None
    updt_reason: Optional[List[UnplannedStopReason]] = None


@dataclass
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


@dataclass
class StopReason:
    description: str = ""
    stops: str = ""
    downtime_min: str = ""
    oee_percent: str = ""
    rejects_percent: str = ""
    stops_per_shift: List[str] = field(default_factory=list)


@dataclass
class Machine:
    id: str = ""
    machine_type: str = ""
    total_downtime_min: str = ""
    total_stops: str = ""
    total_run_time_min: str = ""
    avg_speed_cig_per_min: str = ""
    production_mio_cig: str = ""
    total_rejects_percent: str = ""
    mtbf_min: str = ""
    mttr_min: str = ""
    stop_reasons: List[StopReason] = field(default_factory=list)

    def to_dict(self):
        return {
            k: v if not isinstance(v, list) else [r.to_dict() for r in v]
            for k, v in self.__dict__.items()
        }


@dataclass
class StopStatistics:
    factory: str = ""
    line: str = ""
    design_speed: str = ""
    target_speed: str = ""
    time_period: str = ""
    machines: List[Machine] = field(default_factory=list)

    def to_dict(self):
        return {
            k: v if not isinstance(v, list) else [m.to_dict() for m in v]
            for k, v in self.__dict__.items()
        }
