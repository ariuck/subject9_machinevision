# Day07 Mini Challenge

Source: samples/day07/test/normal/001.png
Threshold: 0.067457

에이전트가 실행 전에 기록한 예상과 실제 측정 결과이다. 학생 개인의 예상으로 간주하지 않는다.

| 변형 | 설정값 | 에이전트 사전 예상 | 실제 Score | 결과 |
|---|---:|---|---:|---|
| mini_blur.png | 9 | PASS | 0.054978 | PASS |
| mini_dark.png | 0.7 | FP | 0.099735 | FP |
| mini_rotation.png | 12.0 | FP | 0.047913 | PASS |

가장 Score가 높았던 조건: mini_dark.png
예상과 달랐던 조건: mini_rotation.png

한 줄 정리: 정상 이미지라도 조건 변화가 정상 평균과의 특징 거리를 키울 수 있다. 설정 강도와 Score 관계는 원본 이미지에 따라서도 달라진다.

학생 개인 예상과 해석은 직접 작성한다. 위 예상은 에이전트가 Score 계산 전에 기록했다.