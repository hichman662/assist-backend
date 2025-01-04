import base64
import numpy as np
import cv2
import mediapipe as mp
import time


class SignLanguageService:
    # Initialize MediaPipe Hands model
    mp_hands = mp.solutions.hands.Hands(static_image_mode=False, max_num_hands=2, min_detection_confidence=0.7)
    current_sentence = ""  # Accumulated sentence from gestures
    last_gestures = None  # Store the last detected gestures
    last_detection_time = 0  # Store the last time gestures were detected

    @staticmethod
    def detect_gesture(hand_landmarks):
        """
        Recognize gestures using MediaPipe landmarks.
        Args:
            hand_landmarks: MediaPipe hand landmarks.
        Returns:
            str: Detected gesture label.
        """
        # Get landmark coordinates
        thumb_tip = hand_landmarks.landmark[mp.solutions.hands.HandLandmark.THUMB_TIP]
        index_tip = hand_landmarks.landmark[mp.solutions.hands.HandLandmark.INDEX_FINGER_TIP]
        middle_tip = hand_landmarks.landmark[mp.solutions.hands.HandLandmark.MIDDLE_FINGER_TIP]
        ring_tip = hand_landmarks.landmark[mp.solutions.hands.HandLandmark.RING_FINGER_TIP]
        pinky_tip = hand_landmarks.landmark[mp.solutions.hands.HandLandmark.PINKY_TIP]
        wrist = hand_landmarks.landmark[mp.solutions.hands.HandLandmark.WRIST]

        # Alphabets (examples, include additional logic for each letter)
        if thumb_tip.y < index_tip.y and all(finger_tip.y > thumb_tip.y for finger_tip in [middle_tip, ring_tip, pinky_tip]):
            return "A"
        if index_tip.y < wrist.y and all(finger_tip.y < wrist.y for finger_tip in [middle_tip, ring_tip, pinky_tip]) and thumb_tip.y > wrist.y:
            return "B"
        if all(finger_tip.x < thumb_tip.x for finger_tip in [index_tip, middle_tip, ring_tip, pinky_tip]):
            return "C"
        if thumb_tip.y > wrist.y and index_tip.y < wrist.y and middle_tip.y > wrist.y:
            return "D"
        if all(finger_tip.y > thumb_tip.y for finger_tip in [index_tip, middle_tip, ring_tip, pinky_tip]):
            return "E"
        if index_tip.y < wrist.y and thumb_tip.x < index_tip.x:
            return "F"
        if index_tip.y < middle_tip.y < wrist.y:
            return "G"
        if thumb_tip.x > index_tip.x > middle_tip.x:
            return "H"
        if thumb_tip.x < index_tip.x and index_tip.y < thumb_tip.y:
            return "I"
        if index_tip.x < thumb_tip.x and pinky_tip.x > index_tip.x:
            return "J"
        if thumb_tip.y < middle_tip.y and index_tip.y > middle_tip.y:
            return "K"
        if index_tip.x < middle_tip.x < pinky_tip.x:
            return "L"
        # Add more logic for M to Z...

        # Numbers (examples, include additional logic for 0–9)
        if all(finger_tip.y > wrist.y for finger_tip in [index_tip, middle_tip, ring_tip, pinky_tip, thumb_tip]):
            return "0"
        if index_tip.y < wrist.y and all(finger_tip.y > wrist.y for finger_tip in [middle_tip, ring_tip, pinky_tip, thumb_tip]):
            return "1"
        if index_tip.y < wrist.y and middle_tip.y < wrist.y and all(finger_tip.y > wrist.y for finger_tip in [ring_tip, pinky_tip, thumb_tip]):
            return "2"
        if all(finger_tip.y < wrist.y for finger_tip in [index_tip, middle_tip, ring_tip]) and pinky_tip.y > wrist.y:
            return "3"
        if all(finger_tip.y < wrist.y for finger_tip in [index_tip, middle_tip, ring_tip, pinky_tip]) and thumb_tip.y > wrist.y:
            return "4"
        # Add logic for 5–9...

        # Common Gestures
        if thumb_tip.y < wrist.y and all(finger_tip.y > wrist.y for finger_tip in [index_tip, middle_tip, ring_tip, pinky_tip]):
            return "Thumbs Up"
        if thumb_tip.y > wrist.y and all(finger_tip.y > wrist.y for finger_tip in [index_tip, middle_tip, ring_tip, pinky_tip]):
            return "Thumbs Down"
        if index_tip.y < wrist.y and middle_tip.y < wrist.y and all(finger_tip.y > wrist.y for finger_tip in [ring_tip, pinky_tip]):
            return "Peace"
        if abs(thumb_tip.x - index_tip.x) < 0.02 and thumb_tip.y < middle_tip.y:
            return "OK"
        if pinky_tip.y < wrist.y and all(finger_tip.y > wrist.y for finger_tip in [index_tip, middle_tip, ring_tip]):
            return "Love"
        if index_tip.y < middle_tip.y and pinky_tip.y < middle_tip.y:
            return "Yes"
        if index_tip.y > wrist.y and pinky_tip.y > wrist.y:
            return "No"

        # Default fallback
        return None

    @staticmethod
    def translate(encoded_frame):
        """
        Translate sign language gestures into text and manage sentence.
        Args:
            encoded_frame (str): Base64-encoded image frame.
        Returns:
            dict: Translated text, sentence, and annotated frame.
        """
        try:
            # Decode the base64 image
            frame_data = base64.b64decode(encoded_frame)
            nparr = np.frombuffer(frame_data, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

            # Process the image with MediaPipe
            results = SignLanguageService.mp_hands.process(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))

            detected_gestures = []

            if results.multi_hand_landmarks:
                for hand_landmarks in results.multi_hand_landmarks:
                    # Detect gesture for each hand
                    gesture = SignLanguageService.detect_gesture(hand_landmarks)
                    if gesture:
                        detected_gestures.append(gesture)

                    # Draw hand landmarks on the image
                    mp.solutions.drawing_utils.draw_landmarks(
                        img, hand_landmarks, mp.solutions.hands.HAND_CONNECTIONS
                    )

                # Combine gestures if multiple hands are detected
                combined_gestures = " + ".join(detected_gestures) if detected_gestures else "Unknown Gesture"

                # Avoid repeated detection of the same gestures
                current_time = time.time()
                if (
                    combined_gestures
                    and combined_gestures != SignLanguageService.last_gestures
                    and (current_time - SignLanguageService.last_detection_time) > 1
                ):
                    SignLanguageService.last_gestures = combined_gestures
                    SignLanguageService.last_detection_time = current_time

                    # Manage sentence formation
                    if combined_gestures == "SPACE":
                        SignLanguageService.current_sentence += " "
                    elif combined_gestures == "CLEAR":
                        SignLanguageService.current_sentence = ""
                    elif combined_gestures != "Unknown Gesture":
                        SignLanguageService.current_sentence += combined_gestures

                # Encode the annotated image back to base64
                _, buffer = cv2.imencode('.jpg', img)
                annotated_frame = base64.b64encode(buffer).decode('utf-8')

                return {
                    "translation": combined_gestures,
                    "sentence": SignLanguageService.current_sentence,
                    "annotated_frame": annotated_frame,
                }
            else:
                return {
                    "translation": "No hand detected or unclear gesture.",
                    "sentence": SignLanguageService.current_sentence,
                    "annotated_frame": None,
                }
        except Exception as e:
            return {
                "translation": f"Error in translation: {e}",
                "sentence": SignLanguageService.current_sentence,
                "annotated_frame": None,
            }
