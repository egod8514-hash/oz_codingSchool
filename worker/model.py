# -*- coding: utf-8 -*-

import io
import os

import torch
import torch.nn as nn
from torchvision import transforms
from PIL import Image


# =========================================================
# 1. 모델 기본 설정
# =========================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

MODEL_STATE_DICT_PATH = os.path.join(
    BASE_DIR,
    "models",
    "model_state_dict.pth",
)

MODEL_NAME = "PneumoniaModel-v1"


# =========================================================
# 2. SimpleCNN 모델 구조
# =========================================================

class SimpleCNN(nn.Module):
    def __init__(self):
        super().__init__()

        self.conv = nn.Sequential(
            nn.Conv2d(
                in_channels=1,
                out_channels=16,
                kernel_size=3,
                stride=1,
                padding=1,
            ),
            nn.ReLU(),
            nn.MaxPool2d(
                kernel_size=2,
                stride=2,
            ),

            nn.Conv2d(
                in_channels=16,
                out_channels=32,
                kernel_size=3,
                stride=1,
                padding=1,
            ),
            nn.ReLU(),
            nn.MaxPool2d(
                kernel_size=2,
                stride=2,
            ),
        )

        self.fc = nn.Sequential(
            nn.Flatten(),
            nn.Linear(32768, 2),
        )

    def forward(self, x):
        x = self.conv(x)
        x = self.fc(x)

        return x


# =========================================================
# 3. X-ray 이미지 전처리
# =========================================================

transform = transforms.Compose([
    transforms.Grayscale(num_output_channels=1),
    transforms.Resize((128, 128)),
    transforms.ToTensor(),
])


# =========================================================
# 4. 폐렴 예측 클래스
# =========================================================

class PneumoniaPredictor:
    def __init__(self):
        # GPU 사용 가능하면 GPU, 아니면 CPU
        self.device = torch.device(
            "cuda" if torch.cuda.is_available() else "cpu"
        )

        self.model_name = MODEL_NAME

        # 모델 로딩
        self.model = self._load_model()

        # 추론 모드
        self.model.eval()

        # 폐렴 판정 임계값
        # 추후 validation 데이터로 성능 검증 후 조정 가능
        self.decision_threshold = 0.35

    def _load_model(self) -> torch.nn.Module:
        """
        SimpleCNN 구조를 생성하고
        model_state_dict.pth의 학습된 가중치를 불러옵니다.
        """

        if not os.path.exists(MODEL_STATE_DICT_PATH):
            raise FileNotFoundError(
                f"모델 파일을 찾을 수 없습니다: "
                f"{MODEL_STATE_DICT_PATH}"
            )

        # SimpleCNN 모델 구조 생성
        model = SimpleCNN()

        # 학습된 가중치 로드
        state_dict = torch.load(
            MODEL_STATE_DICT_PATH,
            map_location=self.device,
            weights_only=True,
        )

        # 모델에 가중치 적용
        model.load_state_dict(state_dict)

        # CPU 또는 GPU로 이동
        model.to(self.device)

        print("=" * 60)
        print("[Worker] 폐렴 AI 모델 로딩 성공")
        print(f"[Worker] 모델명: {self.model_name}")
        print(f"[Worker] 모델 파일: {MODEL_STATE_DICT_PATH}")
        print(f"[Worker] 실행 장치: {self.device}")
        print("=" * 60)

        return model

    def predict(self, image_bytes: bytes) -> dict:
        """
        X-ray 이미지 bytes를 입력받아
        폐렴 여부와 예측 확률을 반환합니다.
        """

        # 이미지 열기
        image = Image.open(
            io.BytesIO(image_bytes)
        ).convert("L")

        # 이미지 전처리
        input_tensor = transform(image)

        # (1, 128, 128)
        # ↓
        # (1, 1, 128, 128)
        input_tensor = input_tensor.unsqueeze(0)

        # CPU 또는 GPU로 이동
        input_tensor = input_tensor.to(self.device)

        # 추론
        with torch.no_grad():
            outputs = self.model(input_tensor)

            probabilities = torch.softmax(
                outputs,
                dim=1,
            )

            # class 1의 확률을 폐렴 확률로 사용
            pneumonia_probability = probabilities[0][1].item()

        # 폐렴 여부 판정
        is_pneumonia = (
            pneumonia_probability
            >= self.decision_threshold
        )

        # 최종 판정에 대한 confidence
        if is_pneumonia:
            confidence = pneumonia_probability
        else:
            confidence = 1.0 - pneumonia_probability

        return {
            "is_pneumonia": is_pneumonia,
            "confidence": round(confidence, 4),
            "pneumonia_probability": round(
                pneumonia_probability,
                4,
            ),
            "model_name": self.model_name,
        }


# =========================================================
# 5. 서버 시작 시 모델을 한 번만 메모리에 로딩
# =========================================================

predictor = PneumoniaPredictor()