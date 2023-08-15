from __future__ import annotations
from datetime import datetime

import re as _re
from io import StringIO as _StringIO
from typing import Dict, List, Optional, Set, Tuple

from pynotam.timeutils import EstimatedDateTime

from ._abbr import ICAO_abbr
from ._parser import NotamParseVisitor


class Notam(object):
    """
    The full text of the NOTAM (for example, when constructed with from_str(s),
    this will contain s.
    """
    full_text: Optional[str] = None

    """The series and number/year of this NOTAM."""
    notam_id: Optional[str] = None

    """The NOTAM type: 'NEW', 'REPLACE', or 'CANCEL'."""
    notam_type: Optional[str] = None

    """
    If this  NOTAM references a previous NOTAM (notam_type is 'REPLACE' or 'CANCEL'),
    the series and number/year of the other NOTAM.
    """
    ref_notam_id: Optional[str] = None

    """The FIR within which the subject of the information is located."""
    fir: Optional[str] = None
    """
    The five-letter NOTAM code, beginning with 'Q'. (Currently a simple str; at some
    point may be further parsed to specify the code's meaning.)
    """
    notam_code: Optional[str] = None

    '''Set of affected traffic. Will contain one or more of: "IFR"/"VFR"/"CHECKLIST"'''
    traffic_type: Set[str] = set()

    """
    Set of NOTAM purposes. Will contain one or more of:
      'IMMEDIATE ATTENTION'/'OPERATIONAL SIGNIFICANCE'/'FLIGHT OPERATIONS'/
      'MISC'/'CHECKLIST'.
    """
    purpose: Set[str] = set()

    """
    Set of NOTAM scopes. Will contain one or more of:
      'AERODROME'/'EN-ROUTE'/'NAV WARNING'/'CHECKLIST'.
    """
    scope: Set[str] = set()

    """Lower vertical limit of NOTAM area of influence, expressed in flight levels (int)."""
    fl_lower: Optional[str] = None
    """Upper vertical limit of NOTAM area of influence, expressed in flight levels (int)."""
    fl_upper: Optional[str] = None
    """
    Approximate circle whose radius encompasses the NOTAM's whole area of influence.
    This is a dict with keys: 'lat', 'long', 'radius' (str, str, int respectively).
    """
    area: Dict[str, str | int] = {}

    """
    List of one or more ICAO location indicators, specifying the aerodrome or FIR
    in which the facility, airspace, or condition being reported on is located.
    """
    location: List[str] = []

    """The date and time at which the NOTAM comes into force (datetime.datetime)."""
    valid_from: Optional[str] = None

    """
    For anything except a 'CANCEL'-type NOTAM, a date and time indicating duration of
    information (datetime.datetime). If permanent, equal to datetime.datetime.max.
    If the validity period is estimated, an instance of timeutils.EstimatedDateTime
    with an attribute 'is_estimated' set to True.
    """
    valid_till: Optional[datetime | EstimatedDateTime] = None

    """
    If the condition is active in accordance with a specific time date schedule, an
    abbreviated textual description of this schedule.
    """
    schedule: Optional[str] = None

    """Text of NOTAM; Plain-language Entry (using ICAO Abbreviations)."""
    body: Optional[str] = None
    """Textual specification of lower height limit of activities or restrictions."""
    limit_lower: Optional[str] = None
    """Textual specification of upper height limits of activities or restrictions."""
    limit_upper: Optional[str] = None

    """Source of the NOTAM."""
    source: Optional[str] = None
    """The date and time of creation."""
    created: Optional[datetime] = None

    # The following contain [start,end) indices for their corresponding NOTAM items (if such exist).
    # They can be used to index into Notam.full_text.
    indices_item_a: Optional[Tuple[int, int]] = None
    indices_item_b: Optional[Tuple[int, int]] = None
    indices_item_c: Optional[Tuple[int, int]] = None
    indices_item_d: Optional[Tuple[int, int]] = None
    indices_item_e: Optional[Tuple[int, int]] = None
    indices_item_f: Optional[Tuple[int, int]] = None
    indices_item_g: Optional[Tuple[int, int]] = None

    decode_abbr_regex = _re.compile(
        r"\b(" + "|".join([_re.escape(key) for key in ICAO_abbr.keys()]) + r")\b"
    )

    def decoded(self) -> str:
        """Returns the full text of the NOTAM, with ICAO abbreviations decoded into their un-abbreviated
        form where appropriate."""

        with _StringIO() as sb:
            indices = [
                getattr(self, "indices_item_{}".format(i)) for i in ("d", "e", "f", "g")
            ]
            indices = [i for i in indices if i is not None]
            indices.sort()  # The items should already be listed in the order of their apperance in the text, but
            # we sort them here just in case
            indices = [(0, 0)] + indices + [(-1, -1)]

            if self.full_text is not None:
                for cur, nxt in zip(indices, indices[1:]):
                    (cs, ce) = cur
                    (ns, _) = nxt
                    _ = sb.write(
                        self.decode_abbr(self.full_text[cs:ce])
                    )  # decode the text of this range
                    _ = sb.write(
                        self.full_text[ce:ns]
                    )  # copy the text from end of current range to start
                    # of next verbatim
            return sb.getvalue()

    @staticmethod
    def from_str(s: str) -> Notam:
        """Returns a Notam containing information parsed from within the provided string."""
        n = Notam()
        visitor = NotamParseVisitor(n)
        visitor.parse(s)
        return n

    @classmethod
    def decode_abbr(cls, txt: str) -> str:
        """Decodes ICAO abbreviations in 'txt' to their un-abbreviated form."""
        return cls.decode_abbr_regex.sub(lambda m: ICAO_abbr[m.group()], txt)
