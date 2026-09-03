import numpy as np

try:
    import insightface
    HAS_INSIGHTFACE = True
except ImportError:
    HAS_INSIGHTFACE = False


class FaceService:
    def __init__(self):
        self._app = None

    def _get_app(self):
        if self._app is None:
            if HAS_INSIGHTFACE:
                self._app = insightface.app.FaceAnalysis(
                    name="buffalo_l",
                    providers=["CUDAExecutionProvider", "CPUExecutionProvider"],
                )
                self._app.prepare(ctx_id=0, det_size=(640, 640))
            else:
                raise RuntimeError("insightface is not installed")
        return self._app

    def detect_and_embed(self, image: np.ndarray) -> list:
        """Detect faces and return embeddings."""
        if not HAS_INSIGHTFACE:
            return []
        app = self._get_app()
        faces = app.get(image)
        return [
            {
                "bbox": face.bbox.tolist(),
                "embedding": face.embedding.tolist(),
                "age": face.age,
                "gender": "M" if face.gender == 1 else "F",
                "is_real": getattr(face, "is_real", 1.0),
            }
            for face in faces
        ]

    def verify(
        self, image1: np.ndarray, image2: np.ndarray, threshold: float = 0.4
    ) -> dict:
        """Verify if two faces are the same person."""
        faces1 = self.detect_and_embed(image1)
        faces2 = self.detect_and_embed(image2)

        if not faces1 or not faces2:
            return {"verified": False, "confidence": 0.0}

        emb1 = np.array(faces1[0]["embedding"])
        emb2 = np.array(faces2[0]["embedding"])
        norm1 = np.linalg.norm(emb1)
        norm2 = np.linalg.norm(emb2)
        if norm1 == 0.0 or norm2 == 0.0:
            similarity = 0.0
        else:
            similarity = float(np.dot(emb1, emb2) / (norm1 * norm2))

        return {
            "verified": similarity > threshold,
            "confidence": similarity,
        }
