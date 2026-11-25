import logging
from typing import Dict, List, Optional
import numpy as np
from ai.detection.yolo_detector import Detection
from ai.tracking.trajectory import VehicleTrack

logger = logging.getLogger(__name__)


class ByteTrackTracker:
    """Manages active vehicle tracks and trajectory state."""
    
    def __init__(self, max_missing_frames: int = 30, history_length: int = 60):
        self.tracks: Dict[int, VehicleTrack] = {}
        self.max_missing_frames = max_missing_frames
        self.history_length = history_length
        self._next_id = 1

    def update_tracks(
        self,
        detections: List[Detection],
        frame_idx: int,
        timestamp: float
    ) -> Dict[int, VehicleTrack]:
        """
        Update tracking state given new detections.
        Matches detections to existing tracks or creates new ones.
        """
        current_frame_ids = set()

        for det in detections:
            track_id = det.track_id
            
            # If detector didn't assign an ID, assign an internal ID based on nearest centroid
            if track_id is None:
                track_id = self._match_or_assign_id(det, frame_idx)
                det.track_id = track_id

            current_frame_ids.add(track_id)

            if track_id not in self.tracks:
                self.tracks[track_id] = VehicleTrack(
                    track_id=track_id,
                    class_name=det.class_name,
                    class_id=det.class_id,
                    initial_bbox=det.bbox,
                    frame_idx=frame_idx,
                    timestamp=timestamp,
                    max_history=self.history_length
                )
            else:
                self.tracks[track_id].update(
                    bbox=det.bbox,
                    frame_idx=frame_idx,
                    timestamp=timestamp
                )

        # Cleanup stale tracks
        stale_ids = [
            tid for tid, track in self.tracks.items()
            if track.is_stale(frame_idx, self.max_missing_frames)
        ]
        for tid in stale_ids:
            del self.tracks[tid]

        return self.tracks

    def _match_or_assign_id(self, det: Detection, frame_idx: int) -> int:
        """Fallback matching: finds closest existing track or creates new ID."""
        best_id = None
        min_dist = float("inf")
        det_cx, det_cy = det.centroid

        for tid, track in self.tracks.items():
            if track.last_frame_idx == frame_idx:
                continue  # Already matched in this frame
            
            last_entry = track.history[-1]
            last_cx, last_cy = last_entry[2]  # centroid
            dist = np.hypot(det_cx - last_cx, det_cy - last_cy)
            
            # If distance is within bounding box scale
            max_allowed_dist = max(det.width, det.height) * 1.5
            if dist < max_allowed_dist and dist < min_dist:
                min_dist = dist
                best_id = tid

        if best_id is not None:
            return best_id
        
        assigned_id = self._next_id
        self._next_id += 1
        return assigned_id

    def get_track(self, track_id: int) -> Optional[VehicleTrack]:
        return self.tracks.get(track_id)

    def get_active_tracks(self) -> Dict[int, VehicleTrack]:
        return self.tracks

    def clear(self):
        self.tracks.clear()
        self._next_id = 1
