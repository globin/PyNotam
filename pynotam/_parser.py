from __future__ import annotations

from typing import TYPE_CHECKING, Any, Callable, List, Sequence
from typing_extensions import override
import parsimonious
from datetime import timezone

from parsimonious.nodes import Node, RegexNode
from .timeutils import datetime, EstimatedDateTime

if TYPE_CHECKING:
    from . import Notam

grammar = parsimonious.Grammar(r"""
    root = "(" header __ q_clause __ a_clause __ b_clause __ (c_clause __)? (d_clause __)? e_clause (__ f_clause __ g_clause)? ")"

    header = notamn_header / notamr_header / notamc_header
    notamn_header = notam_id _ "NOTAMN"
    notamr_header = notam_id _ "NOTAMR" _ notam_id
    notamc_header = notam_id _ "NOTAMC" _ notam_id
    notam_id = ~r"[A-Z][0-9]{4}/[0-9]{2}"

    q_clause = "Q)" _ fir "/" notam_code "/" traffic_type _* "/" purpose _* "/" scope _* "/" lower_limit "/" upper_limit "/" area_of_effect
    fir = icao_id
    notam_code = ~r"Q[A-Z]{4}"
    traffic_type = ~r"(?=[IVK]+)I?V?K?"
    purpose = ~r"(?=[NBOMK]+)N?B?O?M?K?"
    scope = ~"(?=[AEWK]+)A?E?W?K?"
    lower_limit = int3
    upper_limit = int3
    area_of_effect = ~r"(?P<lat>[0-9]{4}[NS])(?P<long>[0-9]{5}[EW])(?P<radius>[0-9]{3})"

    # TODO: needs improved multi-part handling
    a_clause = "A)" _ location_icao (_ location_icao)* (_ "PART" _ int _ "OF" _ int)?
    location_icao = !"PART" icao_id

    b_clause = "B)" _ datetime
    c_clause = "C)" _ ((datetime _* estimated?) / permanent)
    estimated = "EST"
    permanent = "PERM"

    d_clause = "D)" _ till_next_clause
    e_clause = "E)" _ till_next_clause
    f_clause = "F)" _ till_next_clause
    g_clause = "G)" _ till_next_clause

    _ = " "
    __ = (" " / "\n")+
    icao_id = ~r"[A-Z]{4}"
    datetime = int2 int2 int2 int2 int2 # year month day hours minutes
    int = ~r"[0-9]"
    int2 = ~r"[0-9]{2}"
    int3 = ~r"[0-9]{3}"
    till_next_clause = ~r".*?(?=(?:\)$)|(?:\s[A-Z]\)))"s
""")

