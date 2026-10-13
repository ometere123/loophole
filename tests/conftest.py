"""Deterministic protocol simulator for Python state-machine tests.
Not a substitute for real GenVM Direct Mode or chain integration tests.
"""
import sys,types,importlib.util,pytest
from pathlib import Path
from dataclasses import dataclass

BASE = Path(__file__).resolve().parents[1]

class Address(str):
    def __new__(cls,s):
        if not str(s).startswith('0x') or len(str(s)) != 42: raise ValueError('bad address')
        return str.__new__(cls, str(s).lower())
    @property
    def as_hex(self): return str(self)

class Decorators:
    @staticmethod
    def write(fn): return fn
    @staticmethod
    def view(fn): return fn
Decorators.write.payable = lambda fn:fn

class UserError(Exception): pass
class Return:
    def __init__(self,calldata):self.calldata=calldata

class FakeWeb:
    responses = {}

    @classmethod
    def get(cls, url):
        status, body = cls.responses[url]
        return types.SimpleNamespace(status=status, body=body)

class GlFake:
    Contract=object
    public=Decorators()
    class evm:
        @staticmethod
        def contract_interface(c):
            def construct(addr):
                return EvmProxy(addr)
            return construct
    class vm:
        UserError=UserError
        Return=Return
        @staticmethod
        def run_nondet_unsafe(leader,validate):
            result=leader()
            if not validate(Return(result)): raise UserError('independent validator disagreed')
            return result
    class nondet:
        answer='{"verdict":"VALID","letter":true,"purpose":true,"feasible":true,"reason":"Exact written rule permits repeated engagement farming despite the explicit purpose."}'
        answers=[]
        prompts=[]
        web=FakeWeb
        @classmethod
        def exec_prompt(cls,prompt,**kwargs):
            cls.prompts.append(prompt)
            if cls.answers:
                return cls.answers.pop(0)
            return cls.answer
    def __init__(self):
        self.address=''
        self.contracts={}
        self.pending=[]
        self.message=types.SimpleNamespace(sender_address=Address('0x'+'1'*40),contract_address=Address('0x'+'1'*40),value=0,chain_id=61999)
    def get_contract_at(self,address):return ICProxy(str(address),self)

fake = GlFake()
class ICProxy:
    def __init__(self,addr,gl):self.addr=addr;self.gl=gl
    def emit(self,*,on='finalized',value=0):
        assert on=='finalized'
        return ChildProxy(self.addr,self.gl,external=False)
class EvmProxy:
    def __init__(self,addr):self.addr=str(addr)
    def emit_transfer(self,*,value):fake.pending.append(('TRANSFER',fake.message.contract_address,self.addr,int(value),()))
class ChildProxy:
    def __init__(self,addr,gl,external):self.addr=addr;self.gl=gl
    def __getattr__(self,name):
        def call(*args):self.gl.pending.append((name,str(self.gl.message.contract_address),self.addr,0,args))
        return call

@pytest.fixture()
def world(monkeypatch):
    module=types.ModuleType('genlayer');module.Address=Address;module.TreeMap=dict;module.u256=int;module.gl=fake
    monkeypatch.setitem(sys.modules,'genlayer',module)
    fake.__init__();fake.nondet.answers=[];fake.nondet.prompts=[];fake.nondet.web.responses={};fake.nondet.answer='{"verdict":"VALID","letter":true,"purpose":true,"feasible":true,"reason":"Exact written rule permits repeated engagement farming despite the explicit purpose."}'
    def load(path,name):
        spec=importlib.util.spec_from_file_location(name,BASE/'contracts'/path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
    j=load('historical/GapJudge.py','fake_gapjudge').GapJudge
    v=load('historical/RuleVault.py','fake_rulevault').RuleVault
    owner=Address('0x'+'1'*40);alice=Address('0x'+'2'*40);bob=Address('0x'+'3'*40)
    judge_addr=Address('0x'+'a'*40);vault_addr=Address('0x'+'b'*40)
    def run(addr,sender,method,*args,value=0):
        fake.message=types.SimpleNamespace(sender_address=Address(sender),contract_address=Address(addr),origin_address=Address(sender),value=value,chain_id=61999)
        return getattr(fake.contracts[str(addr)],method)(*args)
    def flush():
        while fake.pending:
            name,sender,addr,value,args=fake.pending.pop(0)
            if name=='TRANSFER':continue
            run(addr,sender,name,*args,value=value)
    fake.message=types.SimpleNamespace(sender_address=owner,contract_address=judge_addr,value=0,chain_id=61999)
    judge=j();fake.contracts[str(judge_addr)]=judge
    fake.message=types.SimpleNamespace(sender_address=owner,contract_address=vault_addr,value=0,chain_id=61999)
    vault=v(judge_addr);fake.contracts[str(vault_addr)]=vault
    run(judge_addr,owner,'bind_vault',vault_addr)
    return types.SimpleNamespace(run=run,flush=flush,gl=fake,judge=judge,vault=vault,owner=owner,alice=alice,bob=bob,jaddr=judge_addr,vaddr=vault_addr)

@pytest.fixture
def funded(world):
    w=world
    w.run(w.vaddr,w.owner,'create_challenge','Originality Trap',
        'Reward only genuinely original contributions to this campaign.',
        'Every member who publishes a post of at least 100 words with #OURCAMPAIGN earns points.',
        'Posts must happen during the campaign.','CONTENT',86400,10**16,value=2*10**18)
    return w
