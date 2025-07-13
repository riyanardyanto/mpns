import json
from dataclasses import dataclass, field
from typing import Any, Dict, List, TypedDict

from bs4 import BeautifulSoup


class StopReasonDict(TypedDict):
    description: str
    stops: str
    downtime_min: str
    oee_percent: str
    rejects_percent: str
    stops_per_shift: List[str]


@dataclass(slots=True)
class StopReason:
    description: str = ""
    stops: str = ""
    downtime_min: str = ""
    oee_percent: str = ""
    rejects_percent: str = ""
    stops_per_shift: List[str] = field(default_factory=list)

    def to_dict(self) -> StopReasonDict:
        return {
            "description": self.description,
            "stops": self.stops,
            "downtime_min": self.downtime_min,
            "oee_percent": self.oee_percent,
            "rejects_percent": self.rejects_percent,
            "stops_per_shift": self.stops_per_shift,
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict())


class MachineDict(TypedDict):
    id: str
    machine_type: str
    total_downtime_min: str
    total_stops: str
    total_run_time_min: str
    avg_speed_cig_per_min: str
    production_mio_cig: str
    total_rejects_percent: str
    mtbf_min: str
    mttr_min: str
    stop_reasons: List[StopReasonDict]


@dataclass(slots=True)
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

    def to_dict(self) -> MachineDict:
        return {
            "id": self.id,
            "machine_type": self.machine_type,
            "total_downtime_min": self.total_downtime_min,
            "total_stops": self.total_stops,
            "total_run_time_min": self.total_run_time_min,
            "avg_speed_cig_per_min": self.avg_speed_cig_per_min,
            "production_mio_cig": self.production_mio_cig,
            "total_rejects_percent": self.total_rejects_percent,
            "mtbf_min": self.mtbf_min,
            "mttr_min": self.mttr_min,
            "stop_reasons": [sr.to_dict() for sr in self.stop_reasons],
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict())


class StopStatisticsDict(TypedDict):
    factory: str
    line: str
    design_speed: str
    target_speed: str
    time_period: str
    machines: List[MachineDict]


@dataclass(slots=True)
class StopStatistics:
    factory: str = ""
    line: str = ""
    design_speed: str = ""
    target_speed: str = ""
    time_period: str = ""
    machines: List[Machine] = field(default_factory=list)

    def to_dict(self) -> StopStatisticsDict:
        return {
            "factory": self.factory,
            "line": self.line,
            "design_speed": self.design_speed,
            "target_speed": self.target_speed,
            "time_period": self.time_period,
            "machines": [m.to_dict() for m in self.machines],
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict())


def extract_machines(soup: BeautifulSoup) -> List[List[List[str]]]:
    tables: List[BeautifulSoup] = soup.select("table")
    if len(tables) < 5:
        return []
    table_machines: List[BeautifulSoup] = tables[4].select("table")[2:]
    data_stops: List[List[List[str]]] = []
    for table_machine in table_machines:
        rows: List[BeautifulSoup] = table_machine.select("tr")
        if not rows:
            continue
        table_data: List[List[str]] = [
            [cell.get_text(strip=True) for cell in tr.select("td")]
            for i, tr in enumerate(rows)
            if i != 10
        ]
        data_stops.append(table_data)
    return data_stops


def get_data_machines(soup: BeautifulSoup) -> List[Machine]:
    data: List[List[List[str]]] = extract_machines(soup)
    machine_data: List[List[List[str]]] = data[::2]
    all_machines: List[Machine] = []
    for machine_rows in machine_data:
        if len(machine_rows) < 10:
            continue
        equipment: Machine = Machine(
            id=machine_rows[0][0],
            machine_type=f"{machine_rows[1][1]} - {machine_rows[1][2]}",
            total_downtime_min=machine_rows[2][1],
            total_stops=machine_rows[3][1],
            total_run_time_min=machine_rows[4][1],
            avg_speed_cig_per_min=machine_rows[5][1],
            production_mio_cig=machine_rows[6][1],
            total_rejects_percent=machine_rows[7][1],
            mtbf_min=machine_rows[8][1],
            mttr_min=machine_rows[9][1],
            stop_reasons=[
                StopReason(
                    description=row[0],
                    stops=row[1],
                    downtime_min=row[2],
                    oee_percent=row[3],
                    rejects_percent=row[4],
                    stops_per_shift=row[5:8],
                )
                for row in machine_rows[11:]
                if len(row) >= 8
            ],
        )
        all_machines.append(equipment)
    return all_machines


def extract_stop_stats(html: str) -> StopStatistics:
    """
    Extracts detailed stop statistics from the given HTML page.
    """
    soup: BeautifulSoup = BeautifulSoup(html, "html.parser")
    tables: List[BeautifulSoup] = soup.select("table")
    if len(tables) <= 3:
        raise IndexError("Table index out of bounds")
    table: BeautifulSoup = tables[3]
    rows: List[BeautifulSoup] = table.select("tr")
    data: List[List[str]] = [
        [cell.get_text(strip=True) for cell in row.select("td")] for row in rows
    ]
    stop_statistic: StopStatistics = StopStatistics(
        factory=data[0][1],
        line=data[0][3],
        design_speed=data[1][1],
        target_speed=data[1][3],
        time_period=data[2][1],
        machines=get_data_machines(soup),
    )
    return stop_statistic
