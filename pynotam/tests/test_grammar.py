import unittest

from .._parser import grammar
from .test_helper import read_test_data


class GrammarParse(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super(GrammarParse, self).__init__(*args, **kwargs)
        self.test_data = read_test_data()

    def try_parse_all(self, rule: str, items: list[str]) -> None:
        for i in items:
            try:
                _ = grammar[rule].parse(i)
            except:
                print('Starting at rule "{}", failed to parse:\n{}'.format(rule, i))
                raise

    def test_header(self) -> None:
        headers = [d[0] for d in self.test_data]
        headers = [h[1:].strip() for h in headers] # remove opening parenthesis
        self.try_parse_all('header', headers)

    def test_qclause(self) -> None:
        qlines = [d[1].strip() for d in self.test_data]
        self.try_parse_all('q_clause', qlines)

    def test_aclause(self) -> None:
        alines = [d[2] for d in self.test_data]
        alines = [d[:d.find(' B)')] for d in alines]
        self.try_parse_all('a_clause', alines)

    def test_bclause(self) -> None:
        blines = [d[2] for d in self.test_data]
        blines = [d[d.find('B)'):d.find(' C)')] for d in blines if 'B)' in d]
        self.try_parse_all('b_clause', blines)

    def test_cclause(self) -> None:
        clines = [d[2] for d in self.test_data]
        clines = [d[d.find('C)'):] for d in clines if 'C)' in d]
        self.try_parse_all('c_clause', clines)

    def test_root(self) -> None:
        notams = ['\n'.join(d) for d in self.test_data]
        self.try_parse_all('root', notams)
