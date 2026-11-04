"""Execute Day08 from the project root; re-running replaces generated Day08 data."""
from pathlib import Path
import datetime
import hashlib
import json
import os
import platform
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
def main():
    os.chdir(ROOT)
    logs=ROOT/'reports/day08_logs'; logs.mkdir(parents=True,exist_ok=True)
    env=os.environ.copy()
    env.setdefault('OMP_NUM_THREADS','4'); env.setdefault('MKL_NUM_THREADS','4')
    env['PYTHONUTF8']='1'; env['PYTHONIOENCODING']='utf-8'
    state={'started_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),
           'platform':platform.platform(),'python':sys.version,'status':'running','steps':[]}
    frozen={}
    def digest(path): return hashlib.sha256((ROOT/path).read_bytes()).hexdigest()
    def save():
        (ROOT/'reports/day08_run_status.json').write_text(json.dumps(state,ensure_ascii=False,indent=2),encoding='utf-8')
    save()
    for number in range(62,71):
        sources=list((ROOT/'src').glob(f'{number}_day08_*.py'))
        if len(sources)!=1: raise RuntimeError(f'Expected one script for {number}')
        source=sources[0]; print(f'RUN {source.name}',flush=True)
        log_path=logs/f'{source.stem}.log'
        with log_path.open('w',encoding='utf-8') as log:
            result=subprocess.run([sys.executable,'-u',str(source)],cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT)
        state['steps'].append({'script':source.name,'returncode':result.returncode})
        if result.returncode:
            state['status']='failed'; save(); print(log_path.read_text(encoding='utf-8')); raise SystemExit(result.returncode)
        if number==64:
            for name in ['configs/day08_one_shot_rules.json','artifacts/day08/one_shot_reference.npy']:
                frozen[name]=digest(name)
        if number==66:
            for name in ['configs/day08_fewshot_config.json','artifacts/day08/fewshot_prototypes.npz']:
                frozen[name]=digest(name)
        for name,expected in frozen.items():
            if digest(name)!=expected:
                state['status']='failed'; save(); raise RuntimeError(f'Frozen file changed: {name}')
        save()
    from day08_finish_reports import finish_reports
    finish_reports(ROOT)
    state.update(status='complete',frozen_files_sha256=frozen,
                 finished_at=datetime.datetime.now(datetime.timezone.utc).isoformat())
    save(); print('Day08 complete. See reports/day08_method_comparison.csv',flush=True)

if __name__=='__main__': main()
