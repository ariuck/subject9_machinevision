# Subject 9 Machine Vision

OpenCV 기반 제조 머신비전 검사기술을 단계적으로 학습하는 프로젝트입니다.

- 환경: Windows 11 + WSL2 Ubuntu, Python 3.14, OpenCV 5.0, NumPy 2.5 (`.venv`)
- 실행 위치: 모든 명령은 프로젝트 최상위(`~/ai_vision/subject9_machinevision`)에서 실행합니다.

```bash
source .venv/bin/activate
python src/00_check_env.py
```

---

## Day 01 — 머신비전 검사문제 설계와 ROI

1일차에는 완성된 OK / NG 검사기를 만드는 것이 아니라
이미지와 영상에서 **어디를 검사할 것인지 정하고,
정상과 불량의 차이를 어떻게 측정 가능한 특징으로 바꿀 것인지**
생각하는 과정을 학습했습니다.

### 핵심 흐름

```text
검사 문제 확인 → 이미지 읽기 → ROI 설정 → 여러 이미지에 같은 ROI 적용
→ 영상 Frame 처리 → 영상 Frame에 ROI 적용 → 스마트폰 실시간 영상 연결
→ 실시간 Frame에 ROI 적용 → 결과와 판단 기록
```

### 주요 파일

| 파일 | 역할 |
|---|---|
| `00_check_env.py` | Python · OpenCV · NumPy 환경 확인 |
| `01_read_image.py` | 이미지 한 장 읽기 |
| `02_image_info.py` | 이미지 크기와 채널 확인 |
| `03_roi_crop.py` | 이미지 한 장에서 ROI 설정·저장 |
| `04_batch_roi.py` | 여러 이미지에 동일한 ROI 적용 |
| `05_video_input.py` | 저장 영상을 Frame으로 읽고 일정 간격으로 저장 |
| `06_video_roi.py` | 저장 영상의 Frame에 ROI 적용·저장 |
| `07_webcam_input.py` | 스마트폰 IP Webcam(DroidCam) 영상 입력 확인 |
| `08_phone_camera_roi.py` | 실시간 영상에서 마우스로 ROI 선택·저장 |
| `03_roi_review.ipynb` | `03_roi_crop.py`를 Jupyter에서 단계별로 리뷰 |

### 결과

- ROI `(170, 120, 470, 500)`을 샘플 5장에 적용: 뚜껑 있는 3장은 ROI 안에 들어오고, 2장은 뚜껑 없는 불량 후보로 확인
- 같은 ROI를 1280×720 영상에 적용하면 검사 대상을 놓침 → 고정 ROI는 해상도·위치가 같을 때만 안정적
- 기록: `reports/day01_problem_definition.md`

---

## Day 02 — Image Enhancement와 검사 영상 품질 개선

1일차에 설정한 ROI를 이용하여
촬영조건과 영상 품질이 검사 결과에 어떤 영향을 주는지 확인했습니다.

### 실습 내용

- BGR / Gray / HSV 비교
- Brightness / Contrast
- Gamma Correction
- CLAHE
- Gaussian / Median / Bilateral Filter
- Sharpening
- Threshold / Otsu
- 전처리 전·후 객체 분리 결과 비교
- Mini Challenge를 통한 전처리 직접 선택

### 핵심 결과

| 항목 | 결과 |
|---|---|
| 어두운 영상 | Gamma 1.2~1.5가 밝기와 대비를 함께 개선. Brightness는 대비를 키우지 못함 |
| 저대비 영상 | CLAHE clipLimit 2.0~3.0이 무난. 4.0은 과강조 |
| 점 노이즈 | Median 3이 가장 좋음(PSNR 22.4 → 30.7) |
| Threshold | 고정 80·160은 분리 실패, Otsu(118)는 자동으로 적절한 값 선택 |
| 전처리 비교 | 노이즈 없는 저대비 영상에서는 CLAHE + Otsu가 오히려 조각을 늘림 |
| Mini Challenge | `challenge.jpg`에 Gaussian(7,7) → CLAHE 3.0 선택. 병뚜껑과 벽의 분리 0.00 → 0.81 |

- `outputs/day02/compare/preprocess_compare.png`
- `outputs/day02/challenge/challenge_result.jpg`
- `reports/day02_parameter_table.csv`
- `reports/day02_preprocess_reason.md`
- `reports/day02_metrics.csv`

### 오늘의 핵심

전처리 기술을 먼저 선택하는 것이 아니라
문제 확인 → 필요한 전처리 선택 → Parameter 비교 → Threshold / Otsu 결과 확인 → 사용 여부 결정
순서로 판단한다.

