import os
import cv2
import numpy as np
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
OUTPUT_DIR = BASE_DIR / "videos"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_FILE = OUTPUT_DIR / "sample_traffic.mp4"


class VehicleSprite:
    def __init__(
        self,
        vehicle_id: int,
        vehicle_type: str,
        start_x: float,
        start_y: float,
        speed_vy: float,
        speed_vx: float,
        color: tuple,
        plate_text: str,
        start_frame: int,
        end_frame: int
    ):
        self.vehicle_id = vehicle_id
        self.vehicle_type = vehicle_type
        self.x = start_x
        self.y = start_y
        self.vy = speed_vy
        self.vx = speed_vx
        self.color = color
        self.plate_text = plate_text
        self.start_frame = start_frame
        self.end_frame = end_frame

        if vehicle_type == "truck":
            self.base_w = 80
            self.base_h = 130
        elif vehicle_type == "motorcycle":
            self.base_w = 32
            self.base_h = 60
        elif vehicle_type == "bus":
            self.base_w = 85
            self.base_h = 140
        else:  # car
            self.base_w = 64
            self.base_h = 100

    def update(self, frame_idx: int):
        if self.start_frame <= frame_idx <= self.end_frame:
            self.x += self.vx
            self.y += self.vy

    def draw(self, frame: np.ndarray, frame_idx: int):
        if not (self.start_frame <= frame_idx <= self.end_frame):
            return

        h_img, w_img = frame.shape[:2]
        # Perspective scaling factor based on y position (road depth)
        scale = 0.5 + (self.y / 720.0) * 0.9
        w = int(self.base_w * scale)
        h = int(self.base_h * scale)

        cx, cy = int(self.x), int(self.y)
        x1, y1 = cx - w // 2, cy - h // 2
        x2, y2 = cx + w // 2, cy + h // 2

        if y2 < 0 or y1 >= h_img or x2 < 0 or x1 >= w_img:
            return

        # 1. Vehicle Body
        cv2.rectangle(frame, (x1, y1), (x2, y2), self.color, -1)
        cv2.rectangle(frame, (x1, y1), (x2, y2), (20, 20, 20), 2)

        # 2. Windshield / Roof / Windows
        roof_inset_x = int(w * 0.15)
        roof_inset_y = int(h * 0.25)
        cv2.rectangle(
            frame,
            (x1 + roof_inset_x, y1 + roof_inset_y),
            (x2 - roof_inset_x, y2 - roof_inset_y),
            (35, 45, 55),
            -1
        )

        # 3. Headlights / Taillights
        light_w = max(4, int(w * 0.2))
        light_h = max(3, int(h * 0.08))
        if self.vy > 0:  # Moving down -> Taillights at top/rear
            cv2.rectangle(frame, (x1 + 4, y2 - light_h - 2), (x1 + 4 + light_w, y2 - 2), (0, 0, 240), -1)
            cv2.rectangle(frame, (x2 - 4 - light_w, y2 - light_h - 2), (x2 - 4, y2 - 2), (0, 0, 240), -1)
        else:  # Moving up -> Headlights
            cv2.rectangle(frame, (x1 + 4, y1 + 2), (x1 + 4 + light_w, y1 + 2 + light_h), (0, 240, 255), -1)
            cv2.rectangle(frame, (x2 - 4 - light_w, y1 + 2), (x2 - 4, y1 + 2 + light_h), (0, 240, 255), -1)

        # 4. License Plate Area (White badge with dark letters)
        plate_w = int(w * 0.65)
        plate_h = max(14, int(h * 0.16))
        px1 = cx - plate_w // 2
        py1 = y2 - plate_h - 4
        px2 = cx + plate_w // 2
        py2 = y2 - 4

        cv2.rectangle(frame, (px1, py1), (px2, py2), (245, 245, 245), -1)
        cv2.rectangle(frame, (px1, py1), (px2, py2), (30, 30, 30), 1)

        # Draw Plate Text
        font_scale = max(0.28, 0.38 * scale)
        cv2.putText(
            frame,
            self.plate_text,
            (px1 + 3, py2 - 3),
            cv2.FONT_HERSHEY_SIMPLEX,
            font_scale,
            (10, 10, 10),
            1,
            cv2.LINE_AA
        )


