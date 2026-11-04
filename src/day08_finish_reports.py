"""Write reports from measured CSVs. Preserve human/agent visual review separately."""
from pathlib import Path
import csv
import hashlib
import json
import re

def read_csv(path):
    with path.open(encoding='utf-8-sig',newline='') as f: return list(csv.DictReader(f))

def finish_reports(root):
    reports=root/'reports'
    comparison=read_csv(reports/'day08_method_comparison.csv')
    support=read_csv(reports/'day08_support_count_comparison.csv')
    rules=json.loads((root/'configs/day08_one_shot_rules.json').read_text(encoding='utf-8'))
    threshold=rules['similarity_threshold']
    table=['| Method | Accuracy | Precision | Recall | TP | TN | FP | FN |',
           '|---|---:|---:|---:|---:|---:|---:|---:|']
    for r in comparison:
        table.append(f"| {r['method']} | {float(r['accuracy']):.4f} | {float(r['anomaly_precision']):.4f} | {float(r['anomaly_recall']):.4f} | {r['tp']} | {r['tn']} | {r['fp']} | {r['fn']} |")
    analysis=['# Day08 Method Analysis','','실제 실행 CSV에 기반한 에이전트 요약이다. 학생 개인의 설명·판단은 별도이다.','']+table
    analysis += ['', '## 데이터와 방법', '',
       '동일한 Common Query 정상 10장 + broken_small 10장으로 비교했다. 기준·Calibration·Support·Query·합성 원본 역할을 겹치지 않게 분리했다.',
       f'One-shot은 정상 Reference 1장과 별도 정상 Calibration 20장의 Cosine Similarity 하위 5 Percentile {threshold:.9f}를 사용했다. 불량 예제로 기준을 조정하지 않았다.',
       'Few-shot은 정상 5장과 작은 파손 5장의 512차원 정규화 특징 평균으로 Prototype을 만들고 더 유사한 클래스를 선택했다. 모델을 새로 학습하지 않았다.',
       '두 방법 모두 ImageNet ResNet18의 최종 Average Pool 512차원 특징과 224×224 Resize를 사용한다. 7일차의 layer3 특징·Center Crop·평가 데이터와 달라 정확도를 단순 순위로 비교하지 않는다.', '',
       '## 실제 오류 사례', '']
    for method,name in [('One-shot','day08_one_shot_results.csv'),('Few-shot','day08_fewshot_results.csv')]:
        rows=read_csv(reports/name)
        errors=[r for r in rows if r['actual']!=r['predicted']]
        analysis.append(f'### {method}')
        analysis.append('')
        for r in errors[:4]:
            fields=(f"similarity={float(r['similarity']):.6f}" if 'similarity' in r else f"normal_similarity={float(r['normal_similarity']):.6f}, anomaly_similarity={float(r['anomaly_similarity']):.6f}")
            analysis.append(f"- {r['sample_id']}: actual={r['actual']}, predicted={r['predicted']}, {fields}")
        if not errors: analysis.append('이번 Common Query에서는 오류가 없었다.')
        analysis.append('')
    analysis += ['정상 Reference 1장은 정상 변동을 모두 대표하지 못할 수 있다. Few-shot은 Support 구성에 민감하며 전체 특징 평균에서 작은 결함 차이가 약해질 수 있다. 이는 원인 가설이고 결과 숫자만으로 확정할 수 없다.', '',
                '평가 Query는 20장뿐이며 해당 결함·고정 분할에서 얻은 결과이다. Support 수 실험에서도 Query를 바꾸거나 좋은 결과가 나온 Support로 재선택하지 않았다. 실제 도입 성능을 의미하지 않는다.', '',
                '## Zero-shot과 합성 데이터', '',
                'Zero-shot은 대상 작업의 학습 예제 없이 사전학습 지식·텍스트 조건 등을 이용하는 접근이며 이 수업에서는 개념만 다룬다. 정상 Reference를 직접 제공하는 이번 유사도 검사는 One-shot이다.',
                'Cut-Paste는 실제 불량의 Ground Truth Mask로 결함을 추출해 별도 정상 이미지에 합성하는 데이터 보강이다. 생성 이미지가 실제 결함 분포와 다를 수 있는 Domain Gap이 있으며, 합성 후 성능 향상 학습 실험은 이번 범위에 포함하지 않았다.', '']
    (reports/'day08_method_analysis.md').write_text('\n'.join(analysis),encoding='utf-8')

    mini=['# Day08 Mini Challenge','','에이전트가 수행한 실험이다. 학생의 사전 예상·개념 이해·개인 판단을 대신 확인한 것은 아니다.', '',
          '## 1. Support Count 비교', '',
          '사전 예상: Support가 늘면 안정될 수 있지만 Accuracy의 단조 증가와 FP/FN 동시 감소는 보장되지 않는다.',
          '선택: 각 클래스의 Support 파일명 정렬 순서에서 앞 1/3/5장을 사용한다. 동일 Query의 Feature를 재사용한다.', '',
          '| Support / class | Accuracy | FP | FN |','|---:|---:|---:|---:|']
    for r in support: mini.append(f"| {r['support_count']} | {float(r['accuracy']):.4f} | {r['FP']} | {r['FN']} |")
    mini += ['', '세 실험은 고정된 한 Support 집합의 중첩 부분집합이다. 장수와 포함된 이미지 구성이 함께 달라지므로 일반적인 성능 증가를 증명하지 않는다.', '',
             '## 2. contamination Synthetic Defect', '',
             '별도 정상 이미지 5장, 오염 원본 2장과 Mask로 합성 5장을 생성했다. Scale 0.6~1.0, Rotation -10~10°, Seed 43.',
             '대표 이미지와 자연스러움·경계 품질 판단은 `day08_synthetic_quality_check.md`의 실제 이미지 검수 기록을 확인한다.', '',
             '## 3. 상황별 방법 선택', '',
             '| 데이터 상황 | 먼저 고려할 방법 | 이유 |','|---|---|---|',
             '| 정상 충분 / 불량 없음 | 정상 기반 Anomaly Detection | 정상 범위를 기준으로 차이를 찾는다. |',
             '| 확실한 정상 기준 1장 + 정상 Calibration | One-shot | 한 장과의 유사도를 별도 정상 데이터로 교정한다. |',
             '| 정상·불량 예제가 각각 소수 | Few-shot | 클래스별 예제로 Prototype을 만든다. |',
             '| 실제 불량 부족 | Defect Generation + 실제 데이터 추가 수집 | 합성으로 보강하되 실제 데이터로 평가한다. |', '',
             '## 한 줄 결론', '', '단순 이미지 수보다 데이터의 역할·대표성·평가 분리와 실제 오류를 함께 확인하는 것이 중요하다.', '']
    review_path=reports/'day08_visual_review.json'
    quality=['# Day08 Synthetic Quality Check','','에이전트의 시각 검수 기록이며 학생 개인의 품질 판단은 별도이다.','']
    if review_path.exists():
        review=json.loads(review_path.read_text(encoding='utf-8'))
        valid=all((root/p).is_file() and hashlib.sha256((root/p).read_bytes()).hexdigest()==h for p,h in review['files_sha256'].items())
        if valid:
            quality += review['markdown_lines']
            mini += ['', '### 이미지 검수 결과', ''] + review['mini_lines']
        else:
            quality += ['생성 이미지가 검수 당시와 달라졌다. 재검수 필요.']
    else:
        quality += ['시각 검수 대기. 이미지 수와 파일 정상 여부는 자동 검증과 별개이다.']
    quality += ['', '합성 패치의 위치·크기·색 경계가 실제 제품 결함과 다를 수 있다. 보강 후보로만 다루고 실제 검사 성능 향상은 별도 실험으로 확인한다.', '']
    (reports/'day08_synthetic_quality_check.md').write_text('\n'.join(quality),encoding='utf-8')
    (reports/'day08_mini_challenge.md').write_text('\n'.join(mini),encoding='utf-8')

    summary='''## Day 08 — Low-Data Inspection

### 데이터와 Baseline

- MVTec bottle 원본 재사용, Seed 42, 역할 간 중복 방지
- One-shot: 정상 Reference 1장 + 별도 정상 Calibration 20장
- Few-shot: Normal 5장 + broken_small 5장 Support
- 동일 Common Query: Normal 10장 + broken_small 10장
- ImageNet ResNet18 Average Pool 512차원, L2 Normalize, Cosine Similarity
- One-shot Threshold: '''+f'{threshold:.9f}'+''' (정상 Calibration 5 Percentile)
- Zero-shot은 개념만 정리한다. One-shot / Few-shot은 사전학습 특징을 활용하며 모델 재학습은 하지 않았다.

### 실제 비교 결과

'''+ '\n'.join(table)+'''

### Defect Generation / Mini Challenge

- Ground Truth Mask + Cut-Paste: broken_small 합성 20장, Metadata 저장
- Support 1 / 3 / 5장 실험, 같은 Query 사용
- contamination 합성 5장: Scale 0.6~1.0, Rotation ±10°
- 시각 품질 검수는 보고서에서 확인. 합성이 실제 성능을 개선했다는 결론은 내리지 않았다.

### 실행

```bash
source .venv/bin/activate
python src/day08_run_all.py
```

`62~69`번은 교재 본 실습, `70`번은 Mini Challenge다. 전체 재실행은 8일차 생성 데이터와 결과를 다시 만든다.
7일차 원본과 결과는 유지한다. 7일차의 특징 추출·평가 구성이 달라 정확도를 단순 순위로 비교하지 않는다.

### 결과 파일

- `reports/day08_dataset_summary.md`, `reports/day08_dataset_split.json`
- `configs/day08_one_shot_rules.json`, `configs/day08_fewshot_config.json`
- `artifacts/day08/one_shot_reference.npy`, `artifacts/day08/fewshot_prototypes.npz`
- `reports/day08_one_shot_results.csv`, `reports/day08_fewshot_results.csv`
- `reports/day08_method_comparison.csv`, `reports/day08_method_analysis.md`
- `reports/day08_defect_metadata.csv`, `reports/day08_contamination_metadata.csv`
- `reports/day08_synthetic_quality_check.md`, `reports/day08_mini_challenge.md`
- `reports/day08_support_count_comparison.csv`
- `outputs/day08/cutpaste/generated/`, `outputs/day08/mini_challenge/generated/`
- `reports/day08_run_status.json`, `reports/day08_logs/`, `reports/day08_verification.json`

개인 사전 예상·개념 이해와 학생 본인의 해석은 직접 확인한다. Git Commit / Push는 수행하지 않았다.
'''
    readme=root/'README.md'; text=readme.read_text(encoding='utf-8')
    marker='\n## Day 08 — Low-Data Inspection'
    if marker in text:
        before,old=text.split(marker,1)
        following=re.search(r'(?m)^## Day \d+',old)
        after='\n\n---\n\n'+old[following.start():] if following else ''
        text=before.rstrip()+'\n\n'+summary+after
    else: text=text.rstrip()+'\n\n---\n\n'+summary
    readme.write_text(text,encoding='utf-8')

if __name__=='__main__': finish_reports(Path(__file__).resolve().parents[1])
