from pathlib import Path

import cv2


image_path = Path(
    "samples/day02/challenge.jpg"
)

output_dir = Path(
    "outputs/day02/challenge"
)

output_dir.mkdir(
    parents=True,
    exist_ok=True,
)


image = cv2.imread(
    str(image_path)
)

if image is None:
    raise FileNotFoundError(
        f"이미지를 읽지 못했습니다: {image_path}"
    )


# --------------------------------------------------
# TODO
#
# 1. 이미지의 문제를 판단합니다.
# 2. 필요한 전처리를 선택합니다.
# 3. Parameter를 직접 정합니다.
# 4. result에 최종 결과를 저장합니다.
#
# [내 판단]
# 문제: 전체적으로 어둡고 대비가 낮으며(표준편차 약 19),
#       병뚜껑과 배경 벽의 밝기가 비슷해 경계가 약하다.
#       전처리 없이 Otsu를 쓰면 병뚜껑과 벽이 모두 흰색으로 섞인다.
#
# 선택: Gaussian → CLAHE
#       1) Gaussian으로 먼저 노이즈를 줄인다.
#          (CLAHE가 노이즈까지 키우는 것을 막기 위해)
#       2) CLAHE로 병뚜껑과 배경의 지역 대비를 키운다.
#
# Parameter 비교 결과 (Gaussian kernel × clipLimit, tile=(8, 8) 고정)
#   G3 + clip2.0 : 병뚜껑·벽 분리 0.59, 조각 903개
#   G5 + clip2.0 : 분리 0.59, 조각 413개
#   G5 + clip3.0 : 분리 0.80, 조각 556개
#   G7 + clip2.0 : 분리 0.60, 조각 161개
#   G7 + clip3.0 : 분리 0.81, 조각 214개   ← 선택
#   (분리 = 병뚜껑 안쪽과 벽면의 흰색 비율 차이, 클수록 잘 분리됨)
#
# Parameter: Gaussian kernel = (7, 7), clipLimit = 3.0, tileGridSize = (8, 8)
# 주의: 병뚜껑 존재 여부만 볼 때는 문제없지만,
#       Gaussian 7×7은 세로 홈 같은 미세한 형태를 흐리게 만든다.
# --------------------------------------------------


gray_for_result = cv2.cvtColor(
    image,
    cv2.COLOR_BGR2GRAY,
)

blurred = cv2.GaussianBlur(
    gray_for_result,
    (7, 7),
    0,
)

clahe = cv2.createCLAHE(
    clipLimit=3.0,
    tileGridSize=(8, 8),
)

result = clahe.apply(
    blurred
)


# --------------------------------------------------
# 전처리 결과 저장
# --------------------------------------------------

result_path = (
    output_dir
    / "challenge_result.jpg"
)

cv2.imwrite(
    str(result_path),
    result,
)


# --------------------------------------------------
# Gray 변환
# --------------------------------------------------

def to_gray(source):

    if len(source.shape) == 2:
        return source

    return cv2.cvtColor(
        source,
        cv2.COLOR_BGR2GRAY,
    )


original_gray = to_gray(
    image
)

result_gray = to_gray(
    result
)


# --------------------------------------------------
# 전처리 전 Otsu
#
# 이번 Challenge에서는
# 밝은 병뚜껑을 흰색 객체로 확인합니다.
# --------------------------------------------------

_, original_otsu = cv2.threshold(
    original_gray,
    0,
    255,
    cv2.THRESH_BINARY
    + cv2.THRESH_OTSU,
)


# --------------------------------------------------
# 전처리 후 Otsu
# --------------------------------------------------

_, result_otsu = cv2.threshold(
    result_gray,
    0,
    255,
    cv2.THRESH_BINARY
    + cv2.THRESH_OTSU,
)


cv2.imwrite(
    str(
        output_dir
        / "challenge_original_otsu.jpg"
    ),
    original_otsu,
)

cv2.imwrite(
    str(
        output_dir
        / "challenge_result_otsu.jpg"
    ),
    result_otsu,
)


print("입력 :", image_path)
print("결과 :", result_path)
print("Challenge 완료")
