import io
import os
import torch
import torch.nn as nn
from torchvision import transforms, models
from PIL import Image

# 1. 모델 파일 경로 설정
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PTH_PATH = os.path.join(BASE_DIR, "models", "model.pth")
MODEL_STATE_DICT_PATH = os.path.join(BASE_DIR, "models", "model_state_dict.pth")

MODEL_NAME = "PneumoniaModel-v1"

# 2. X-ray 이미지 전처리 (224x224 리사이즈, RGB 변환 및 정규화)
transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.Grayscale(num_output_channels=3),  # 3채널 RGB 변환
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
])


class PneumoniaPredictor:
    def __init__(self):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model_name = MODEL_NAME
        self.model = self._load_model()
        self.model.eval()  # 추론 모드 설정

        # NFR-PRED-001 (Recall ≥ 0.90) 달성을 위한 임계값 조정
        self.decision_threshold = 0.35

    def _load_model(self) -> torch.nn.Module:
        """
        worker/models 디렉토리 내의 model.pth 또는 model_state_dict.pth를 메모리에 로드합니다.
        """
        # 케이스 1: 모델 구조 전체가 저장된 model.pth 로드 시도
        if os.path.exists(MODEL_PTH_PATH):
            try:
                model = torch.load(MODEL_PTH_PATH, map_location=self.device)
                model.to(self.device)
                print(f"[Worker] model.pth 로드 성공: {MODEL_PTH_PATH}")
                return model
            except Exception as e:
                print(f"[Worker] model.pth 전체 로드 실패, state_dict 방식으로 전환합니다: {e}")

        # 케이스 2: 가중치만 저장된 model_state_dict.pth 로드 시도
        if os.path.exists(MODEL_STATE_DICT_PATH):
            model = models.resnet18(weights=None)
            num_ftrs = model.fc.in_features
            model.fc = nn.Linear(num_ftrs, 2)

            state_dict = torch.load(MODEL_STATE_DICT_PATH, map_location=self.device)
            model.load_state_dict(state_dict)
            model.to(self.device)
            print(f"[Worker] model_state_dict.pth 로드 성공: {MODEL_STATE_DICT_PATH}")
            return model

        # 기본 인스턴스 예비 생성
        print("[Worker] ⚠️ 모델 파일을 찾을 수 없어 기본 ResNet18 인스턴스를 생성합니다.")
        model = models.resnet18(weights=None)
        model.fc = nn.Linear(model.fc.in_features, 2)
        model.to(self.device)
        return model

    def predict(self, image_bytes: bytes) -> dict:
        """
        업로드된 이미지 바이트 데이터를 입력받아 폐렴 여부와 신뢰도(Confidence)를 예측합니다.
        """
        image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        input_tensor = transform(image).unsqueeze(0).to(self.device)

        with torch.no_grad():
            outputs = self.model(input_tensor)
            probabilities = torch.softmax(outputs, dim=1)

            pneumonia_prob = round(probabilities[0][1].item(), 4)

            # Recall 중심 판정 (임계값 0.35 이상 시 폐렴 진단)
            is_pneumonia = pneumonia_prob >= self.decision_threshold
            confidence = pneumonia_prob if is_pneumonia else round(1.0 - pneumonia_prob, 4)

        return {
            "is_pneumonia": is_pneumonia,
            "confidence": confidence,
            "pneumonia_probability": pneumonia_prob,
            "model_name": self.model_name
        }


# 서버 시작 시 미리 모델을 메모리에 상주 (싱글톤)
predictor = PneumoniaPredictor()
