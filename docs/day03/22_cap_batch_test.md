# 22_cap_batch_test.py — 처리 구조

새로 촬영한 이미지 여러 장에 같은 Rule을 적용해 정답 여부와 정확도를 확인하고 CSV로 저장합니다.

## 입출력

| 구분 | 경로 |
|---|---|
| 기준 이미지 | `samples/day03/cap_on/cap_on_001.jpg`, `samples/day03/cap_off/cap_off_001.jpg` |
| 테스트 이미지 | `cap_on_002`, `cap_on_003`, `cap_off_002`, `cap_off_003` |
| 출력 이미지 | `outputs/day03/batch/{파일명}_result.jpg` |
| 출력 CSV | `reports/day03_inspection_results.csv` (UTF-8 BOM) |

## 처리 흐름

```text
measure(image_path)  ← 21번의 측정 과정에 Feature를 더한 함수
   Gray → Otsu (BINARY_INV) → 3×3 Opening → Closing → Contour
   → 0.1% 미만 제외
   → valid_count, 가장 큰 Contour, Area Ratio, 정규화된 Center 반환
   → 이미지를 읽지 못하면 None
        ↓
[기준] cap_on_001, cap_off_001 측정 (하나라도 실패하면 RuntimeError)
   threshold = (on_ratio + off_ratio) / 2
   cap_present_when_greater = on_ratio > off_ratio
        ↓
[테스트] TEST_IMAGES 4장을 차례로
   ├─ measure() 후 judge(ratio) → (predicted, decision, reason)
   │     predicted: "cap_on" / "cap_off"
   │     decision : "OK" / "NG"  (NG이면 reason = NG_CAP_AREA)
   ├─ predicted == expected → correct
   ├─ Contour와 "predicted ratio" 글자를 그려 *_result.jpg 저장
   │     (맞으면 초록, 틀리면 빨강)
   └─ rows에 한 줄 추가
        ↓
검사한 이미지가 0장이면 종료, 아니면 CSV 저장
        ↓
확인 이미지 수 · 일치 · 불일치 · Accuracy 출력
```

## 실행 결과

```text
Reference ON : 0.4379
Reference OFF: 0.2838
Threshold    : 0.3608
확인 이미지 수: 4 / 기준과 일치: 4 / 불일치: 0 / Accuracy: 1.0
```

| 이미지 | 실제 | 예측 | Area Ratio | valid_count | 판정 |
|---|---|---|---:|---:|---|
| cap_on_002 | cap_on | cap_on | 0.5599 | 1 | OK |
| cap_on_003 | cap_on | cap_on | 0.4566 | 2 | OK |
| cap_off_002 | cap_off | cap_off | 0.2903 | 6 | NG |
| cap_off_003 | cap_off | cap_off | 0.3169 | 7 | NG |

## 핵심 포인트

- 21번과 기준 이미지가 다릅니다. 21번은 `reference/` 폴더(1일차 ROI)를, 22번은 새로 촬영한 `cap_on_001` / `cap_off_001`을 기준으로 씁니다. 그래서 기준값이 0.5599가 아니라 0.3608입니다.
- 기준 이미지와 테스트 이미지를 분리해야 "새 이미지에서도 맞는가"를 볼 수 있습니다.
- 가장 가까운 경우는 `cap_off_003`(0.3169)과 기준값(0.3608)의 차이 약 0.044입니다. 여유가 크지 않으므로 4장 모두 맞았다고 해서 정확도 100%라고 말할 수 없습니다.
- `valid_count`와 Center는 CSV에 기록만 하고 판정에는 쓰지 않습니다.
- 테스트 이미지 4장은 코드에 파일명이 고정되어 있습니다. 이미지를 추가하려면 `TEST_IMAGES` 목록을 고쳐야 합니다.
