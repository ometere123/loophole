import pytest,hashlib,json

def attack(cid,sender,salt='abcd012345678901',scenario=None):
    scenario=scenario or 'I will repeat meaningless words over one hundred times with the hashtag, farming a reward without creating original content.'
    quote='Every member who publishes a post of at least 100 words'
    impact='The post meets the length rule but violates the original-educational-contribution objective.'
    pre='|'.join([str(cid),str(sender).lower(),salt,scenario,quote,impact])
    return hashlib.sha256(pre.encode()).hexdigest(),(salt,scenario,quote,impact)


def test_creation_lock_and_binding(funded):
    w=funded;c=json.loads(w.vault.get_challenge(1))
    assert c['prize_wei']==str(2*10**18) and c['organizer']==w.owner
    assert w.vault.total_locked==2*10**18
    assert json.loads(w.judge.get_configuration())['vault']==w.vaddr
    with pytest.raises(Exception,match='binding forbidden'):
        w.run(w.jaddr,w.owner,'bind_vault',w.vaddr)
    with pytest.raises(Exception,match='invalid policy|incomplete policy'):
        w.run(w.vaddr,w.owner,'create_challenge','x','not good','short','', 'CONTENT',86400,10**16,value=10**18)

def test_commit_reveal_judge_settlement_and_no_double_payout(funded):
    w=funded;digest,payload=attack(1,w.alice)
    w.run(w.vaddr,w.alice,'commit_attempt',1,digest,value=10**16)
    assert json.loads(w.vault.get_attempt(1))['status']=='COMMITTED'
    with pytest.raises(Exception,match='commitment does not match'):
        w.run(w.vaddr,w.alice,'reveal_attempt',1,'other-salt-xxxxxxxx',*payload[1:])
    with pytest.raises(Exception,match='original challenger'):
        w.run(w.vaddr,w.bob,'reveal_attempt',1,*payload)
    w.run(w.vaddr,w.alice,'reveal_attempt',1,*payload)
    w.run(w.vaddr,w.bob,'start_review',1)
    assert json.loads(w.vault.get_attempt(1))['status']=='REVIEWING'
    with pytest.raises(Exception,match='forged'):
        w.run(w.vaddr,w.bob,'record_verdict',1,1,1,'0'*64,'VALID','forged',True,True,True)
    w.flush()
    c=json.loads(w.vault.get_challenge(1));a=json.loads(w.vault.get_attempt(1))
    assert c['status']=='WON' and c['winner']==w.alice
    assert a['verdict']=='VALID'
    assert w.vault.get_credit(w.alice)==2*10**18+10**16
    assert w.vault.total_credit==2*10**18+10**16
    assert w.vault.total_locked==0
    w.run(w.vaddr,w.jaddr,'record_verdict',1,1,1,a['evidence_hash'],'VALID','duplicate',True,True,True)
    assert w.vault.get_credit(w.alice)==2*10**18+10**16
    with pytest.raises(Exception,match='busy or closed'):
        w.run(w.vaddr,w.bob,'start_review',1)

def test_invalid_awards_bond_organizer_and_retains_bounty(funded):
    w=funded;digest,data=attack(1,w.alice)
    w.run(w.vaddr,w.alice,'commit_attempt',1,digest,value=10**16)
    w.run(w.vaddr,w.alice,'reveal_attempt',1,*data)
    w.gl.nondet.answer='{"verdict":"INVALID","letter":false,"purpose":true,"feasible":true,"reason":"The action is expressly barred by the published rule and is not eligible."}'
    w.run(w.vaddr,w.bob,'start_review',1);w.flush()
    c=json.loads(w.vault.get_challenge(1))
    assert c['status']=='OPEN' and c['active_attempt']=='0'
    assert json.loads(w.vault.get_attempt(1))['status']=='INVALID_PENDING'
    assert w.vault.get_credit(w.owner)==0
    a=json.loads(w.vault.get_attempt(1));a['appeal_deadline']-=2*86400;w.vault.attempts[1]=json.dumps(a)
    w.run(w.vaddr,w.bob,'finalize_invalid',1)
    assert w.vault.get_credit(w.owner)==10**16 and w.vault.total_locked==2*10**18

def test_inconclusive_returns_bond_without_releasing_bounty(funded):
    w=funded;digest,data=attack(1,w.alice)
    w.run(w.vaddr,w.alice,'commit_attempt',1,digest,value=10**16)
    w.run(w.vaddr,w.alice,'reveal_attempt',1,*data)
    w.gl.nondet.answer='{"verdict":"INCONCLUSIVE","letter":false,"purpose":false,"feasible":false,"reason":"A missing eligibility definition prevents demonstrating the claimed attack."}'
    w.run(w.vaddr,w.owner,'start_review',1);w.flush()
    assert w.vault.get_credit(w.alice)==10**16
    assert w.vault.total_locked==2*10**18

