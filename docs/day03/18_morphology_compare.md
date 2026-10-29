# 18_morphology_compare.py — 처리 구조

Binary Image에 Opening·Closing을 적용하고 Kernel 크기(3×3, 5×5, 9×9)에 따라 결과가 어떻게 달라지는지 비교합니다. 측정이나 판정은 하지 않고 눈으로 비교할 이미지만 저장합니다.

## 입출력

| 구분 | 경로 |
|---|---|
| 입력 | `samples/day03/reference/cap_on.jpg` (이미 ROI로 잘린 이미지, 추가 Crop 없음) |
| 출력 | `outputs/day03/morphology/` 8장 |

출력 파일

```text
01_gray.jpg
02_binary.jpg
kernel_3_opening.jpg   kernel_3_closing.jpg
kernel_5_opening.jpg   kernel_5_closing.jpg
kernel_9_opening.jpg   kernel_9_closing.jpg
```

## 처리 흐름

```text
cap_on.jpg 읽기 (실패하면 FileNotFoundError)
        ↓
BGR → Gray                      → 01_gray.jpg
        ↓
Otsu + THRESH_BINARY_INV        → 02_binary.jpg
(어두운 병뚜껑 = 흰색 객체)
        ↓
kernel_sizes = [3, 5, 9] 반복
   ├─ 타원형 Kernel (size × size) 생성
   ├─ Opening (iterations=1)    → kernel_N_opening.jpg
   └─ Opening 결과에 Closing    → kernel_N_closing.jpg
        ↓
입력 경로 · Otsu 값 출력
```

## 핵심 포인트

- Binary는 한 번만 만들고, 세 Kernel이 같은 Binary에서 출발합니다.
- `kernel_N_closing.jpg`는 Closing만 적용한 것이 아니라 **Opening → Closing**을 모두 거친 결과입니다.
- Kernel은 `MORPH_ELLIPSE`, Iteration은 모두 1입니다.
- 이 파일에서 Kernel을 정하지 않습니다. 다음 단계(19~22)는 3×3 · Opening 1회 · Closing 1회를 기준으로 씁니다.

## 실행 결과

```text
입력: samples/day03/reference/cap_on.jpg
Otsu Threshold: 111.0
Morphology 비교 결과 저장 완료
```

Otsu 111.0은 `BINARY_INV`이므로 111보다 어두운 픽셀이 흰색이 된다는 뜻입니다. 면적 비율이나 정확도가 아닙니다.
