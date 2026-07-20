"""
face_utils.py
Helper functions for capturing a student's face and generating
a face "encoding" (a 128-number fingerprint used to recognize them later).
"""

import cv2
import face_recognition
import numpy as np
from config import CAMERA_INDEX, PHOTOS_PER_STUDENT


def capture_face_encoding(status_callback=None):
    """
    Opens the webcam, waits until a face is clearly detected,
    captures several samples, and returns the AVERAGE encoding.

    `status_callback`, if provided, is called with a string message
    so the GUI can show progress (e.g. "Captured 2/5").

    Returns:
        numpy array (the face encoding) on success, or None if the
        user pressed 'q' to cancel before enough captures were taken.
    """
    video = cv2.VideoCapture(CAMERA_INDEX)
    encodings_collected = []

    while len(encodings_collected) < PHOTOS_PER_STUDENT:
        ret, frame = video.read()
        if not ret:
            continue

        # face_recognition works with RGB, OpenCV gives BGR
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        face_locations = face_recognition.face_locations(rgb_frame)

        # Draw a box around any detected face so the user can see it
        for (top, right, bottom, left) in face_locations:
            cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)

        cv2.putText(
            frame,
            f"Captured: {len(encodings_collected)}/{PHOTOS_PER_STUDENT}  (press SPACE to capture, q to cancel)",
            (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2
        )
        cv2.imshow("Register Student - Face Capture", frame)

        key = cv2.waitKey(1) & 0xFF

        if key == ord(' ') and len(face_locations) == 1:
            encoding = face_recognition.face_encodings(rgb_frame, face_locations)[0]
            encodings_collected.append(encoding)
            if status_callback:
                status_callback(f"Captured {len(encodings_collected)}/{PHOTOS_PER_STUDENT}")

        elif key == ord(' ') and len(face_locations) != 1:
            if status_callback:
                status_callback("Make sure exactly ONE face is visible, then press SPACE again")

        elif key == ord('q'):
            video.release()
            cv2.destroyAllWindows()
            return None

    video.release()
    cv2.destroyAllWindows()

    # Average the samples into one stable encoding
    average_encoding = np.mean(encodings_collected, axis=0)
    return average_encoding


def run_attendance_session(known_students, on_recognized, status_callback=None):
    """
    Opens the webcam and continuously looks for faces, matching them
    against `known_students` (a list of (student_id, roll_no, name, encoding)).

    Every time a NEW face is recognized, `on_recognized(student_id, roll_no, name)`
    is called so the caller can mark attendance in the database.

    Press 'q' in the video window to stop the session.
    """
    from config import FACE_MATCH_TOLERANCE

    known_encodings = [s[3] for s in known_students]
    already_greeted_this_session = set()

    video = cv2.VideoCapture(CAMERA_INDEX)

    while True:
        ret, frame = video.read()
        if not ret:
            continue

        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        face_locations = face_recognition.face_locations(rgb_frame)
        face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

        for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
            matches = face_recognition.compare_faces(
                known_encodings, face_encoding, tolerance=FACE_MATCH_TOLERANCE
            )
            name_label = "Unknown"
            box_color = (0, 0, 255)  # red for unknown

            if True in matches:
                distances = face_recognition.face_distance(known_encodings, face_encoding)
                best_match_index = np.argmin(distances)
                if matches[best_match_index]:
                    student_id, roll_no, name, _ = known_students[best_match_index]
                    name_label = f"{name} ({roll_no})"
                    box_color = (0, 255, 0)  # green for recognized

                    if student_id not in already_greeted_this_session:
                        already_greeted_this_session.add(student_id)
                        on_recognized(student_id, roll_no, name)
                        if status_callback:
                            status_callback(f"Marked present: {name} ({roll_no})")

            cv2.rectangle(frame, (left, top), (right, bottom), box_color, 2)
            cv2.putText(frame, name_label, (left, top - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, box_color, 2)

        cv2.putText(frame, "Press 'q' to finish attendance", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        cv2.imshow("Take Attendance", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    video.release()
    cv2.destroyAllWindows()
