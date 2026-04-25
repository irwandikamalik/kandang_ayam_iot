import cv2

class Camera:
    def __init__(self):
        self.cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

        # optional: kecilin resolusi biar ringan
        self.cap.set(3, 320)
        self.cap.set(4, 240)

    def read(self):
        success, frame = self.cap.read()
        return frame if success else None

    def get_frame(self):
        frame = self.read()
        if frame is None:
            return None

        # encode ke jpg
        ret, buffer = cv2.imencode(
            '.jpg',
            frame,
            [int(cv2.IMWRITE_JPEG_QUALITY), 60]
        )
        return buffer.tobytes()

    def release(self):
        self.cap.release()


# 🔥 DI LUAR CLASS
def gen_frames(camera):
    while True:
        frame = camera.get_frame()
        if frame is None:
            break

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')