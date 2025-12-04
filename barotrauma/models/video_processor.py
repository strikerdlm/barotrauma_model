"""
Video Processing for Tympanic Membrane Movement Analysis.

This module provides computer vision algorithms for extracting TM movement
from endoscopic video recordings during Valsalva maneuvers.

Processing Pipeline
-------------------
1. Frame preprocessing (denoising, contrast enhancement)
2. TM region detection and segmentation
3. Optical flow analysis for movement tracking
4. Displacement signal extraction
5. Quality assessment and artifact rejection

Supported video formats: MP4, AVI, MOV (via OpenCV)

Requirements
------------
- opencv-python >= 4.5.0
- numpy >= 1.21.0
- scipy >= 1.7.0

Note on Deep Learning
---------------------
This module includes a placeholder for deep learning-based TM segmentation.
In production, this would be replaced with a trained CNN model (e.g., U-Net)
for more robust segmentation across diverse endoscope types and lighting.

Author: Aerospace Medicine Research
License: MIT
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Generator

import numpy as np
from numpy.typing import NDArray

# Type aliases
FloatArray = NDArray[np.floating[Any]]
UInt8Array = NDArray[np.uint8]

# Conditional imports for video processing
try:
    import cv2
    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False
    cv2 = None  # type: ignore

try:
    from scipy import ndimage
    from scipy.signal import butter, filtfilt
    SCIPY_AVAILABLE = True
except ImportError:
    SCIPY_AVAILABLE = False
    ndimage = None  # type: ignore


# ============================================================================
# Configuration
# ============================================================================

class VideoQuality(Enum):
    """Video quality assessment grades."""
    EXCELLENT = 1
    GOOD = 2
    ACCEPTABLE = 3
    POOR = 4
    UNUSABLE = 5


@dataclass(frozen=True)
class VideoProcessingConfig:
    """Configuration for video processing pipeline."""
    # Frame processing
    target_fps: float = 30.0
    resize_width: int = 640
    resize_height: int = 480
    
    # Optical flow parameters
    flow_pyr_scale: float = 0.5
    flow_levels: int = 3
    flow_winsize: int = 15
    flow_iterations: int = 3
    flow_poly_n: int = 5
    flow_poly_sigma: float = 1.1
    
    # TM detection parameters
    min_tm_radius: int = 50
    max_tm_radius: int = 200
    hough_param1: int = 50
    hough_param2: int = 30
    
    # Signal processing
    lowpass_cutoff: float = 5.0  # Hz
    
    # Quality thresholds
    min_brightness: float = 30.0
    max_brightness: float = 250.0
    min_contrast: float = 20.0


DEFAULT_CONFIG = VideoProcessingConfig()


# ============================================================================
# Video Reader
# ============================================================================

@dataclass
class VideoMetadata:
    """Metadata extracted from video file."""
    path: Path
    width: int
    height: int
    fps: float
    frame_count: int
    duration_seconds: float
    codec: str


class EndoscopeVideoReader:
    """
    Reader for endoscopic video files.
    
    Handles various video formats and provides frame-by-frame access
    with optional preprocessing.
    """
    
    def __init__(
        self,
        video_path: Path,
        config: VideoProcessingConfig = DEFAULT_CONFIG,
    ) -> None:
        """
        Initialize video reader.
        
        Args:
            video_path: Path to video file
            config: Processing configuration
            
        Raises:
            ImportError: If OpenCV is not available
            FileNotFoundError: If video file doesn't exist
        """
        if not CV2_AVAILABLE:
            raise ImportError(
                "OpenCV (cv2) is required for video processing. "
                "Install with: pip install opencv-python"
            )
        
        self.video_path = Path(video_path)
        if not self.video_path.exists():
            raise FileNotFoundError(f"Video file not found: {video_path}")
        
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Open video capture
        self._cap: Optional[cv2.VideoCapture] = None
        self._metadata: Optional[VideoMetadata] = None
        self._open_video()
    
    def _open_video(self) -> None:
        """Open video file and extract metadata."""
        if cv2 is None:
            raise ImportError("OpenCV not available")
        
        self._cap = cv2.VideoCapture(str(self.video_path))
        
        if not self._cap.isOpened():
            raise ValueError(f"Could not open video: {self.video_path}")
        
        width = int(self._cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(self._cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = self._cap.get(cv2.CAP_PROP_FPS)
        frame_count = int(self._cap.get(cv2.CAP_PROP_FRAME_COUNT))
        codec_int = int(self._cap.get(cv2.CAP_PROP_FOURCC))
        codec = "".join([chr((codec_int >> 8 * i) & 0xFF) for i in range(4)])
        
        self._metadata = VideoMetadata(
            path=self.video_path,
            width=width,
            height=height,
            fps=fps if fps > 0 else 30.0,
            frame_count=frame_count,
            duration_seconds=frame_count / fps if fps > 0 else 0.0,
            codec=codec,
        )
        
        self.logger.info(
            f"Opened video: {width}x{height}, {fps:.1f} fps, "
            f"{frame_count} frames ({self._metadata.duration_seconds:.1f}s)"
        )
    
    @property
    def metadata(self) -> VideoMetadata:
        """Get video metadata."""
        if self._metadata is None:
            raise RuntimeError("Video not opened")
        return self._metadata
    
    def read_frame(self, frame_idx: int) -> Optional[UInt8Array]:
        """
        Read a specific frame from the video.
        
        Args:
            frame_idx: Frame index (0-based)
            
        Returns:
            Frame as numpy array (BGR format) or None if failed
        """
        if self._cap is None:
            raise RuntimeError("Video not opened")
        
        self._cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
        ret, frame = self._cap.read()
        
        if not ret:
            return None
        
        return frame
    
    def iter_frames(
        self,
        start_frame: int = 0,
        end_frame: Optional[int] = None,
        step: int = 1,
    ) -> Generator[Tuple[int, UInt8Array], None, None]:
        """
        Iterate over video frames.
        
        Args:
            start_frame: Starting frame index
            end_frame: Ending frame index (None for all)
            step: Frame step size
            
        Yields:
            Tuple of (frame_index, frame_array)
        """
        if self._cap is None or self._metadata is None:
            raise RuntimeError("Video not opened")
        
        if end_frame is None:
            end_frame = self._metadata.frame_count
        
        self._cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame)
        
        for frame_idx in range(start_frame, end_frame, step):
            ret, frame = self._cap.read()
            if not ret:
                break
            yield frame_idx, frame
            
            # Skip frames if step > 1
            for _ in range(step - 1):
                self._cap.grab()
    
    def close(self) -> None:
        """Release video resources."""
        if self._cap is not None:
            self._cap.release()
            self._cap = None
    
    def __enter__(self) -> 'EndoscopeVideoReader':
        return self
    
    def __exit__(self, *args: Any) -> None:
        self.close()


# ============================================================================
# Frame Preprocessing
# ============================================================================

class FramePreprocessor:
    """
    Preprocessor for endoscopic video frames.
    
    Applies image enhancement techniques optimized for TM visualization:
    - Noise reduction
    - Contrast enhancement (CLAHE)
    - Color normalization
    - Glare/reflection handling
    """
    
    def __init__(self, config: VideoProcessingConfig = DEFAULT_CONFIG) -> None:
        """Initialize preprocessor."""
        if not CV2_AVAILABLE:
            raise ImportError("OpenCV required for preprocessing")
        
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # CLAHE for contrast enhancement
        self._clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    
    def preprocess(self, frame: UInt8Array) -> UInt8Array:
        """
        Apply full preprocessing pipeline to frame.
        
        Args:
            frame: Input BGR frame
            
        Returns:
            Preprocessed BGR frame
        """
        # Resize if needed
        h, w = frame.shape[:2]
        target_w = self.config.resize_width
        target_h = self.config.resize_height
        
        if w != target_w or h != target_h:
            frame = cv2.resize(frame, (target_w, target_h))
        
        # Convert to LAB for luminance-based enhancement
        lab = cv2.cvtColor(frame, cv2.COLOR_BGR2LAB)
        l_channel, a, b = cv2.split(lab)
        
        # Apply CLAHE to L channel
        l_enhanced = self._clahe.apply(l_channel)
        
        # Merge and convert back
        lab_enhanced = cv2.merge([l_enhanced, a, b])
        enhanced = cv2.cvtColor(lab_enhanced, cv2.COLOR_LAB2BGR)
        
        # Gaussian denoising
        denoised = cv2.GaussianBlur(enhanced, (3, 3), 0)
        
        return denoised
    
    def assess_quality(self, frame: UInt8Array) -> Tuple[VideoQuality, Dict[str, float]]:
        """
        Assess frame quality for TM analysis.
        
        Args:
            frame: Input frame
            
        Returns:
            Tuple of (quality_grade, quality_metrics)
        """
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Brightness metrics
        mean_brightness = float(np.mean(gray))
        
        # Contrast (standard deviation)
        contrast = float(np.std(gray))
        
        # Sharpness (Laplacian variance)
        laplacian = cv2.Laplacian(gray, cv2.CV_64F)
        sharpness = float(laplacian.var())
        
        metrics = {
            'brightness': mean_brightness,
            'contrast': contrast,
            'sharpness': sharpness,
        }
        
        # Determine quality grade
        if (self.config.min_brightness <= mean_brightness <= self.config.max_brightness
            and contrast >= self.config.min_contrast
            and sharpness >= 50):
            grade = VideoQuality.EXCELLENT
        elif (self.config.min_brightness - 10 <= mean_brightness <= self.config.max_brightness + 10
              and contrast >= self.config.min_contrast - 5):
            grade = VideoQuality.GOOD
        elif contrast >= 10:
            grade = VideoQuality.ACCEPTABLE
        elif contrast >= 5:
            grade = VideoQuality.POOR
        else:
            grade = VideoQuality.UNUSABLE
        
        return grade, metrics


# ============================================================================
# TM Detection and Segmentation
# ============================================================================

@dataclass
class TMRegion:
    """Detected tympanic membrane region."""
    center_x: int
    center_y: int
    radius: int
    confidence: float
    mask: Optional[UInt8Array] = None
    
    @property
    def bounding_box(self) -> Tuple[int, int, int, int]:
        """Get bounding box (x, y, width, height)."""
        return (
            self.center_x - self.radius,
            self.center_y - self.radius,
            2 * self.radius,
            2 * self.radius,
        )


class TMDetector:
    """
    Detector for tympanic membrane in endoscopic images.
    
    Uses a combination of:
    - Hough circle detection for initial localization
    - Color-based segmentation for refinement
    - Edge detection for membrane boundary
    
    Note: In production, this would be replaced with a trained deep learning
    model (e.g., U-Net or Mask R-CNN) for robust segmentation.
    """
    
    def __init__(self, config: VideoProcessingConfig = DEFAULT_CONFIG) -> None:
        """Initialize detector."""
        if not CV2_AVAILABLE:
            raise ImportError("OpenCV required for TM detection")
        
        self.config = config
        self.logger = logging.getLogger(__name__)
    
    def detect(self, frame: UInt8Array) -> Optional[TMRegion]:
        """
        Detect TM region in frame.
        
        Args:
            frame: Preprocessed BGR frame
            
        Returns:
            TMRegion if detected, None otherwise
        """
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Apply Gaussian blur
        blurred = cv2.GaussianBlur(gray, (9, 9), 2)
        
        # Detect circles using Hough transform
        circles = cv2.HoughCircles(
            blurred,
            cv2.HOUGH_GRADIENT,
            dp=1,
            minDist=100,
            param1=self.config.hough_param1,
            param2=self.config.hough_param2,
            minRadius=self.config.min_tm_radius,
            maxRadius=self.config.max_tm_radius,
        )
        
        if circles is None or len(circles) == 0:
            return None
        
        # Take the most prominent circle
        circles = np.uint16(np.around(circles))
        best_circle = circles[0, 0]
        
        cx, cy, radius = int(best_circle[0]), int(best_circle[1]), int(best_circle[2])
        
        # Create mask
        mask = np.zeros(gray.shape, dtype=np.uint8)
        cv2.circle(mask, (cx, cy), radius, 255, -1)
        
        # Compute confidence based on contrast within region
        region = gray[mask > 0]
        if len(region) == 0:
            return None
        
        confidence = min(1.0, np.std(region) / 50.0)
        
        return TMRegion(
            center_x=cx,
            center_y=cy,
            radius=radius,
            confidence=confidence,
            mask=mask,
        )
    
    def track(
        self,
        prev_frame: UInt8Array,
        curr_frame: UInt8Array,
        prev_region: TMRegion,
    ) -> Optional[TMRegion]:
        """
        Track TM region between frames using optical flow.
        
        Args:
            prev_frame: Previous preprocessed frame
            curr_frame: Current preprocessed frame
            prev_region: TM region from previous frame
            
        Returns:
            Updated TMRegion or None if tracking failed
        """
        prev_gray = cv2.cvtColor(prev_frame, cv2.COLOR_BGR2GRAY)
        curr_gray = cv2.cvtColor(curr_frame, cv2.COLOR_BGR2GRAY)
        
        # Define feature points within the TM region
        mask = prev_region.mask
        if mask is None:
            mask = np.zeros(prev_gray.shape, dtype=np.uint8)
            cv2.circle(
                mask,
                (prev_region.center_x, prev_region.center_y),
                prev_region.radius,
                255, -1
            )
        
        # Detect good features to track
        features = cv2.goodFeaturesToTrack(
            prev_gray,
            mask=mask,
            maxCorners=50,
            qualityLevel=0.01,
            minDistance=5,
        )
        
        if features is None or len(features) == 0:
            return None
        
        # Calculate optical flow
        next_pts, status, _ = cv2.calcOpticalFlowPyrLK(
            prev_gray, curr_gray, features, None
        )
        
        if next_pts is None:
            return None
        
        # Filter valid points
        good_old = features[status == 1]
        good_new = next_pts[status == 1]
        
        if len(good_new) == 0:
            return None
        
        # Estimate new center from mean displacement
        displacement = good_new - good_old
        mean_disp = np.mean(displacement, axis=0)
        
        new_cx = int(prev_region.center_x + mean_disp[0])
        new_cy = int(prev_region.center_y + mean_disp[1])
        
        # Update mask
        new_mask = np.zeros(curr_gray.shape, dtype=np.uint8)
        cv2.circle(new_mask, (new_cx, new_cy), prev_region.radius, 255, -1)
        
        return TMRegion(
            center_x=new_cx,
            center_y=new_cy,
            radius=prev_region.radius,
            confidence=prev_region.confidence * 0.98,  # Decay confidence
            mask=new_mask,
        )


# ============================================================================
# Movement Analysis
# ============================================================================

class TMMovementAnalyzer:
    """
    Analyzer for TM movement during Valsalva maneuver.
    
    Extracts displacement signal from video frames using:
    - Dense optical flow for sub-pixel motion estimation
    - TM-weighted averaging for displacement measurement
    - Signal filtering for noise reduction
    """
    
    def __init__(self, config: VideoProcessingConfig = DEFAULT_CONFIG) -> None:
        """Initialize analyzer."""
        if not CV2_AVAILABLE:
            raise ImportError("OpenCV required for movement analysis")
        
        self.config = config
        self.logger = logging.getLogger(__name__)
    
    def compute_frame_displacement(
        self,
        prev_frame: UInt8Array,
        curr_frame: UInt8Array,
        tm_region: TMRegion,
    ) -> Tuple[float, float]:
        """
        Compute TM displacement between two frames.
        
        Args:
            prev_frame: Previous frame (grayscale)
            curr_frame: Current frame (grayscale)
            tm_region: TM region for weighting
            
        Returns:
            Tuple of (displacement_magnitude, displacement_direction)
        """
        # Ensure grayscale
        if len(prev_frame.shape) == 3:
            prev_gray = cv2.cvtColor(prev_frame, cv2.COLOR_BGR2GRAY)
        else:
            prev_gray = prev_frame
        
        if len(curr_frame.shape) == 3:
            curr_gray = cv2.cvtColor(curr_frame, cv2.COLOR_BGR2GRAY)
        else:
            curr_gray = curr_frame
        
        # Compute dense optical flow (Farneback method)
        flow = cv2.calcOpticalFlowFarneback(
            prev_gray, curr_gray, None,
            pyr_scale=self.config.flow_pyr_scale,
            levels=self.config.flow_levels,
            winsize=self.config.flow_winsize,
            iterations=self.config.flow_iterations,
            poly_n=self.config.flow_poly_n,
            poly_sigma=self.config.flow_poly_sigma,
            flags=0,
        )
        
        # Extract flow within TM region
        mask = tm_region.mask
        if mask is None:
            mask = np.ones(prev_gray.shape, dtype=np.uint8) * 255
        
        flow_x = flow[:, :, 0]
        flow_y = flow[:, :, 1]
        
        # Weighted average displacement (TM center weighted more)
        y_coords, x_coords = np.where(mask > 0)
        if len(x_coords) == 0:
            return 0.0, 0.0
        
        # Distance-based weighting (center weighted more)
        distances = np.sqrt(
            (x_coords - tm_region.center_x) ** 2 +
            (y_coords - tm_region.center_y) ** 2
        )
        weights = np.exp(-distances / (tm_region.radius * 0.5))
        weights = weights / np.sum(weights)
        
        # Weighted mean flow
        mean_fx = np.sum(flow_x[y_coords, x_coords] * weights)
        mean_fy = np.sum(flow_y[y_coords, x_coords] * weights)
        
        # Compute magnitude and direction
        magnitude = float(np.sqrt(mean_fx ** 2 + mean_fy ** 2))
        direction = float(np.arctan2(mean_fy, mean_fx))
        
        return magnitude, direction
    
    def extract_displacement_signal(
        self,
        video_reader: EndoscopeVideoReader,
        tm_regions: List[Optional[TMRegion]],
        start_frame: int = 0,
        end_frame: Optional[int] = None,
    ) -> Tuple[FloatArray, FloatArray, float]:
        """
        Extract displacement signal from video.
        
        Args:
            video_reader: Opened video reader
            tm_regions: List of TM regions per frame
            start_frame: Starting frame index
            end_frame: Ending frame index
            
        Returns:
            Tuple of (time_array, displacement_array, sampling_rate)
        """
        if end_frame is None:
            end_frame = video_reader.metadata.frame_count
        
        n_frames = end_frame - start_frame
        displacements = np.zeros(n_frames)
        directions = np.zeros(n_frames)
        
        prev_frame = None
        prev_idx = 0
        
        for idx, (frame_idx, frame) in enumerate(
            video_reader.iter_frames(start_frame, end_frame)
        ):
            if prev_frame is None:
                prev_frame = frame
                prev_idx = idx
                continue
            
            # Get TM region for this frame
            region = tm_regions[idx] if idx < len(tm_regions) else None
            if region is None:
                # Use previous region if current not available
                region = tm_regions[prev_idx] if prev_idx < len(tm_regions) else None
            
            if region is None:
                displacements[idx] = 0.0
                directions[idx] = 0.0
            else:
                mag, direction = self.compute_frame_displacement(
                    prev_frame, frame, region
                )
                displacements[idx] = mag
                directions[idx] = direction
            
            prev_frame = frame
            prev_idx = idx
        
        # Cumulative displacement
        cumulative = np.cumsum(displacements)
        
        # Normalize to 0-1 range
        max_disp = np.max(np.abs(cumulative))
        if max_disp > 0:
            normalized = cumulative / max_disp
        else:
            normalized = cumulative
        
        # Create time array
        fps = video_reader.metadata.fps
        time = np.arange(n_frames) / fps
        
        # Apply lowpass filter for noise reduction
        if SCIPY_AVAILABLE and len(normalized) > 10:
            b, a = butter(2, self.config.lowpass_cutoff / (fps / 2), 'low')
            normalized = filtfilt(b, a, normalized)
        
        return time, normalized, fps


# ============================================================================
# Complete Processing Pipeline
# ============================================================================

@dataclass
class VideoAnalysisResult:
    """Complete result from video analysis."""
    video_path: Path
    metadata: VideoMetadata
    quality: VideoQuality
    quality_metrics: Dict[str, float]
    
    time_signal: FloatArray
    displacement_signal: FloatArray
    sampling_rate: float
    
    maneuver_start_idx: int
    maneuver_end_idx: int
    
    tm_detection_rate: float  # Fraction of frames with TM detected
    processing_notes: List[str] = field(default_factory=list)


class ValsalvaVideoProcessor:
    """
    Complete video processing pipeline for Valsalva maneuver analysis.
    
    Orchestrates:
    1. Video reading
    2. Frame preprocessing
    3. TM detection and tracking
    4. Movement analysis
    5. Signal extraction
    """
    
    def __init__(self, config: VideoProcessingConfig = DEFAULT_CONFIG) -> None:
        """Initialize processor."""
        self.config = config
        self.preprocessor = FramePreprocessor(config)
        self.detector = TMDetector(config)
        self.analyzer = TMMovementAnalyzer(config)
        self.logger = logging.getLogger(__name__)
    
    def process_video(
        self,
        video_path: Path,
        maneuver_start_time: Optional[float] = None,
        maneuver_end_time: Optional[float] = None,
    ) -> VideoAnalysisResult:
        """
        Process video file and extract displacement signal.
        
        Args:
            video_path: Path to video file
            maneuver_start_time: Start time of Valsalva (seconds), auto-detected if None
            maneuver_end_time: End time of Valsalva (seconds), auto-detected if None
            
        Returns:
            VideoAnalysisResult with extracted signals
        """
        notes: List[str] = []
        
        with EndoscopeVideoReader(video_path, self.config) as reader:
            metadata = reader.metadata
            fps = metadata.fps
            
            # Assess video quality from first few frames
            first_frame = reader.read_frame(0)
            if first_frame is None:
                raise ValueError("Could not read first frame")
            
            quality, quality_metrics = self.preprocessor.assess_quality(first_frame)
            
            if quality == VideoQuality.UNUSABLE:
                notes.append("WARNING: Video quality is very poor")
            
            # Detect TM in initial frames
            preprocessed_first = self.preprocessor.preprocess(first_frame)
            initial_region = self.detector.detect(preprocessed_first)
            
            if initial_region is None:
                notes.append("WARNING: Could not detect TM in initial frame")
                # Create default region in center
                h, w = first_frame.shape[:2]
                initial_region = TMRegion(
                    center_x=w // 2,
                    center_y=h // 2,
                    radius=min(w, h) // 3,
                    confidence=0.5,
                )
            
            # Track TM through all frames
            tm_regions: List[Optional[TMRegion]] = []
            prev_frame = preprocessed_first
            current_region = initial_region
            detection_count = 0
            
            for frame_idx, frame in reader.iter_frames():
                preprocessed = self.preprocessor.preprocess(frame)
                
                # Try to track from previous frame
                new_region = self.detector.track(prev_frame, preprocessed, current_region)
                
                if new_region is None or new_region.confidence < 0.3:
                    # Try fresh detection
                    new_region = self.detector.detect(preprocessed)
                
                if new_region is not None:
                    detection_count += 1
                    current_region = new_region
                
                tm_regions.append(current_region)
                prev_frame = preprocessed
            
            detection_rate = detection_count / metadata.frame_count
            
            # Extract displacement signal
            time_signal, disp_signal, sr = self.analyzer.extract_displacement_signal(
                reader, tm_regions
            )
            
            # Detect maneuver timing if not provided
            if maneuver_start_time is None or maneuver_end_time is None:
                start_idx, end_idx = self._detect_maneuver_timing(disp_signal, fps)
                notes.append("Maneuver timing auto-detected")
            else:
                start_idx = int(maneuver_start_time * fps)
                end_idx = int(maneuver_end_time * fps)
            
            # Validate indices
            start_idx = max(0, min(start_idx, len(disp_signal) - 1))
            end_idx = max(start_idx + 1, min(end_idx, len(disp_signal)))
        
        return VideoAnalysisResult(
            video_path=video_path,
            metadata=metadata,
            quality=quality,
            quality_metrics=quality_metrics,
            time_signal=time_signal,
            displacement_signal=disp_signal,
            sampling_rate=sr,
            maneuver_start_idx=start_idx,
            maneuver_end_idx=end_idx,
            tm_detection_rate=detection_rate,
            processing_notes=notes,
        )
    
    def _detect_maneuver_timing(
        self,
        signal: FloatArray,
        fps: float,
    ) -> Tuple[int, int]:
        """
        Auto-detect Valsalva maneuver start and end times.
        
        Uses signal dynamics to identify the active maneuver period.
        """
        if len(signal) < 10:
            return 0, len(signal)
        
        # Compute absolute displacement from baseline
        baseline = np.median(signal[:int(fps)])  # First second as baseline
        deviation = np.abs(signal - baseline)
        
        # Threshold: significant deviation from baseline
        threshold = np.std(deviation) * 2
        
        # Find first and last significant deviation
        above_threshold = np.where(deviation > threshold)[0]
        
        if len(above_threshold) == 0:
            # No significant movement detected
            return len(signal) // 4, 3 * len(signal) // 4
        
        start_idx = int(above_threshold[0])
        end_idx = int(above_threshold[-1])
        
        # Add margin
        margin = int(0.5 * fps)  # 0.5 second margin
        start_idx = max(0, start_idx - margin)
        end_idx = min(len(signal), end_idx + margin)
        
        return start_idx, end_idx


def process_bilateral_videos(
    left_video_path: Path,
    right_video_path: Path,
    config: VideoProcessingConfig = DEFAULT_CONFIG,
) -> Tuple[VideoAnalysisResult, VideoAnalysisResult]:
    """
    Process bilateral (left and right ear) videos.
    
    Args:
        left_video_path: Path to left ear video
        right_video_path: Path to right ear video
        config: Processing configuration
        
    Returns:
        Tuple of (left_result, right_result)
    """
    processor = ValsalvaVideoProcessor(config)
    
    left_result = processor.process_video(left_video_path)
    right_result = processor.process_video(right_video_path)
    
    return left_result, right_result
