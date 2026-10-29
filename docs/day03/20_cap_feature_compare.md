# 20_cap_feature_compare.py — 처리 구조

`cap_on`과 `cap_off`를 **같은 함수·같은 조건**으로 측정해 어떤 Feature가 두 상태를 구분하는지 비교합니다.

## 입출력

| 구분 | 경로 |
|---|---|
| 입력 | `samples/day03/reference/cap_on.jpg`, `cap_off.jpg` |
| 출력 이미지 | `outputs/day03/feature/` — `{label}_binary.jpg`, `{label}_cleaned.jpg`, `{label}_contour.jpg` (총 6장) |
| 출력 CSV | `reports/day03_reference_features.csv` (UTF-8 BOM) |

## 처리 흐름

```text
input_files = {cap_on, cap_off}
        ↓
각 이미지마다 measure_features(image) 호출
   ├─ Gray → Otsu (BINARY_INV) → binary
   ├─ 3×3 타원 Kernel, Opening → Closing → cleaned
   ├─ findContours (RETR_EXTERNAL)
   ├─ ROI 면적의 0.1% 미만 Contour 제외 → valid_contours
   │      └─ 없으면 기본값(0, "")을 담아 바로 반환
   ├─ 가장 큰 Contour 선택
   │      area, BBox, Center(moments)
   ├─ touches_border = BBox가 이미지 가장자리에 닿는가
   └─ 정규화: area_ratio = area / ROI 면적
              center_x_norm = cx / 너비, center_y_norm = cy / 높이
        ↓
(features, binary, cleaned, annotated) 반환
        ↓
이미지 3장 저장 + 터미널 출력 + rows에 누적
        ↓
CSV 저장
```

## 측정 Feature

| Feature | 의미 |
|---|---|
| `otsu_value` | Otsu가 정한 이진화 기준 밝기 |
| `valid_count` | 최소 면적을 넘는 Contour 개수 |
| `largest_area` / `largest_area_ratio` | 가장 큰 객체의 면적 / ROI 대비 비율 |
| `center_x_norm`, `center_y_norm` | 중심 위치(0~1) |
| `touches_border` | 객체가 ROI 가장자리에 닿는지 |

## 실행 결과

| | cap_on | cap_off |
|---|---:|---:|
| otsu_value | 111.0 | 116.0 |
| valid_count | 3 | 1 |
| largest_area | 27878 | 19347 |
| largest_area_ratio | **0.661** | **0.459** |
| center (x, y) | (0.491, 0.461) | (0.536, 0.551) |
| touches_border | False | True |

## 핵심 포인트

- 두 이미지에 다른 Kernel이나 Threshold를 쓰면 비교가 무너지므로 같은 함수로 처리합니다.
- 가장 뚜렷한 차이는 `largest_area_ratio`(0.661 vs 0.459)입니다. 다음 단계(21)가 이 값을 사용합니다.
- `valid_count`와 `touches_border`는 차이가 있지만 이미지 두 장만으로는 기준으로 삼기 이릅니다.
- 19번에서는 Contour가 5개였지만 여기서는 3개입니다. 최소 면적 필터가 작은 영역을 제외했기 때문입니다.
