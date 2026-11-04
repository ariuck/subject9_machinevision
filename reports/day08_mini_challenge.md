# Day08 Mini Challenge

에이전트가 수행한 실험이다. 학생의 사전 예상·개념 이해·개인 판단을 대신 확인한 것은 아니다.

## 1. Support Count 비교

사전 예상: Support가 늘면 안정될 수 있지만 Accuracy의 단조 증가와 FP/FN 동시 감소는 보장되지 않는다.
선택: 각 클래스의 Support 파일명 정렬 순서에서 앞 1/3/5장을 사용한다. 동일 Query의 Feature를 재사용한다.

| Support / class | Accuracy | FP | FN |
|---:|---:|---:|---:|
| 1 | 0.7000 | 1 | 5 |
| 3 | 0.8000 | 0 | 4 |
| 5 | 0.9000 | 0 | 2 |

세 실험은 고정된 한 Support 집합의 중첩 부분집합이다. 장수와 포함된 이미지 구성이 함께 달라지므로 일반적인 성능 증가를 증명하지 않는다.

## 2. contamination Synthetic Defect

별도 정상 이미지 5장, 오염 원본 2장과 Mask로 합성 5장을 생성했다. Scale 0.6~1.0, Rotation -10~10°, Seed 43.
대표 이미지와 자연스러움·경계 품질 판단은 `day08_synthetic_quality_check.md`의 실제 이미지 검수 기록을 확인한다.

## 3. 상황별 방법 선택

| 데이터 상황 | 먼저 고려할 방법 | 이유 |
|---|---|---|
| 정상 충분 / 불량 없음 | 정상 기반 Anomaly Detection | 정상 범위를 기준으로 차이를 찾는다. |
| 확실한 정상 기준 1장 + 정상 Calibration | One-shot | 한 장과의 유사도를 별도 정상 데이터로 교정한다. |
| 정상·불량 예제가 각각 소수 | Few-shot | 클래스별 예제로 Prototype을 만든다. |
| 실제 불량 부족 | Defect Generation + 실제 데이터 추가 수집 | 합성으로 보강하되 실제 데이터로 평가한다. |

## 한 줄 결론

단순 이미지 수보다 데이터의 역할·대표성·평가 분리와 실제 오류를 함께 확인하는 것이 중요하다.


### 이미지 검수 결과

- 상대적으로 가장 자연스러운 오염 합성: `outputs/day08/mini_challenge/generated/synthetic_003.png`
- 가장 어색한 오염 합성: `outputs/day08/mini_challenge/generated/synthetic_000.png`
- 이유: 003은 국소 갈색 오염처럼 보이지만 규칙적 원형 경계가 남는다. 000은 넓은 유리 윤곽이 복제되어 병 바닥이 겹쳐 보인다.
- 위 판단은 에이전트의 시각 검수이며 학생 본인의 선택은 별도로 기록한다.