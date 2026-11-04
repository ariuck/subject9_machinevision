"""Run lesson 7 from the project root and preserve every step's log.

Usage: python src/day07_run_all.py
Re-running regenerates lesson 7 derived datasets/results; originals are preserved.
"""
from pathlib import Path
import datetime
import json
import os
import platform
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]

def main():
    os.chdir(ROOT)
    logs = ROOT / 'reports/day07_logs'
    logs.mkdir(parents=True, exist_ok=True)
    # Limit CPU oversubscription for small single-image inference batches.
    env = os.environ.copy()
    env.setdefault('OMP_NUM_THREADS', '4')
    env.setdefault('MKL_NUM_THREADS', '4')
    env['PYTHONUTF8'] = '1'
    env['PYTHONIOENCODING'] = 'utf-8'
    state = {
        'started_at': datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'platform': platform.platform(), 'python': sys.version,
        'status': 'running', 'steps': [],
    }
    status_file = ROOT / 'reports/day07_run_status.json'
    def save():
        status_file.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding='utf-8')
    save()
    for number in range(50, 62):
        files = list((ROOT / 'src').glob(f'{number}_day07_*.py'))
        if len(files) != 1:
            raise RuntimeError(f'Expected one script for step {number}: {files}')
        source = files[0]
        print(f'RUN {source.name}', flush=True)
        with (logs / f'{source.stem}.log').open('w', encoding='utf-8') as log:
            result = subprocess.run([sys.executable, '-u', str(source)], cwd=ROOT,
                                    env=env, stdout=log, stderr=subprocess.STDOUT)
        state['steps'].append({'script': source.name, 'returncode': result.returncode})
        if result.returncode:
            state['status'] = 'failed'
            save()
            print((logs / f'{source.stem}.log').read_text(encoding='utf-8'), flush=True)
            raise SystemExit(result.returncode)
        save()
    from day07_finish_reports import finish_reports
    finish_reports(ROOT)
    state['status'] = 'complete'
    state['finished_at'] = datetime.datetime.now(datetime.timezone.utc).isoformat()
    save()
    print('Day07 complete. See reports/day07_test_metrics.md', flush=True)

if __name__ == '__main__':
    main()
