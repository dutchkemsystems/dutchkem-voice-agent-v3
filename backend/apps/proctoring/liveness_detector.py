import numpy as np

# EAR threshold for blink detection (typical value)
EAR_THRESHOLD = 0.21
# Head movement threshold in degrees
HEAD_MOVEMENT_THRESHOLD = 5.0


class LivenessDetector:
    def _detect_landmarks(self, frame: np.ndarray) -> dict:
        """Detect facial landmarks and compute Eye Aspect Ratio (EAR)."""
        # Placeholder: in production, use dlib/mediapipe landmarks
        # Returns EAR for left and right eyes
        return {"left_ear": 0.35, "right_ear": 0.35}

    def _get_head_pose(self, frame: np.ndarray) -> dict:
        """Estimate head pose (yaw, pitch, roll) from facial landmarks."""
        # Placeholder: in production, use solvePnP with 68 landmarks
        return {"yaw": 0.0, "pitch": 0.0, "roll": 0.0}

    def _analyze_texture(self, image: np.ndarray) -> dict:
        """Analyze image texture for anti-spoofing (real vs photo/screen)."""
        # Placeholder: in production, use LBP/DMD/remote face anti-spoofing
        return {"real_score": 0.95}

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
