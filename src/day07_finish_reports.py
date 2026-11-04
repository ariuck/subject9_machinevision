"""Summarize measured results without substituting the textbook example values."""
from pathlib import Path
import csv
import json
import re

def read_csv(path):
    with path.open(encoding='utf-8-sig', newline='') as f:
        return list(csv.DictReader(f))

def finish_reports(root):
    reports = root / 'reports'
    rows = read_csv(reports / 'day07_anomaly_scores.csv')
    challenge = read_csv(reports / 'day07_challenge_results.csv')
    rules = json.loads((root / 'configs/day07_anomaly_rules.json').read_text(encoding='utf-8'))
    threshold = rules['anomaly_threshold']
    counts = {t:sum(r['error_type'] == t for r in rows) for t in ['TP', 'TN', 'FP', 'FN']}
    assert len(rows) == 83 and sum(counts.values()) == 83
    assert sum(r['actual'] == 'Normal' for r in rows) == 20
    assert all(float(r['threshold']) == threshold for r in rows + challenge)
    split = json.loads((reports / 'day07_dataset_split.json').read_text(encoding='utf-8'))
    assert len(split['train']) == 167 and len(split['validation']) == 42
    assert not set(split['train']) & set(split['validation'])
    reasons = {
        'FP': '정상 이미지의 조명·색·위치 차이가 정상 평균 특징에서 벗어났을 가능성. Score만으로 원인을 확정할 수 없다.',
        'FN': '작은 국소 결함이 전체 특징 평균에서 약해졌거나 중심 Crop 밖에 있었을 가능성. 원본·Mask·Heatmap을 함께 확인해야 한다.',
    }
    lines = ['# Day07 Failure Analysis', '', '실제 실행 CSV 기반 자동 요약. 아래 원인은 가설이며 학생의 육안 확인은 별도이다.', '']
    for error in ['FP','FN']:
        selected = [r for r in rows if r['error_type'] == error]
        lines += [f'## Test {error}', '']
        if selected:
            r = selected[0]
            lines += [f'- File: {r["file"]}', f'- Score: {r["anomaly_score"]}', f'- Threshold: {threshold}', f'- 원인 추정: {reasons[error]}', '']
        else:
            lines += ['이번 실행에는 해당 실패가 없다.', '']
    lines += ['## Challenge FP', '']
    failures = [r for r in challenge if r['result'] == 'FP']
    for r in failures:
        lines += [f'- {r["file"]}: Score {r["anomaly_score"]} > {threshold}']
    if not failures:
        lines += ['이번 실행에는 Challenge FP가 없다.']
    lines += ['', '원인 추정: 촬영 조건 변화가 사전학습 특징을 바꾸어 정상 평균과의 거리를 키웠을 가능성이 있다.', '',
              '## 한 줄 정리', '', '큰 파손·오염과 작은 결함의 검출 차이는 종류별 성능표에서 확인한다. 촬영 조건 변화도 오탐 원인이 될 수 있다.', '',
              '개선 후보: 촬영·정렬 안정화, 정상 조건 다양화, 국소 특징 기반 검출. 개선 후에는 새로운 검증·Test로 평가하고 기존 Test에 맞춰 Threshold를 조정하지 않는다.', '',
              '## Heatmap 해석', '', 'Heatmap은 정상 특징과의 차이이고 Ground Truth는 실제 결함 위치이다. 색은 이미지별 정규화되어 이미지 간 절대 점수 비교용이 아니다.',
              '사전학습 전처리의 Center Crop 좌표에 맞추어 원본 위에 복원했다. Crop 밖 영역은 모델이 보지 않은 영역이며 Overlay에서 원본으로 남겨 둔다.', '']
    (reports / 'day07_failure_analysis.md').write_text('\n'.join(lines), encoding='utf-8')
    tp,tn,fp,fn = (counts[t] for t in ['TP','TN','FP','FN'])
    accuracy = (tp+tn)/len(rows)
    precision = tp/(tp+fp) if tp+fp else 0
    recall = tp/(tp+fn) if tp+fn else 0
    summary = f'''## Day 07 — Anomaly Detection

### Dataset / Baseline

- MVTec AD bottle: Normal Train 167 / Validation 42 / Test Normal 20 / Anomaly 63
- Split seed: 42. 원본 보존, Train / Validation 중복 없음.
- ImageNet 사전학습 ResNet18 layer3, 정상 Train 특징 평균, Euclidean distance
- 전처리: 짧은 변 256 Resize → 224 Center Crop → ImageNet Normalize
- Rule: {rules['baseline_version']}, 정상 Validation 95 Percentile, Threshold {threshold}
- Test와 Challenge는 동일 Frozen Rule 사용. 교재 예시 수치를 복사하지 않고 실제 실행 결과를 기록했다.

### Test Result

- Accuracy: {accuracy:.4f}, Precision: {precision:.4f}, Recall: {recall:.4f}
- TP {tp} / TN {tn} / FP {fp} / FN {fn}

### Challenge

'''
    summary += '\n'.join(f'- {r["file"]}: {r["result"]} (Score {r["anomaly_score"]})' for r in challenge)
    summary += '''

### 실행과 결과

```bash
source .venv/bin/activate
python src/day07_run_all.py
```

개별 실습은 `src/50_day07_check_anomaly_env.py`부터 `src/61_day07_mini_challenge.py`까지 번호 순서로 실행한다.
전체 재실행은 7일차 생성 데이터와 결과를 다시 만든다. `samples/day07/original/bottle`은 유지한다.
Mini Challenge는 `61`번 파일의 Dark / Blur / Rotation 값을 바꾸어 재실행할 수 있다.

- Rule: `configs/day07_anomaly_rules.json`
- Split 기록: `reports/day07_dataset_split.json`
- Test: `reports/day07_anomaly_scores.csv`, `reports/day07_test_metrics.md`
- Challenge: `reports/day07_challenge_results.csv`
- Mini Challenge: `reports/day07_mini_challenge.md`
- 실패 분석: `reports/day07_failure_analysis.md`
- 실행 환경·상태: `reports/day07_run_status.json`, `reports/day07_logs/`
- 이미지: `outputs/day07/fp`, `outputs/day07/fn`, `outputs/day07/heatmap`

정상 기준 → Validation Threshold → Rule Freeze → Test → 환경 변화 실험 흐름을 구현했다.
작은 결함과 촬영 조건에 대한 한계는 실패 분석에 기록했다. 개념 이해와 개인 예상·육안 분석은 학생이 직접 확인한다.
'''
    readme = root / 'README.md'
    text = readme.read_text(encoding='utf-8')
    marker = '\n## Day 07 — Anomaly Detection'
    if marker in text:
        before, existing = text.split(marker, 1)
        following = re.search(r'(?m)^## Day \d+', existing)
        tail = existing[following.start():] if following else ''
        updated = before.rstrip() + '\n\n' + summary.rstrip()
        if tail:
            updated += '\n\n---\n\n' + tail
    else:
        updated = text.rstrip() + '\n\n---\n\n' + summary
    readme.write_text(updated, encoding='utf-8')

if __name__ == '__main__':
    finish_reports(Path(__file__).resolve().parents[1])
