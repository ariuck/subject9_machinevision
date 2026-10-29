# Day05 Calibration · Rule Freeze · Test 결과 분석

> 측정값: `day05_calibration_measurements.csv` · 후보: `day05_rule_candidates.csv` · Rule: `configs/day05_logo_rules.json`
> Test: `day05_test_results.csv` · 평가: `day05_test_metrics.md` (38번이 생성)
> 실제 이미지 크기는 1280×960이다(교재 폴더 이름은 `1920X1080`).

## 1. Calibration 12장 측정 (34)

| 파일 | 실제 | Template | SIFT Good | Inlier | Inlier Ratio |
|---|---|---:|---:|---:|---:|
| ok_01 | OK | 0.536 | 174 | 167 | 0.960 |
| ok_02 | OK | 0.545 | 174 | 158 | 0.908 |
| ok_03 | OK | 0.556 | 184 | 164 | 0.891 |
| ok_04 | OK | 0.425 | 151 | 142 | 0.940 |
| ok_05 | OK | 0.553 | 161 | 147 | 0.913 |
| ok_06 | OK | 0.440 | **74** | 60 | 0.811 |
| ng_01 | NG | 0.531 | 126 | 120 | 0.952 |
| ng_02 | NG | 0.443 | 99 | 81 | 0.818 |
| ng_03 | NG | 0.484 | 141 | 109 | 0.773 |
| ng_04 | NG | 0.536 | 161 | 139 | 0.863 |
| ng_05 | NG | 0.526 | 107 | 94 | 0.879 |
| ng_06 | NG | 0.462 | 109 | 91 | 0.835 |

- Template Score: OK 0.425~0.556, NG 0.443~0.536 → 거의 완전히 겹쳐 구분에 쓸 수 없다.
- SIFT Good Match: OK는 대부분 151 이상이지만 `ok_06`(74)이 크게 벗어난다. NG에도 141, 161이 있다.
- Inlier Ratio: OK 0.81~0.96, NG 0.77~0.95 → 많이 겹친다.
- Homography는 12장 모두 계산되었다(가린 NG도 로고 일부로 위치를 찾음).

## 2. Rule 후보와 결정 (35 → 36)

- SIFT 후보 15개 × Inlier Ratio 후보 15개를 시험하고, FN → 전체 오류 → FP → 작은 기준값 순으로 정렬했다.
- 가장 좋은 후보: **SIFT Good Match ≥ 129 AND Inlier Ratio ≥ 0.8664** (Accuracy 0.9167, FP 1, FN 0)
  - 이 값은 교재 36번에 적힌 기준값과 같아서 36번 코드를 수정하지 않았다.
  - 같은 정확도의 후보가 6개(129·137·145 × 0.8664·0.8797)였고, 정렬 규칙에 따라 가장 작은 값을 선택했다.
- Calibration 오판정 1건: `ok_06`(SIFT 74, Ratio 0.811) → FP.
- **여유가 매우 작다**: `ng_04`의 Inlier Ratio 0.8634와 기준 0.8664의 차이는 0.003이다.
- 참고: SIFT 하나만 쓰면(≥129) `ok_06`이 FP, `ng_03`(141)·`ng_04`(161)가 FN이 되어 오류가 3건이다. 그래서 두 Feature를 함께 쓰는 Rule이 선택되었다.

## 3. Test 6장 (37 → 38)

| 파일 | 실제 | 판정 | 유형 | SIFT Good | Inlier Ratio | NG Reason |
|---|---|---|---|---:|---:|---|
| test_ok_01 | OK | NG | FP | 169 | 0.781 | LOW_INLIER_RATIO |
| test_ok_02 | OK | NG | FP | 156 | 0.840 | LOW_INLIER_RATIO |
| test_ok_03 | OK | NG | FP | 204 | 0.853 | LOW_INLIER_RATIO |
| test_ng_01 | NG | NG | TP | 58 | 0.741 | LOW_SIFT_MATCH;LOW_INLIER_RATIO |
| test_ng_02 | NG | NG | TP | 111 | 0.766 | LOW_SIFT_MATCH;LOW_INLIER_RATIO |
| test_ng_03 | NG | NG | TP | 105 | 0.914 | LOW_SIFT_MATCH |

- Accuracy 0.50, TP 3, TN 0, **FP 3**, FN 0, NG Precision 0.50, NG Recall 1.00
- 결과가 교재 27장에 적힌 값과 같다.

## 4. 실패 분석 — NG Reason과 실제 원인

- **NG Reason**(프로그램이 내린 이유): 세 FP 모두 `LOW_INLIER_RATIO`.
- **Failure Cause**(실제 원인으로 보이는 것):
  - `test_ok_01` 결과 이미지를 보면 로고가 선명하고, Homography 사각형도 로고를 정확히 감쌌다. SIFT Good Match도 169로 높다. 제품은 정상이고 로고도 찾았다.
  - 문제는 Inlier Ratio 기준이다. Calibration에서 OK와 NG의 Inlier Ratio가 많이 겹쳤는데, 기준 0.8664가 그 겹친 구간 안에 걸려 있었다. 처음 보는 정상 이미지 3장은 0.78~0.85로 그 기준 아래에 떨어졌다.
  - 즉 **Inlier Ratio는 이 데이터에서 정상/불량을 안정적으로 나누지 못하는 Feature**였고, Calibration 12장으로는 그 불안정성이 드러나지 않았다(Calibration에서는 0.003 차이로 맞음).
- 참고(가설): Test 6장에서는 SIFT Good Match만 보면 OK 156~204, NG 58~111로 나뉜다. 하지만 이것은 **Test 결과를 보고 얻은 정보이므로 지금 Rule을 바꾸는 근거로 쓰지 않는다.** 다음 Calibration에서 더 많은 정상 이미지로 다시 확인할 가설로만 남긴다.

## 5. 판단

- 교재 31장 원칙대로 **Test 결과를 보고 Threshold를 다시 맞추지 않았다.** 현재 Baseline(day05-logo-v1.0)의 한계로 기록한다.
- 다음에 개선할 때:
  1. Calibration 정상 이미지를 늘려 Inlier Ratio의 실제 범위를 다시 확인한다.
  2. Inlier Ratio를 Rule에서 빼거나 기준을 낮춘 후보를 **새 Calibration 데이터로** 다시 시험한다.
  3. 새 Rule은 새 버전(v1.1)으로 Freeze하고, 아직 쓰지 않은 Test 이미지로 평가한다.

## 6. Mini Challenge

- `src/39_day05_mini_challenge.py`의 TODO 1~7을 완성했다. 기준 Feature 2개 조합과 Threshold를 Calibration 측정값에서 자동으로 고르고, JSON으로 고정한 뒤 Test에 적용해 TP/TN/FP/FN을 계산한다.
- **다른 제품의 사진이 없어 실제 Mini Challenge는 하지 않았다.** `samples/day05/mini_challenge/`에 다른 제품 사진 11장을 넣고 실행하면 된다.
- 코드가 끝까지 동작하는지는 광천김 사진으로 임시 폴더에서만 확인했다(이 결과는 Mini Challenge 결과가 아니다).
