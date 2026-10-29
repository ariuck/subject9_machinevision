# 19_contour_measure.py — 처리 구조

`cap_on` 한 장에서 Contour를 찾고 가장 큰 객체의 Area, Area Ratio, BBox, Center를 측정해 이미지에 표시합니다.

## 입출력

| 구분 | 경로 |
|---|---|
| 입력 | `samples/day03/reference/cap_on.jpg` |
| 출력 | `outputs/day03/contour/binary.jpg`, `cleaned.jpg`, `contour_result.jpg` |

## 처리 흐름

```text
cap_on.jpg 읽기
        ↓
BGR → Gray → Otsu (BINARY_INV) → binary
        ↓
3×3 타원 Kernel
Opening 1회 → Closing 1회        → cleaned
        ↓
findContours (RETR_EXTERNAL, CHAIN_APPROX_SIMPLE)
        ↓
전체 Contour 수 출력
   └─ 0개이면 binary·cleaned 저장 후 종료
        ↓
가장 큰 Contour 선택 (contourArea 기준)
   ├─ Area          = contourArea
   ├─ BBox          = boundingRect → (x, y, w, h)
   ├─ Center        = moments → (m10/m00, m01/m00)
   └─ Area Ratio    = Area / (ROI 너비 × 높이)
        ↓
원본 ROI에 표시
   초록 = Contour / 파랑 = BBox / 빨강 = Center / 노랑 글자 = Area Ratio
        ↓
binary.jpg · cleaned.jpg · contour_result.jpg 저장 → 측정값 출력
```

## 핵심 포인트

- 작은 Contour를 걸러내는 최소 면적 기준이 **없습니다**. 그래서 Contour가 5개로 잡혔습니다. 20번 이후는 ROI 면적의 0.1% 미만을 제외하는 필터가 있습니다.
- Contour 5개는 병뚜껑 5개가 아니라 흰색으로 분리된 영역이 5개라는 뜻입니다. 가장 큰 것을 병뚜껑 후보로 씁니다.
- Area는 픽셀 수이고 Area Ratio는 ROI 대비 비율입니다. 해상도가 달라져도 비교하기 쉽도록 비율을 함께 기록합니다.
- `m00`이 0이면 Center를 계산하지 않고 `None`으로 둡니다.

## 실행 결과

```text
전체 Contour 수: 5
Largest Area: 27878.0
Area Ratio: 0.6610233793332385
BBox: (6, 9, 195, 163)
Center: (104, 91)
```

0.661은 아직 판정 기준이 아니라 측정값입니다. `cap_off`와 비교하는 것은 20번에서 합니다.
