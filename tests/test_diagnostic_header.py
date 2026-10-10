from pathlib import Path


def test_diagnostic_depends_header_is_first_line():
    lines = Path('diagnostics/AdjudicationProbe.py').read_text(encoding='utf-8').splitlines()
    assert lines[0].startswith('# { "Depends": "py-genlayer:')
    assert lines[1] == 'from genlayer import *'
