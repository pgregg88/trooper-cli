"""Audio file path management utilities."""

import os
from pathlib import Path
from typing import Optional, Tuple

from loguru import logger

from src.quotes.models import Quote


class AudioPathManager:
    """Manages audio file paths and directory structure."""
    
    def __init__(self, root_dir: Optional[Path] = None):
        """Initialize the audio path manager.
        
        Args:
            root_dir: Optional root directory for audio files.
                     Defaults to project_root/assets/audio
        """
        if root_dir is None:
            project_root = Path(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
            root_dir = project_root / "assets" / "audio"
            
        self.root_dir = root_dir
        self.raw_dir = root_dir / "polly_raw"
        self.processed_dir = root_dir / "processed"
        self.temp_dir = root_dir / "temp"
    
    def ensure_directories(self) -> None:
        """Create required directories if they don't exist."""
        self.raw_dir.mkdir(parents=True, exist_ok=True)
        self.processed_dir.mkdir(parents=True, exist_ok=True)
        self.temp_dir.mkdir(parents=True, exist_ok=True)
    
    def get_base_name(self, quote: Quote) -> str:
        """Generate consistent base filename for a quote.
        
        Args:
            quote: Quote to generate filename for
            
        Returns:
            Base filename without extension
        """
        # Clean text for filename
        clean_text = "_".join(quote.text.split()[:3]).lower()
        clean_text = "".join(c for c in clean_text if c.isalnum() or c == "_")
        
        return f"Matthew_neural_{quote.category.value}_{quote.context}_{clean_text}"
    
    def get_paths(self, quote: Quote) -> Tuple[Path, Path]:
        """Get paths for raw and processed audio files.
        
        Args:
            quote: Quote to get paths for
            
        Returns:
            Tuple of (raw_path, processed_path)
        """
        base_name = self.get_base_name(quote)
        raw_path = self.raw_dir / f"{base_name}.wav"
        processed_path = self.processed_dir / f"{base_name}_processed.wav"
        
        return raw_path, processed_path
    
    def get_temp_path(self, quote: Quote) -> Path:
        """Get temporary file path for processing.
        
        Args:
            quote: Quote being processed
            
        Returns:
            Path to temporary file
        """
        base_name = self.get_base_name(quote)
        return self.temp_dir / f"{base_name}_temp_{os.getpid()}.wav"
    
    def cleanup_temp_files(self) -> None:
        """Clean up any temporary files."""
        if not self.temp_dir.exists():
            return
            
        try:
            for temp_file in self.temp_dir.glob("*_temp_*.wav"):
                try:
                    temp_file.unlink()
                except OSError as e:
                    logger.warning(f"Failed to delete temp file {temp_file}: {e}")
        except Exception as e:
            logger.error(f"Error cleaning temp files: {e}") 