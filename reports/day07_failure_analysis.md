# Day07 Failure Analysis

실제 실행 CSV 기반 자동 요약. 아래 원인은 가설이며 학생의 육안 확인은 별도이다.

## Test FP

- File: samples/day07/test/normal/006.png
- Score: 0.069448
- Threshold: 0.067457
- 원인 추정: 정상 이미지의 조명·색·위치 차이가 정상 평균 특징에서 벗어났을 가능성. Score만으로 원인을 확정할 수 없다.

## Test FN

- File: samples/day07/test/anomaly/broken_small/000.png
- Score: 0.053299
- Threshold: 0.067457
- 원인 추정: 작은 국소 결함이 전체 특징 평균에서 약해졌거나 중심 Crop 밖에 있었을 가능성. 원본·Mask·Heatmap을 함께 확인해야 한다.

## Challenge FP

- normal_bright.png: Score 0.104316 > 0.067457
- normal_dark.png: Score 0.123439 > 0.067457
- normal_shift.png: Score 0.076077 > 0.067457

원인 추정: 촬영 조건 변화가 사전학습 특징을 바꾸어 정상 평균과의 거리를 키웠을 가능성이 있다.

## 한 줄 정리

큰 파손·오염과 작은 결함의 검출 차이는 종류별 성능표에서 확인한다. 촬영 조건 변화도 오탐 원인이 될 수 있다.

개선 후보: 촬영·정렬 안정화, 정상 조건 다양화, 국소 특징 기반 검출. 개선 후에는 새로운 검증·Test로 평가하고 기존 Test에 맞춰 Threshold를 조정하지 않는다.

## Heatmap 해석

Heatmap은 정상 특징과의 차이이고 Ground Truth는 실제 결함 위치이다. 색은 이미지별 정규화되어 이미지 간 절대 점수 비교용이 아니다.
사전학습 전처리의 Center Crop 좌표에 맞추어 원본 위에 복원했다. Crop 밖 영역은 모델이 보지 않은 영역이며 Overlay에서 원본으로 남겨 둔다.
