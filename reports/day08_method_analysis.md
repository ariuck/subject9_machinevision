# Day08 Method Analysis

실제 실행 CSV에 기반한 에이전트 요약이다. 학생 개인의 설명·판단은 별도이다.

| Method | Accuracy | Precision | Recall | TP | TN | FP | FN |
|---|---:|---:|---:|---:|---:|---:|---:|
| one_shot | 0.8500 | 0.8889 | 0.8000 | 8 | 9 | 1 | 2 |
| few_shot | 0.9000 | 1.0000 | 0.8000 | 8 | 10 | 0 | 2 |

## 데이터와 방법

동일한 Common Query 정상 10장 + broken_small 10장으로 비교했다. 기준·Calibration·Support·Query·합성 원본 역할을 겹치지 않게 분리했다.
One-shot은 정상 Reference 1장과 별도 정상 Calibration 20장의 Cosine Similarity 하위 5 Percentile 0.982109931를 사용했다. 불량 예제로 기준을 조정하지 않았다.
Few-shot은 정상 5장과 작은 파손 5장의 512차원 정규화 특징 평균으로 Prototype을 만들고 더 유사한 클래스를 선택했다. 모델을 새로 학습하지 않았다.
두 방법 모두 ImageNet ResNet18의 최종 Average Pool 512차원 특징과 224×224 Resize를 사용한다. 7일차의 layer3 특징·Center Crop·평가 데이터와 달라 정확도를 단순 순위로 비교하지 않는다.

## 실제 오류 사례

### One-shot

- normal/006.png: actual=Normal, predicted=Anomaly, similarity=0.959205
- anomaly/broken_small/007.png: actual=Anomaly, predicted=Normal, similarity=0.984947
- anomaly/broken_small/016.png: actual=Anomaly, predicted=Normal, similarity=0.982901

### Few-shot

- anomaly/broken_small/000.png: actual=Anomaly, predicted=Normal, normal_similarity=0.988358, anomaly_similarity=0.981073
- anomaly/broken_small/007.png: actual=Anomaly, predicted=Normal, normal_similarity=0.987544, anomaly_similarity=0.987444

정상 Reference 1장은 정상 변동을 모두 대표하지 못할 수 있다. Few-shot은 Support 구성에 민감하며 전체 특징 평균에서 작은 결함 차이가 약해질 수 있다. 이는 원인 가설이고 결과 숫자만으로 확정할 수 없다.

평가 Query는 20장뿐이며 해당 결함·고정 분할에서 얻은 결과이다. Support 수 실험에서도 Query를 바꾸거나 좋은 결과가 나온 Support로 재선택하지 않았다. 실제 도입 성능을 의미하지 않는다.

## Zero-shot과 합성 데이터

Zero-shot은 대상 작업의 학습 예제 없이 사전학습 지식·텍스트 조건 등을 이용하는 접근이며 이 수업에서는 개념만 다룬다. 정상 Reference를 직접 제공하는 이번 유사도 검사는 One-shot이다.
Cut-Paste는 실제 불량의 Ground Truth Mask로 결함을 추출해 별도 정상 이미지에 합성하는 데이터 보강이다. 생성 이미지가 실제 결함 분포와 다를 수 있는 Domain Gap이 있으며, 합성 후 성능 향상 학습 실험은 이번 범위에 포함하지 않았다.
