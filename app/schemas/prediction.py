from pydantic import BaseModel


class PredictionExecuteResponse(BaseModel):
    record_id: int
    is_pneumonia: bool
    confidence: float
    pneumonia_probability: float
    model_name: str