def test_repeated_attempt_limit_and_refund(funded):
    w=funded
    for i in range(2):
        d,_=attack(1,w.alice,salt=f'012345678{i}abcdef')
        w.run(w.vaddr,w.alice,'commit_attempt',1,d,value=10**16)
    with pytest.raises(Exception,match='two outstanding attempts'):
        w.run(w.vaddr,w.alice,'commit_attempt',1,'a'*64,value=10**16)
    c=json.loads(w.vault.get_challenge(1));c['ends_at']-=40*86400;c['reveal_deadline']-=40*86400;w.vault.challenges[1]=json.dumps(c)
    w.run(w.vaddr,w.bob,'settle_remaining_bond',1)
    assert w.vault.get_credit(w.owner)==10**16
    with pytest.raises(Exception,match='bond is not eligible'):
        w.run(w.vaddr,w.bob,'settle_remaining_bond',1)
    w.run(w.vaddr,w.bob,'refund_unwon',1)
    assert json.loads(w.vault.get_challenge(1))['status']=='REFUNDED'
    assert w.vault.get_credit(w.owner)==2*10**18+2*10**16
    assert w.vault.total_locked==0
    with pytest.raises(Exception,match='bond is not eligible'):
        w.run(w.vaddr,w.bob,'settle_remaining_bond',2)
    assert w.vault.total_locked==0

def test_withdraw_is_one_shot_and_not_proven_child_execution(funded):
    w=funded;d,p=attack(1,w.alice)
    w.run(w.vaddr,w.alice,'commit_attempt',1,d,value=10**16)
    w.run(w.vaddr,w.alice,'reveal_attempt',1,*p)
    w.run(w.vaddr,w.bob,'start_review',1);w.flush()
    w.run(w.vaddr,w.alice,'withdraw')
    out=json.loads(w.vault.get_withdrawal(1))
    assert out['status']=='TRANSFER_EMITTED_UNVERIFIED'
    assert w.vault.get_credit(w.alice)==0 and w.vault.total_credit==0
    assert w.gl.pending[0][0]=='TRANSFER'
    with pytest.raises(Exception,match='no claimable'):
        w.run(w.vaddr,w.alice,'withdraw')

def test_queued_review_timeout_blocks_stale_success(funded):
    w=funded;d,p=attack(1,w.alice)
    w.run(w.vaddr,w.alice,'commit_attempt',1,d,value=10**16)
    w.run(w.vaddr,w.alice,'reveal_attempt',1,*p)
    w.run(w.vaddr,w.bob,'start_review',1)
    c=json.loads(w.vault.get_challenge(1));c['review_started']-=6*86400;w.vault.challenges[1]=json.dumps(c)
    w.run(w.vaddr,w.bob,'recover_stalled_review',1)
    w.flush()
    assert json.loads(w.vault.get_challenge(1))['status']=='OPEN'
    assert w.vault.get_credit(w.alice)==10**16
    assert w.vault.total_locked==2*10**18

def test_commitment_domain_separated_by_account_and_challenge(funded):
    w=funded;d,p=attack(1,w.alice)
    w.run(w.vaddr,w.alice,'commit_attempt',1,d,value=10**16)
    with pytest.raises(Exception,match='original challenger'):
        w.run(w.vaddr,w.bob,'reveal_attempt',1,*p)
    assert attack(1,w.alice)[0]!=attack(1,w.bob)[0]
    assert attack(1,w.alice)[0]!=attack(2,w.alice)[0]

def test_organizer_cannot_be_challenger_and_exact_bond(funded):
    w=funded;d,p=attack(1,w.alice)
    with pytest.raises(Exception,match='organizer'):
        w.run(w.vaddr,w.owner,'commit_attempt',1,d,value=10**16)
    with pytest.raises(Exception,match='exact bond'):
        w.run(w.vaddr,w.alice,'commit_attempt',1,d,value=2*10**16)
    assert w.vault.attempt_count==0

def test_quote_must_exist_in_frozen_policy(funded):
    w=funded
    scenario='A detailed attack sequence containing many steps showing an unintended loophole.'
    quote='This phrase is not part of the actual frozen source.'
    impact='This behavior would wrongly unlock a reward without original content.'
    salt='specialabcd9876'
    pre='|'.join(['1',str(w.alice).lower(),salt,scenario,quote,impact])
    digest=hashlib.sha256(pre.encode()).hexdigest()
    w.run(w.vaddr,w.alice,'commit_attempt',1,digest,value=10**16)
    with pytest.raises(Exception,match='quoted rule passage'):
        w.run(w.vaddr,w.alice,'reveal_attempt',1,salt,scenario,quote,impact)

def test_early_winner_releases_other_hidden_commitment(funded):
    w=funded;d,p=attack(1,w.alice)
    w.run(w.vaddr,w.alice,'commit_attempt',1,d,value=10**16)
    d2,_=attack(1,w.bob)
    w.run(w.vaddr,w.bob,'commit_attempt',1,d2,value=10**16)
    w.run(w.vaddr,w.alice,'reveal_attempt',1,*p)
    w.run(w.vaddr,w.bob,'start_review',1);w.flush()
    assert json.loads(w.vault.get_challenge(1))['status']=='WON'
    w.run(w.vaddr,w.bob,'settle_remaining_bond',2)
    assert w.vault.get_credit(w.bob)==10**16
    assert w.vault.total_locked==0