def generate_sample_traffic_video(
    output_path: str = str(OUTPUT_FILE),
    duration_seconds: int = 20,
    fps: int = 30
):
    """Generates a realistic 1280x720 synthetic traffic simulation video."""
    width, height = 1280, 720
    total_frames = duration_seconds * fps

    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

    print(f"Generating synthetic traffic video: {output_path} ({total_frames} frames)...")

    # Define vehicle population
    vehicles = [
        # Vehicle 1: Standard Commuter Car (Lane 1, ~50 km/h)
        VehicleSprite(1, "car", 380, 100, 4.2, 0.1, (200, 70, 40), "MH02CB1234", 0, 160),
        # Vehicle 2: Speeding Red Sports Car (Lane 2, ~90 km/h - Triggers OVERSPEED)
        VehicleSprite(2, "car", 820, 50, 8.5, 0.0, (20, 20, 220), "DL01AX9988", 30, 130),
        # Vehicle 3: Delivery Truck (Lane 2, ~42 km/h)
        VehicleSprite(3, "truck", 880, 80, 3.6, 0.0, (180, 180, 180), "KA05MK4422", 80, 260),
        # Vehicle 4: Commuter Motorcycle (Lane 1, ~52 km/h)
        VehicleSprite(4, "motorcycle", 430, 80, 4.4, -0.05, (30, 180, 30), "TS08EE5566", 120, 280),
        # Vehicle 5: City Bus (Lane 1, ~45 km/h)
        VehicleSprite(5, "bus", 360, 60, 3.8, 0.05, (0, 140, 255), "UP32BZ7711", 180, 360),
        # Vehicle 6: Red-Light Runner / Late Speeding SUV (Lane 2, ~78 km/h)
        VehicleSprite(6, "car", 800, 70, 6.8, -0.1, (130, 40, 150), "HR26DK3399", 240, 390),
        # Vehicle 7: Additional Commuter Car (Lane 1, ~48 km/h)
        VehicleSprite(7, "car", 400, 90, 4.0, 0.0, (60, 120, 190), "GJ01TR8800", 320, 480),
        # Vehicle 8: Fast Sedan (Lane 2, ~82 km/h - Triggers OVERSPEED)
        VehicleSprite(8, "car", 840, 80, 7.5, 0.0, (50, 50, 50), "AP39XX1234", 380, 520),
        # Vehicle 9: Motorcycle (Lane 2, ~45 km/h)
        VehicleSprite(9, "motorcycle", 760, 100, 4.1, 0.0, (200, 120, 20), "KL07BH4321", 440, 590),
    ]

    for frame_idx in range(total_frames):
        # 1. Create Base Background (Asphalt Road, Grass, Sky)
        frame = np.zeros((height, width, 3), dtype=np.uint8)

        # Sky / Horizon
        frame[0:220, :] = [180, 140, 90]  # Light sky
        # Roadside Grass / Terrain
        frame[220:height, :] = [45, 80, 45]

        # 2. Draw Perspective Asphalt Highway
        # Road trapezoid: top (300, 220) to (980, 220), bottom (60, 720) to (1220, 720)
        road_pts = np.array([[300, 220], [980, 220], [1220, 720], [60, 720]], dtype=np.int32)
        cv2.fillPoly(frame, [road_pts], (50, 52, 55))

        # Road Outer Shoulders (Solid White lines)
        cv2.line(frame, (300, 220), (60, 720), (230, 230, 230), 4)
        cv2.line(frame, (980, 220), (1220, 720), (230, 230, 230), 4)

        # Center Lane Divider (Dashed Yellow/White line)
        for seg_y in range(230, 720, 45):
            t1 = (seg_y - 220) / 500.0
            t2 = (seg_y + 25 - 220) / 500.0
            cx1 = int(640 * (1 - t1) + 640 * t1)
            cx2 = int(640 * (1 - t2) + 640 * t2)
            cv2.line(frame, (cx1, seg_y), (cx2, min(720, seg_y + 25)), (0, 215, 255), int(2 + t1 * 3))

        # Lane Markings (Dashed white dividers for sub-lanes)
        for seg_y in range(240, 720, 50):
            t1 = (seg_y - 220) / 500.0
            t2 = (seg_y + 22 - 220) / 500.0
            # Left lane divider
            lx1 = int(470 * (1 - t1) + 350 * t1)
            lx2 = int(470 * (1 - t2) + 350 * t2)
            cv2.line(frame, (lx1, seg_y), (lx2, min(720, seg_y + 22)), (200, 200, 200), int(1 + t1 * 2))

            # Right lane divider
            rx1 = int(810 * (1 - t1) + 930 * t1)
            rx2 = int(810 * (1 - t2) + 930 * t2)
            cv2.line(frame, (rx1, seg_y), (rx2, min(720, seg_y + 22)), (200, 200, 200), int(1 + t1 * 2))

        # 3. Draw Virtual Stop Line Marks / Crosswalk Stripes on the road
        stop_y = 500
        cv2.line(frame, (180, stop_y), (1100, stop_y), (240, 240, 240), 3)

        # 4. Update and Draw Vehicles
        for v in vehicles:
            v.update(frame_idx)
            v.draw(frame, frame_idx)

        # Write frame to video
        out.write(frame)

    out.release()
    print(f"Sample traffic video generated successfully: {output_path}")
    return output_path


if __name__ == "__main__":
    generate_sample_traffic_video()
