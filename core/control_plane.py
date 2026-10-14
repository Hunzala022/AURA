"""Plan -> validate -> permission -> policy -> approval -> execute -> verify -> audit."""
import json
import time
import requests
from core.schema import ToolCallSchema
from core.prompt import BASE_SYSTEM_PROMPT
from core.tools import AGENT_REGISTRY, TOOLS, validate_parameters
from core.policy import evaluate_risk, authorize_high_risk_action
from core.verification import before_action, verify_action
from core.sanitization import sanitize_content
OLLAMA_API='http://localhost:11434'
MODEL_NAME='aura-qwen:latest'
PLAN_OPTIONS={'temperature':0,'num_ctx':4096,'num_predict':768}

def _model_request(messages, purpose='plan', *, schema=None):
    """Shared production inference with opt-in real first-token measurements."""
    from core.planning_trace import record_call
    started=time.perf_counter();first=None;content='';final={};raw=None;error=None;response=None
    try:
        response=requests.post(OLLAMA_API+'/api/chat',json={'model':MODEL_NAME,'messages':messages,'stream':True,'think':False,'format':schema or ToolCallSchema.model_json_schema(),'options':PLAN_OPTIONS},timeout=180,stream=True)
        response.raise_for_status()
        for line in response.iter_lines():
            if time.perf_counter()-started>180:raise TimeoutError('Planning deadline exceeded')
            if not line:continue
            chunk=json.loads(line)
            if chunk.get('error'):raise ValueError('Inference backend rejected request')
            message=chunk.get('message',{})
            if first is None and (message.get('content') or message.get('thinking')):
                first=time.perf_counter()-started
            content+=message.get('content','')
            if chunk.get('done'):final=chunk
        if not final:raise ValueError('Incomplete inference stream')
        raw=json.loads(content)
        return raw
    except Exception as exc:
        error=type(exc).__name__
        raise
    finally:
        if response is not None:response.close()
        duration=final.get('eval_duration')
        record_call({'purpose':purpose,'elapsed_seconds':time.perf_counter()-started,
                     'request_started_monotonic':started,
                     'ttft_seconds':first,'raw_plan':raw,'raw_text':content if raw is None else None,
                     'error':error,'eval_count':final.get('eval_count'),
                     'tokens_per_second':final.get('eval_count',0)/(duration/1e9) if duration else None,
                     'done_reason':final.get('done_reason'),
                     'prompt_eval_count':final.get('prompt_eval_count')})
class TaskStateManager:
    def __init__(self):
        self.current_task=None; self.plan=[]; self.current_step=0; self.history=[]
    def load_plan(self,task,plan):
        self.current_task=task; self.plan=plan; self.current_step=0; self.history=[]
    def get_next_step(self):
        return self.plan[self.current_step] if self.current_step<len(self.plan) else None
    def mark_step_complete(self,result):
        self.history.append({'step':self.current_step+1,'result':result});self.current_step+=1
def generate_plan(prompt_text,memory_context=''):
    """Model chooses decisions/tools/arguments; compile only derived metadata."""
    from core.planning_proposal import propose
    return propose(prompt_text,memory_context)

def _memory():
    from core.storage_selection import production_memory
    return production_memory()
def execute_pipeline(user_prompt, *, memory_factory=None, allowed_agents=None):
    from agents.browser_agent import browser_session
    with browser_session():
        return _execute_pipeline(user_prompt,memory_factory=memory_factory,allowed_agents=allowed_agents)

def _execute_pipeline(user_prompt, *, memory_factory=None, allowed_agents=None):
    """Trusted caller supplies permission scope/dependencies; they are never model fields."""
    start=time.perf_counter()
    result={'decision':None,'status':'ERROR','success':False,'steps':[],'error':None,'warnings':[]}
    memory=None
    def finish(status,error=None):
        result['status']=status;result['success']=status=='COMPLETED';result['error']=error
        result['latency_seconds']=time.perf_counter()-start
        if memory is not None:
            try:memory.log_session('control_plane',user_prompt,json.dumps(result))
            except Exception:
                result.update(status='AUDIT_ERROR',success=False,error='Final session audit failed; side effects may already exist')
        return result
    try:
        memory=(memory_factory or _memory)()
        if memory is None: return finish('AUDIT_ERROR','Audit storage unavailable')
    except Exception:
        return finish('AUDIT_ERROR','Audit storage unavailable')
    context=''
    try:context='\n'.join(memory.retrieve_memory(user_prompt,n_results=2))
    except Exception:result['warnings'].append('Memory retrieval unavailable')
    raw=generate_plan(user_prompt,context)
    if raw is None:return finish('PLAN_ERROR','Planner unavailable or invalid response')
    try:
        plan=ToolCallSchema.model_validate(raw)
        scope=set(AGENT_REGISTRY) if allowed_agents is None else set(allowed_agents)
        for step in plan.plan:
            if step.agent not in scope:raise PermissionError('Agent is outside caller permissions')
            if step.tool not in AGENT_REGISTRY.get(step.agent,{}):raise PermissionError('Tool is not registered to agent')
    except Exception:
        return finish('INVALID_PLAN','Plan failed contract or agent permission validation')
    result['decision']=plan.decision
    if plan.decision!='EXECUTE':return finish(plan.decision)
    outputs={}
    for step in plan.plan:
        params=step.parameters
        record={'step':step.step,'tool':step.tool,'agent':step.agent,'risk':None,'executed':False,'verified':False,'status':'PENDING'}
        result['steps'].append(record)
        try:
            params={k:outputs[v['from_step']] if isinstance(v,dict) else v for k,v in params.items()}
            params=validate_parameters(step.tool,params)
            risk=evaluate_risk(step.tool,params);record['risk']=risk
            memory.log_audit_trail(step.tool,risk,params,'ATTEMPTED')
            if risk=='HIGH':
                approved=authorize_high_risk_action({'tool':step.tool,'parameters':params,'reasoning':step.reasoning})
                memory.log_audit_trail(step.tool,risk,params,'APPROVED_BY_HITL' if approved is True else 'DENIED_BY_HITL')
                if approved is not True:
                    record['status']='BLOCKED';return finish('BLOCKED')
            else:memory.log_audit_trail(step.tool,risk,params,'APPROVED_BY_POLICY')
            before=before_action(step.tool,params)
            record['executed']=True
            success,output=AGENT_REGISTRY[step.agent][step.tool](params)
            if success is not True:
                record['status']='FAILED'
                memory.log_audit_trail(step.tool,risk,params,'EXECUTION_FAILED')
                return finish('FAILED',str(output))
            if not verify_action(step.tool,params,output,before):
                record['status']='VERIFICATION_FAILED'
                memory.log_audit_trail(step.tool,risk,params,'VERIFICATION_FAILED')
                return finish('VERIFICATION_FAILED','Postcondition not satisfied')
            record.update(status='VERIFIED',verified=True,result=output)
            outputs[step.step]=output
            memory.log_audit_trail(step.tool,risk,params,'VERIFIED')
        except Exception as error:
            record['status']='ERROR'
            try:memory.log_audit_trail(step.tool,record['risk'] or 'UNKNOWN',params,'ERROR')
            except Exception:pass
            return finish('ERROR',type(error).__name__+': execution or audit failed; inspect completed steps')
    return finish('COMPLETED')
