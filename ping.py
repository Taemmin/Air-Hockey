import cv2
import cvzone
from cvzone.HandTrackingModule import HandDetector
import numpy as np

# 비디오 캡처 설정
cap = cv2.VideoCapture(cv2.CAP_DSHOW + 0)
cap.set(3, 1280)  # 비디오 프레임의 너비 설정
cap.set(4, 720)  # 비디오 프레임의 높이 설정

# 이미지 불러오기
imgBackground = cv2.imread("Background.png")
imgGameOver = cv2.imread("gameOver.png")
imgBall = cv2.imread("Ball.png", cv2.IMREAD_UNCHANGED)
imgBat1 = cv2.imread("bat1.png", cv2.IMREAD_UNCHANGED)
imgBat2 = cv2.imread("bat2.png", cv2.IMREAD_UNCHANGED)

# 손 감지
detector = HandDetector(detectionCon=0.8, maxHands=2)

# 변수 초기화
ballPos = [100, 100]  # 공의 초기 위치
speedX = 40  # 공의 X 방향 속도
speedY = 40  # 공의 Y 방향 속도
gameOver = False  # 게임 종료 여부
score = [0, 0]  # 두 플레이어의 점수

while True:
    _, img = cap.read()  # 비디오 프레임 읽기
    img = cv2.flip(img, 1)  # 프레임 좌우 반전
    imgRaw = img.copy()  # 원본 이미지 보존

    # Find the hand and its landmarks
    hands, img = detector.findHands(img, flipType=False)  # 손 감지

    # 배경 이미지 추가
    img = cv2.addWeighted(img, 0.2, imgBackground, 0.8, 0)

    # 손 인식
    if hands:
        for hand in hands:
            x, y, w, h = hand["bbox"]  # 감지된 손의 바운딩 박스 정보를 추출
            h1, w1, _ = imgBat1.shape  # 핸들의 높이와 너비 추출
            y1 = y - h1 // 2  # 화면에 핸들 표시할 y좌표 계산
            y1 = np.clip(y1, 20, 415)  # y값 이동경계 제한

            if hand["type"] == "Left":
                img = cvzone.overlayPNG(img, imgBat1, (59, y1))  # 핸들 그리기
                if 59 < ballPos[0] < 59 + w1 and y1 < ballPos[1] < y1 + h1:  # 공 충돌시
                    speedX = -speedX  # 방향 반대로 전환
                    ballPos[0] += 30  # 공을 오른쪽으로 밀어냄
                    score[0] += 1

            if hand["type"] == "Right":
                img = cvzone.overlayPNG(img, imgBat2, (1195, y1))  # 핸들 그리기
                if 1195 - 50 < ballPos[0] < 1195 and y1 < ballPos[1] < y1 + h1:  # 공 충돌시
                    speedX = -speedX  # 방향 반대로 전환
                    ballPos[0] -= 30  # 공을 왼쪽으로 밀어냄
                    score[1] += 1

    # 게임 오버 조건
    if ballPos[0] < 40 or ballPos[0] > 1200:
        gameOver = True

    if gameOver:
        img = imgGameOver
        cv2.putText(
            img,
            str(score[1] + score[0]).zfill(2),
            (585, 360),
            cv2.FONT_HERSHEY_COMPLEX,
            2.5,
            (200, 0, 200),
            5,
        )

    # 게임 진행 중일 때, 공 이동
    else:
        # 공의 경계에서 튕기게 하기
        if ballPos[1] >= 500 or ballPos[1] <= 10:
            speedY = -speedY

        ballPos[0] += speedX
        ballPos[1] += speedY

        # 공 그리기
        img = cvzone.overlayPNG(img, imgBall, ballPos)

        # 플레이어 1과 플레이어 2의 점수 표시
        cv2.putText(
            img,
            str(score[0]),
            (300, 650),
            cv2.FONT_HERSHEY_COMPLEX,
            3,
            (255, 255, 255),
            5,
        )
        cv2.putText(
            img,
            str(score[1]),
            (900, 650),
            cv2.FONT_HERSHEY_COMPLEX,
            3,
            (255, 255, 255),
            5,
        )

    # 원본 이미지를 리사이즈하여 화면에 추가
    img[580:700, 20:233] = cv2.resize(imgRaw, (213, 120))

    # 게임 화면 표시
    cv2.imshow("Speed Hockey", img)

    # 키 입력 대기
    key = cv2.waitKey(1)

    # "r" 키를 누르면 게임 재시작
    if key == ord("r"):
        ballPos = [100, 100]
        speedX = 40
        speedY = 40
        gameOver = False
        score = [0, 0]
        imgGameOver = cv2.imread("gameOver.png")
    if key == ord("q"):
        break
