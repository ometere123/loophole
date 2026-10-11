# { "Depends": "py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6" }
from genlayer import *
import json

# Separate diagnostic sender for the RuleVault -> GapJudge boundary. This is
# never part of the LOOPHOLE production deployment.


class CrossContractRelay(gl.Contract):
    target: Address
    request_count: u256

    def __init__(self, target: str):
        if gl.message.chain_id != u256(61999):
            raise gl.vm.UserError('Studionet 61999 only')
        candidate = target if isinstance(target, Address) else Address(target)
        if candidate == gl.message.contract_address:
            raise gl.vm.UserError('relay target must be external')
        self.target = candidate
        self.request_count = u256(0)

    @gl.public.write
    def trigger_probe(self, prompt: str) -> None:
        self.request_count += u256(1)
        gl.get_contract_at(self.target).emit(on='finalized').direct_judgment(prompt)

    @gl.public.view
    def get_state(self) -> str:
        return json.dumps({'target': self.target.as_hex, 'request_count': str(int(self.request_count))}, sort_keys=True)