---

## Day 03 — Morphology·Contour와 규칙 기반 판정

1일차에서 실제 촬영한 ROI 이미지와
2일차에서 학습한 Threshold / Otsu 방식을 이어서 사용했습니다.

3일차에서는 Binary Image를 Morphology로 정리하고,
Contour를 이용하여 객체의 특징을 숫자로 측정한 뒤
실제 측정값을 근거로 Rule 기반 OK / NG 판정을 만들었습니다.

### 실습 흐름

```text
ROI Image → Gray → Threshold / Otsu → Binary Image → Morphology → Contour
→ Feature 측정 → cap_on / cap_off 비교 → Candidate Rule → OK / NG
→ 새로운 실제 촬영 이미지 Batch Test → 결과 분석 → Mini Challenge
```

### 주요 파일

| 파일 | 역할 |
|---|---|
| `18_morphology_compare.py` | Opening / Closing과 Kernel 3·5·9 비교 |
| `19_contour_measure.py` | Contour 검출과 Area / BBox / Center 측정 |
| `20_cap_feature_compare.py` | cap_on / cap_off의 Feature 비교 |
| `21_cap_rule.py` | 실제 측정값으로 Candidate Rule 생성 |
| `22_cap_batch_test.py` | 새로 촬영한 이미지에 같은 Rule 적용 |
| `23_day03_challenge.py` | Mini Challenge: 빨간 병뚜껑 존재 검사(HSV) |
| `docs/day03/` | 스크립트별 설명 |

### 병뚜껑 Rule 실습

| 항목 | 값 |
|---|---|
| cap_on `largest_area_ratio` | 0.661 |
| cap_off `largest_area_ratio` | 0.459 |
| Candidate Threshold | 0.560 (두 값의 중간) |
| Batch Test | 4장 중 4장 일치 |

```text
Threshold 이상 → cap_on → OK
Threshold 미만 → cap_off → NG
```

- `cap_on_003`(0.457)이 기준 cap_off(0.459)와 거의 같아, 면적 비율 하나만으로는 경계가 아슬아슬하다.
- 이미지 4장의 결과이므로 성능이 아니라 교육용 Candidate Rule의 확인이다.
- 기록: `reports/day03_reference_features.csv`, `reports/day03_inspection_results.csv`

### Mini Challenge — 빨간 병뚜껑 존재 검사

- 문제: 콜라병 입구에 빨간 병뚜껑이 있는가 (`sample.mp4`의 Frame 6장)
- 처리: BGR → HSV 빨강 Mask(H 0~4/170~180, S ≥ 90, V ≥ 120) → Opening·Closing → Contour
- Feature: `largest_red_area_ratio` (정상 0.0049~0.0069, 불량 0.0000)
- Rule: `>= 0.00247`이면 OK, 미만이면 NG(`NG_RED_CAP_MISSING`)
- 결과: 확인용 4장 모두 일치. 병따개가 뚜껑을 가린 경우도 OK
- 기록: `reports/day03_rule_analysis.md`, `reports/day03_challenge_results.csv`

### 확장 실습 — IP Webcam + FastAPI 실시간 병뚜껑 검사

3일차 Rule을 스마트폰 실시간 영상에 적용하고 브라우저에 OK / NG를 표시합니다.

| 파일 | 역할 |
|---|---|
| `src/cap_inspector.py` | Gray·Otsu·Morphology·Contour·Area Ratio 검사 함수 |
| `src/fastapi_cap_app.py` | 카메라 수신, ROI 저장, 상태 조회, MJPEG 스트림 API |
| `web/cap_inspection.html` | 영상 표시, 마우스 ROI 선택, 판정 결과 화면 |
| `tests/test_inspector.py` | 검사 로직과 FastAPI 연동 자동 테스트 |

```bash
python -m pytest tests/test_inspector.py -q
python -m uvicorn src.fastapi_cap_app:app --host 127.0.0.1 --port 8000
```

브라우저에서 `http://127.0.0.1:8000`을 열고 카메라 주소(예: `http://<폰 IP>:4747/video`)를 입력한 뒤 병뚜껑 영역을 드래그합니다.

- 자동 테스트 2개 통과, 카메라 연결과 영상 수신 확인
- 실제 병으로 뚜껑 있음 / 없음 판정은 아직 확인하지 않음

---

## 다음 학습

Day 04에서는 객체 분리, Template Matching, 특징점 매칭으로
위치가 바뀌어도 검사 대상을 찾는 방법을 학습한다.
