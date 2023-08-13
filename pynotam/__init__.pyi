from _typeshed import Incomplete
from datetime import datetime
from pynotam.timeutils import EstimatedDateTime as EstimatedDateTime
from typing import Dict, List, Optional, Set, Tuple

class Notam:
    full_text: Optional[str]
    notam_id: Optional[str]
    notam_type: Optional[str]
    ref_notam_id: Optional[str]
    fir: Optional[str]
    notam_code: Optional[str]
    traffic_type: Optional[Set[str]]
    purpose: Optional[Set[str]]
    scope: Optional[Set[str]]
    fl_lower: Optional[str]
    fl_upper: Optional[str]
    area: Optional[Dict[str, str | int]]
    location: Optional[List[str]]
    valid_from: Optional[str]
    valid_till: Optional[datetime | EstimatedDateTime]
    schedule: Optional[str]
    body: Optional[str]
    limit_lower: Optional[str]
    limit_upper: Optional[str]
    source: Optional[str]
    created: Optional[datetime]
    indices_item_a: Optional[Tuple[int, int]]
    indices_item_b: Optional[Tuple[int, int]]
    indices_item_c: Optional[Tuple[int, int]]
    indices_item_d: Optional[Tuple[int, int]]
    indices_item_e: Optional[Tuple[int, int]]
    indices_item_f: Optional[Tuple[int, int]]
    indices_item_g: Optional[Tuple[int, int]]
    decode_abbr_regex: Incomplete
    def decoded(self) -> str: ...
    @staticmethod
    def from_str(s: str) -> Notam: ...
    @classmethod
    def decode_abbr(cls, txt: str) -> str: ...