class NotamParseVisitor(parsimonious.NodeVisitor):
    def __init__(self, tgt: "Notam"):
        """tgt must be an instance of an object with a __dict__ attribute. All data attributes
        resulting from the parsing of the NOTAM will be assigned to that object."""
        self.tgt = tgt
        super().__init__()

    grammar = grammar

    @staticmethod
    def has_descendant(node: Node, descnd_name: str) -> bool:
        if node.expr_name == descnd_name:
            return True
        else:
            return any([NotamParseVisitor.has_descendant(c,descnd_name) for c in node.children])

    def visit_simple_regex(self, node: RegexNode, _) -> str:
        return node.match.group(0)
    visit_till_next_clause = visit_simple_regex

    def visit_code_node(self, *args: RegexNode, meanings: dict[str, str]):
        """Maps coded strings, where each character encodes a special meaning, into a corresponding decoded set
        according to the meanings dictionary (see examples of usage further below)"""
        codes = self.visit_simple_regex(*args)
        return set([meanings[code] for code in codes])

    def visit_intX(self, *args: RegexNode) -> int:
        v = self.visit_simple_regex(*args)
        return int(v)

    visit_int2 = visit_intX
    visit_int3 = visit_intX

    @staticmethod
    def visit_notamX_header(notam_type: str) -> Callable[[NotamParseVisitor, Node, Sequence[str]], None]:
        def inner(self: NotamParseVisitor, _, visited_children: Sequence[str]):
            self.tgt.notam_id = visited_children[0]
            self.tgt.notam_type = notam_type
            if self.tgt.notam_type in ('REPLACE', 'CANCEL'):
                self.tgt.ref_notam_id = visited_children[-1]
        return inner

    visit_notamn_header = visit_notamX_header('NEW')
    visit_notamr_header = visit_notamX_header('REPLACE')
    visit_notamc_header = visit_notamX_header('CANCEL')

    visit_icao_id = visit_simple_regex
    visit_notam_id = visit_simple_regex

    def visit_q_clause(self, _: Node, visited_children: list[Any]):
        self.tgt.fir = visited_children[2]
        self.tgt.fl_lower = visited_children[15]
        self.tgt.fl_upper = visited_children[17]

    def visit_notam_code(self, *args: RegexNode):
        self.tgt.notam_code = self.visit_simple_regex(*args) # TODO: Parse this into the code's meaning. One day...

    def visit_traffic_type(self, *args):
        self.tgt.traffic_type = self.visit_code_node(*args, meanings={'I' : 'IFR',
                                                                      'V' : 'VFR',
                                                                      'K' : 'CHECKLIST'})

    def visit_purpose(self, *args):
        self.tgt.purpose = self.visit_code_node(*args, meanings={'N' : 'IMMEDIATE ATTENTION',
                                                                 'B' : 'OPERATIONAL SIGNIFICANCE',
                                                                 'O' : 'FLIGHT OPERATIONS',
                                                                 'M' : 'MISC',
                                                                 'K' : 'CHECKLIST'})

    def visit_scope(self, *args):
        self.tgt.scope = self.visit_code_node(*args, meanings={'A' : 'AERODROME',
                                                               'E' : 'EN-ROUTE',
                                                               'W' : 'NAV WARNING',
                                                               'K' : 'CHECKLIST'})

    def visit_area_of_effect(self, node: RegexNode, _):
        self.tgt.area = node.match.groupdict() # dictionary containing mappings for 'lat', 'long', and 'radius'
        self.tgt.area['radius'] = int(self.tgt.area['radius'])

    def visit_a_clause(self, node: RegexNode, _):
        def _dfs_icao_id(n: RegexNode) -> List[str]:
            if n.expr_name == "icao_id": return [self.visit_simple_regex(n, [])]
            return sum([_dfs_icao_id(c) for c in n.children], []) # flatten list-of-lists

        start = node.children[2].start
        end = node.children[-1].end
        self.tgt.location = _dfs_icao_id(node)
        self.tgt.indices_item_a = (start, end)

    def visit_b_clause(self, node: Node, visited_children: Sequence[Any]):
        self.tgt.valid_from = visited_children[2]
        content_child = node.children[2]
        self.tgt.indices_item_b = (content_child.start, content_child.end)

    def visit_c_clause(self, node: Node, visited_children: Sequence[Any]):
        if self.has_descendant(node, 'permanent'):
            dt = datetime.max
        else:
            dt = visited_children[2][0][0]
            if self.has_descendant(node, 'estimated'):
                dt = EstimatedDateTime(dt)
        self.tgt.valid_till = dt
        content_child = node.children[2]
        self.tgt.indices_item_c = (content_child.start, content_child.end)

    def visit_d_clause(self, node: Node, visited_children: Sequence[Any]):
        self.tgt.schedule = visited_children[2]
        content_child = node.children[2]
        self.tgt.indices_item_d = (content_child.start, content_child.end)

    def visit_e_clause(self, node: Node, visited_children: Sequence[Any]):
        self.tgt.body = visited_children[2]
        content_child = node.children[2]
        self.tgt.indices_item_e = (content_child.start, content_child.end)

    def visit_f_clause(self, node: Node, visited_children: Sequence[Any]):
        self.tgt.limit_lower = visited_children[2]
        content_child = node.children[2]
        self.tgt.indices_item_f = (content_child.start, content_child.end)

    def visit_g_clause(self, node: Node, visited_children: Sequence[Any]):
        self.tgt.limit_upper = visited_children[2]
        content_child = node.children[2]
        self.tgt.indices_item_g = (content_child.start, content_child.end)

    def visit_datetime(self, _, visited_children: List[Any]):
        dparts = visited_children
        dparts[0] = 1900 + dparts[0] if dparts[0] > 80 else 2000 + dparts[0] # interpret 2-digit year
        return datetime(*dparts, tzinfo=timezone.utc)

    @override
    def generic_visit(self, node: Node, visited_children: Sequence[Any]) -> Sequence[Any]:
        return visited_children

    def visit_root(self, node: Node, _):
        self.tgt.full_text = node.full_text
