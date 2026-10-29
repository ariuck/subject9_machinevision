# 21_cap_rule.py — 처리 구조

두 기준 이미지의 Area Ratio로 후보 기준값을 만들고, `if` 조건으로 OK / NG를 판정하는 Rule을 구현합니다. 측정(OpenCV)과 판정(Python Rule)을 나누는 첫 파일입니다.

## 입출력

| 구분 | 경로 |
|---|---|
| 입력 | `samples/day03/reference/cap_on.jpg`, `cap_off.jpg` |
| 출력 | `outputs/day03/rule/cap_on_rule.jpg`, `cap_off_rule.jpg` |

## 처리 흐름

```text
[측정] measure_area_ratio(image_path)
   Gray → Otsu (BINARY_INV) → 3×3 Opening → Closing
   → Contour → 0.1% 미만 제외 → 가장 큰 것
   → Area Ratio, 원본 이미지, Contour 반환 (없으면 0.0, image, None)
        ↓
cap_on_ratio, cap_off_ratio 측정
        ↓
[기준 생성]
candidate_threshold        = (cap_on_ratio + cap_off_ratio) / 2
cap_present_when_greater   = cap_on_ratio > cap_off_ratio
        ↓
[판정] judge_cap(area_ratio)
   cap_present_when_greater 이면  ratio >= threshold → OK, 아니면 NG
   아니면                         ratio <= threshold → OK, 아니면 NG
   NG이면 reason = "NG_CAP_AREA"
        ↓
두 기준 이미지에 다시 적용
   → Contour와 "OK/NG ratio=…" 글자를 그려 *_rule.jpg 저장
   → 판정 결과 출력
```

## 실행 결과

```text
cap_on ratio  : 0.6610
cap_off ratio : 0.4587
reference gap : 0.2023
candidate threshold : 0.5599
cap present when: GREATER

cap_on.jpg  → OK
cap_off.jpg → NG (NG_CAP_AREA)
```

## 핵심 포인트

- 기준값 0.5599를 코드에 고정하지 않고 실행할 때마다 두 이미지에서 계산합니다.
- 비율이 큰 쪽이 뚜껑 있음이라고 가정하지 않고 `cap_present_when_greater`로 방향을 저장합니다.
- 기준값을 만든 같은 두 장을 다시 판정한 것은 **정확도가 아니라 Rule 구조가 동작하는지 확인**한 것입니다. 성능 검증은 새 이미지가 필요하며 22번에서 합니다.
- 기준 이미지의 차이(0.2023)가 작으면 Rule이 불안정해집니다. 이 파일은 차이를 검사하지 않고 출력만 합니다.
