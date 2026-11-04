"""Support count experiment and contamination Cut-Paste using the same Query."""
from pathlib import Path
import csv
import json
import numpy as np
from day08_feature_core import create_feature_model, extract_feature, build_prototype, cosine_similarity
from day08_cutpaste_core import generate_synthetic_set

SUPPORT_COUNTS = [1, 3, 5]
SUPPORT_ROOT = Path('samples/day08/few_shot/support')
QUERY_ROOT = Path('samples/day08/common_query')
REPORTS = Path('reports')
REPORTS.mkdir(exist_ok=True)
# These are agent predictions made before inference, not student/team responses.
prediction = {
    'author':'agent',
    'prediction':'Support를 늘리면 Prototype이 안정될 수 있지만 Accuracy가 단조 증가하거나 FP/FN이 모두 줄어든다고 보장할 수 없다.',
    'selection':'각 클래스 파일명을 정렬한 뒤 앞 1/3/5장을 사용. Query 결과로 Support를 고르지 않음.',
}
(REPORTS/'day08_mini_prediction.json').write_text(json.dumps(prediction,ensure_ascii=False,indent=2),encoding='utf-8')
model = create_feature_model()
support = {label:sorted((SUPPORT_ROOT/label).glob('*.png')) for label in ['normal','anomaly']}
if any(len(files) != 5 for files in support.values()):
    raise RuntimeError('Expected exactly five support images per class')
features = {label:[extract_feature(model,p) for p in files] for label,files in support.items()}
query = [(f'normal/{p.name}','Normal',p) for p in sorted((QUERY_ROOT/'normal').glob('*.png'))]
query += [(f'anomaly/broken_small/{p.name}','Anomaly',p) for p in sorted((QUERY_ROOT/'anomaly/broken_small').glob('*.png'))]
if len(query) != 20:
    raise RuntimeError('Expected 20 Common Query images')
query_features = [(sid,actual,extract_feature(model,p)) for sid,actual,p in query]
details, summaries = [], []
for count in SUPPORT_COUNTS:
    normal = build_prototype(features['normal'][:count])
    anomaly = build_prototype(features['anomaly'][:count])
    rows = []
    for sid,actual,feature in query_features:
        ns, ans = cosine_similarity(feature,normal),cosine_similarity(feature,anomaly)
        predicted = 'Normal' if ns >= ans else 'Anomaly'
        error = ('TP' if predicted=='Anomaly' else 'FN') if actual=='Anomaly' else ('FP' if predicted=='Anomaly' else 'TN')
        rows.append(dict(support_count=count,sample_id=sid,actual=actual,predicted=predicted,
                         normal_similarity=ns,anomaly_similarity=ans,error_type=error))
    counts = {t:sum(r['error_type']==t for r in rows) for t in ['TP','TN','FP','FN']}
    summaries.append(dict(support_count=count,samples=len(rows),accuracy=(counts['TP']+counts['TN'])/len(rows),**counts))
    details.extend(rows)
for name,rows in [('day08_support_count_comparison.csv',summaries),('day08_support_count_results.csv',details)]:
    with (REPORTS/name).open('w',encoding='utf-8-sig',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=list(rows[0])); writer.writeheader(); writer.writerows(rows)

source = Path('samples/day08/mini_challenge/defect_source/contamination')
generated = generate_synthetic_set(
    normal_dir='samples/day08/mini_challenge/normal',
    defect_image_dir=source/'images', defect_mask_dir=source/'masks',
    output_dir='outputs/day08/mini_challenge/generated',
    metadata_path=REPORTS/'day08_contamination_metadata.csv',
    defect_type='contamination', count=5, seed=43,
    scale_range=(0.6,1.0), angle_range=(-10.0,10.0))
print('Support count results:',summaries)
print('Generated contamination:',len(generated))
