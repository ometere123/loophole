# Isolated Studionet differential probe. This is not a LOOPHOLE production contract.
# { "Depends": "py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6" }
from genlayer import *
import json


class AdjudicationProbe(gl.Contract):
    last_result: str
    ping_count: u256

    def __init__(self):
        if gl.message.chain_id != u256(61999):
            raise gl.vm.UserError('Studionet 61999 only')
        self.last_result = ''
        self.ping_count = u256(0)

    def _judge(self, prompt: str) -> dict:
        def assess() -> dict:
            answer = gl.nondet.exec_prompt(
                'Return only compact JSON {"label":"CONTROL"}. ' + prompt,
                response_format='json')
            value = answer if isinstance(answer, dict) else json.loads(answer)
            return {'label': 'CONTROL' if value.get('label') == 'CONTROL' else 'REJECTED'}

        def independently_verify(leader) -> bool:
            if not isinstance(leader, gl.vm.Return) or not isinstance(leader.calldata, dict):
                return False
            return assess() == leader.calldata

        return gl.vm.run_nondet_unsafe(assess, independently_verify)

    @gl.public.write
    def direct_judgment(self, prompt: str) -> None:
        self.last_result = json.dumps(self._judge(prompt), sort_keys=True)

    @gl.public.write
    def trigger_judgment(self, prompt: str) -> None:
        gl.get_contract_at(gl.message.contract_address).emit(on='finalized').child_judgment(prompt)

    @gl.public.write
    def child_judgment(self, prompt: str) -> None:
        self.last_result = json.dumps(self._judge(prompt), sort_keys=True)

    @gl.public.write
    def trigger_ping(self) -> None:
        gl.get_contract_at(gl.message.contract_address).emit(on='finalized').child_ping()

    @gl.public.write
    def child_ping(self) -> None:
        self.ping_count += u256(1)

    @gl.public.view
    def get_state(self) -> str:
        return json.dumps({'last_result': self.last_result, 'ping_count': str(int(self.ping_count))}, sort_keys=True)
