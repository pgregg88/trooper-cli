#!/usr/bin/env python3
"""Stormtrooper Text-to-Speech CLI.

This script provides a command-line interface to the Stormtrooper TTS system.
"""

import sys
import argparse
from pathlib import Path
from typing import Optional
from loguru import logger

# Add project root to Python path
project_root = Path(__file__).parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.append(str(project_root))

from src.audio.processor import process_and_play_text
from src.audio import AudioError

def create_parser() -> argparse.ArgumentParser:
    """Create argument parser for CLI.
    
    Returns:
        Configured argument parser
    """
    parser = argparse.ArgumentParser(
        description="Convert text to Stormtrooper speech",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  speak "Stop right there!"
  speak -v 11 "Intruder alert!"
  speak --volume 11 --urgency high --context combat "Enemy spotted!"
  speak --no-play --keep "All clear"
"""
    )
    
    parser.add_argument(
        "text",
        help="Text to convert to speech"
    )
    
    parser.add_argument(
        "-v", "--volume",
        type=float,
        choices=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11],
        help="Volume level (1-11, default: 5)"
    )
    
    parser.add_argument(
        "-u", "--urgency",
        choices=["low", "normal", "high"],
        default="normal",
        help="Voice urgency level (default: normal)"
    )
    
    parser.add_argument(
        "-c", "--context",
        choices=["general", "combat", "alert", "patrol"],
        default="general",
        help="Voice context (default: general)"
    )
    
    parser.add_argument(
        "--no-play",
        action="store_true",
        help="Generate audio without playing"
    )
    
    parser.add_argument(
        "--keep",
        action="store_true",
        help="Keep generated audio files"
    )
    
    return parser

def main() -> int:
    """Run the CLI application.
    
    Returns:
        Exit code (0 for success, non-zero for error)
    """
    parser = create_parser()
    args = parser.parse_args()
    
    try:
        # Process text to speech
        output_path = process_and_play_text(
            text=args.text,
            urgency=args.urgency,
            context=args.context,
            play_immediately=not args.no_play,
            cleanup=not args.keep,
            volume=args.volume
        )
        
        # Print output path if keeping file
        if args.keep:
            print(f"\nAudio file saved to: {output_path}")
            
        return 0
        
    except AudioError as e:
        logger.error(f"Audio processing failed: {str(e)}")
        return 1
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return 2

if __name__ == "__main__":
    sys.exit(main()) 