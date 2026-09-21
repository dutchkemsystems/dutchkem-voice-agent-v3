import numpy as np

# EAR threshold for blink detection (typical value)
EAR_THRESHOLD = 0.21
# Head movement threshold in degrees
HEAD_MOVEMENT_THRESHOLD = 5.0

# 3D face model points for solvePnP (nose tip, chin, eye corners, mouth corners)
_3D_FACE_MODEL = np.array(
    [
        [0.0, 0.0, 0.0],  # Nose tip
        [0.0, -330.0, -65.0],  # Chin
        [-225.0, 170.0, -135.0],  # Left eye outer corner
        [225.0, 170.0, -135.0],  # Right eye outer corner
        [-150.0, -150.0, -125.0],  # Left mouth corner
        [150.0, -150.0, -125.0],  # Right mouth corner
    ],
    dtype=np.float64,
)

# Camera matrix approximation (standard 640x480)
_CAM_MATRIX = np.array(
    [
        [640.0, 0.0, 320.0],
        [0.0, 640.0, 240.0],
        [0.0, 0.0, 1.0],
    ],
    dtype=np.float64,
)


class LivenessDetector:
    def _detect_landmarks(self, frame: np.ndarray) -> dict:
        """Detect facial landmarks and compute Eye Aspect Ratio (EAR)."""
        try:
            import cv2

            # ponytail: mediapipe preferred, fallback to mediapipe directly
            import mediapipe as mp

            face_mesh = mp.solutions.face_mesh.FaceMesh(
                static_image_mode=True,
                max_num_faces=1,
                refine_landmarks=True,
            )
            rgb = (
                cv2.cvtColor(frame, cv2.COLOR_BGR2RGB) if frame.shape[2] == 3 else frame
            )
            results = face_mesh.process(rgb)
            face_mesh.close()

            if not results.multi_face_landmarks:
                return {"left_ear": 0.0, "right_ear": 0.0}

            lm = results.multi_face_landmarks[0]
            h, w = frame.shape[:2]

            # Left eye: indices 33, 160, 158, 133, 153, 144 (EAR formula)
            left_eye = [
                (lm.landmark[i].x * w, lm.landmark[i].y * h)
                for i in [33, 160, 158, 133, 153, 144]
            ]
            # Right eye: indices 362, 385, 387, 263, 373, 380
            right_eye = [
                (lm.landmark[i].x * w, lm.landmark[i].y * h)
                for i in [362, 385, 387, 263, 373, 380]
            ]

            def ear(eye):
                v1 = np.linalg.norm(np.array(eye[1]) - np.array(eye[5]))
                v2 = np.linalg.norm(np.array(eye[2]) - np.array(eye[4]))
                h_ = np.linalg.norm(np.array(eye[0]) - np.array(eye[3]))
                return (v1 + v2) / (2.0 * h_) if h_ > 1e-6 else 0.0

            return {"left_ear": ear(left_eye), "right_ear": ear(right_eye)}
        except ImportError:
            return {"left_ear": 0.0, "right_ear": 0.0}

    def _get_head_pose(self, frame: np.ndarray) -> dict:
        """Estimate head pose (yaw, pitch, roll) from facial landmarks."""
        try:
            import cv2
            import mediapipe as mp

            face_mesh = mp.solutions.face_mesh.FaceMesh(
                static_image_mode=True,
                max_num_faces=1,
            )
            rgb = (
                cv2.cvtColor(frame, cv2.COLOR_BGR2RGB) if frame.shape[2] == 3 else frame
            )
            results = face_mesh.process(rgb)
            face_mesh.close()

            if not results.multi_face_landmarks:
                return {"yaw": 0.0, "pitch": 0.0, "roll": 0.0}

            lm = results.multi_face_landmarks[0]
            h, w = frame.shape[:2]

            # Map mediapipe landmarks to 6 points for solvePnP
            # Nose tip(1), Chin(152), Left eye outer(33), Right eye outer(263), Left mouth(61), Right mouth(291)
            indices = [1, 152, 33, 263, 61, 291]
            image_points = np.array(
                [[lm.landmark[i].x * w, lm.landmark[i].y * h] for i in indices],
                dtype=np.float64,
            )

            success, rvec, tvec = cv2.solvePnP(
                _3D_FACE_MODEL,
                image_points,
                _CAM_MATRIX,
                None,
                flags=cv2.SOLVEPNP_ITERATIVE,
            )
            if not success:
                return {"yaw": 0.0, "pitch": 0.0, "roll": 0.0}

            rmat, _ = cv2.Rodrigues(rvec)
            # 分解为yaw/pitch/roll
            sy = np.sqrt(rmat[0, 0] ** 2 + rmat[1, 0] ** 2)
            if sy < 1e-6:
                yaw = np.degrees(np.arctan2(-rmat[2, 0], sy))
                pitch = np.degrees(np.arctan2(-rmat[2, 1], rmat[2, 2]))
                roll = np.degrees(np.arctan2(-rmat[1, 0], rmat[0, 0]))
            else:
                yaw = np.degrees(np.arctan2(rmat[1, 0], rmat[0, 0]))
                pitch = np.degrees(np.arctan2(-rmat[2, 0], sy))
                roll = 0.0

            return {"yaw": float(yaw), "pitch": float(pitch), "roll": float(roll)}
        except ImportError:
            return {"yaw": 0.0, "pitch": 0.0, "roll": 0.0}

    def _analyze_texture(self, image: np.ndarray) -> dict:
        """Analyze image texture for anti-spoofing (real vs photo/screen)."""
        try:
            import cv2

            gray = (
                cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
                if len(image.shape) == 3
                else image
            )

            # ponytail: basic frequency analysis — spoof images have different DCT patterns
            # Real faces have natural texture variation; prints/screens have moiré
            small = cv2.resize(gray, (64, 64)).astype(np.float32)
            dct = cv2.dct(small)
            # High-frequency energy ratio (top-left 8x8 vs full)
            low_energy = np.sum(dct[:8, :8] ** 2)
            total_energy = np.sum(dct**2)
            hf_ratio = 1.0 - (low_energy / (total_energy + 1e-8))

            # Real faces typically have hf_ratio between 0.3-0.7
            # Very low = suspicious (flat print), very high = suspicious (screen moiré)
            if 0.25 < hf_ratio < 0.75:
                real_score = 0.85 + 0.1 * (1.0 - abs(hf_ratio - 0.5) / 0.25)
            else:
                real_score = 0.4 + 0.2 * min(abs(hf_ratio - 0.5), 0.5)

            return {"real_score": float(np.clip(real_score, 0.0, 1.0))}
        except Exception:
            return {"real_score": 0.5}

    def check_blink(self, frames: list) -> dict:
        """Detect blink across a sequence of frames using EAR."""
        blink_count = 0
        prev_open = True

        for frame in frames:
            landmarks = self._detect_landmarks(frame)
            avg_ear = (landmarks["left_ear"] + landmarks["right_ear"]) / 2.0
            is_open = avg_ear > EAR_THRESHOLD

            if prev_open and not is_open:
                blink_count += 1
            prev_open = is_open

        return {"blink_detected": blink_count > 0, "blink_count": blink_count}

    def check_head_movement(self, frames: list) -> dict:
        """Detect head movement across frames."""
        if len(frames) < 2:
            return {"head_movement": False, "max_yaw": 0.0, "max_pitch": 0.0}

        max_yaw = 0.0
        max_pitch = 0.0

        for i in range(1, len(frames)):
            prev_pose = self._get_head_pose(frames[i - 1])
            curr_pose = self._get_head_pose(frames[i])
            yaw_diff = abs(curr_pose["yaw"] - prev_pose["yaw"])
            pitch_diff = abs(curr_pose["pitch"] - prev_pose["pitch"])
            max_yaw = max(max_yaw, yaw_diff)
            max_pitch = max(max_pitch, pitch_diff)

        moved = max_yaw > HEAD_MOVEMENT_THRESHOLD or max_pitch > HEAD_MOVEMENT_THRESHOLD
        return {"head_movement": moved, "max_yaw": max_yaw, "max_pitch": max_pitch}

    def anti_spoof_check(self, image: np.ndarray) -> dict:
        """Check if the face is real or a spoof (photo/screen attack)."""
        texture = self._analyze_texture(image)
        is_real = texture["real_score"] > 0.5
        return {"is_real": is_real, "confidence": texture["real_score"]}
