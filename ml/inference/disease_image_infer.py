"""
Scaffold for a future image-based crop disease detection model (e.g. a CNN
trained on leaf-image datasets such as PlantVillage).

This module deliberately mirrors the function signature style of
disease_risk_infer.predict() so the FastAPI route/service layer can call
either path — or both, and combine them — without changing its own code.

NOT YET IMPLEMENTED: no image model is trained or bundled in this project.
Calling predict_from_image() raises NotImplementedError with guidance on how
to wire in a real model once one exists. This file exists purely so the
integration point is already in place, per the "structure the backend so an
image-based model can be added later" requirement.

--- How to complete this later ---
1. Collect/obtain a labeled leaf-image dataset (e.g. PlantVillage, or your
   own field photos) organized as ml/datasets/images/<class_name>/*.jpg.
2. Add a training script ml/training/train_disease_image_model.py that:
   - loads images with e.g. torchvision.datasets.ImageFolder or tf.data,
   - fine-tunes a small pretrained CNN (MobileNetV2/EfficientNet-B0 are good
     starting points for a farmer-facing mobile-friendly model),
   - evaluates with accuracy/precision/recall/F1 + confusion matrix like the
     other training scripts in this project,
   - saves the model (e.g. TorchScript, SavedModel, or ONNX) into
     ml/saved_models/disease_image_model/.
3. Implement `predict_from_image()` below to load that model once at import
   time (mirroring every other inference module in this package) and run
   inference on the given image bytes.
4. In backend/app/services/ml_service.py, add a thin wrapper function and
   call it from a new route (e.g. POST /api/disease/predict-image accepting
   an UploadFile) — no changes needed to the structured-data disease route
   or model.
"""
from typing import Optional


class DiseaseImageModelNotAvailable(NotImplementedError):
    """Raised until a real image-based model is trained and wired in."""


def predict_from_image(image_bytes: bytes, crop: Optional[str] = None) -> dict:
    """
    Intended future signature: takes raw image bytes (e.g. a photo of a leaf)
    and an optional crop hint, and returns a dict shaped like
    disease_risk_infer.predict()'s output so callers can treat both
    interchangeably:

        {
            "risk_level": "high",
            "risk_percentage": 87.4,
            "possible_disease_category": "Late Blight",
            "preventive_suggestions": [...],
            "class_probabilities": {...},
            "source": "image_model",
        }
    """
    raise DiseaseImageModelNotAvailable(
        "No image-based disease detection model is trained/bundled yet. "
        "See the module docstring in ml/inference/disease_image_infer.py "
        "for how to add one without changing any route or service code."
    )
