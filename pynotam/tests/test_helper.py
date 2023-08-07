from pathlib import Path


def read_test_data() -> list[list[str]]:
    test_data = []
    for filepath in (Path(__file__).parent / 'test_data').iterdir():
        test_data.append(filepath.read_text().split('\n'))

    print(test_data)

    return test_data


def read_single_notam(id: str) -> str:
    """'id' should be either the IAA internal integer identifier, or the NOTAM series and number/year --
    depending on the name of the test_data file containing it."""

    filename = '{}.txt'.format(id)
    filename = filename.replace('/', '_')

    return (Path(__file__).parent / 'test_data' / filename).read_text()
