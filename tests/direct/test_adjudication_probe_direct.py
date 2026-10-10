import json


def test_adjudication_probe_direct_judgment(direct_vm, direct_deploy, direct_alice):
    direct_vm._chain_id = 61999
    direct_vm.mock_llm(r'.*CONTROL.*', '{"label":"CONTROL"}')
    probe = direct_deploy('diagnostics/AdjudicationProbe.py')
    direct_vm.sender = direct_alice
    probe.direct_judgment('Harmless fixed control prompt.')
    assert json.loads(probe.get_state()) == {'last_result': '{"label": "CONTROL"}', 'ping_count': '0'}
