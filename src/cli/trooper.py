#!/usr/bin/env python3
"""Stormtrooper Voice Assistant CLI.

This module provides a command-line interface to the Stormtrooper voice system.
It supports two main commands:
- 'say': Convert text to Stormtrooper speech with various options
- 'process-quotes': Generate audio files from a YAML quotes configuration

Example Usage:
    Basic text-to-speech:
    $ trooper say 'Stop right there!'

    Combat alert with maximum volume:
    $ trooper say -v 11 --urgency high --context combat 'Enemy spotted!'

    Process all quotes:
    $ trooper process-quotes

    Regenerate all quotes:
    $ trooper process-quotes --clean
"""

import argparse
import os
import sys
from pathlib import Path
from typing import Any, Dict, Tuple, cast

import numpy as np
import soundfile as sf
from loguru import logger

# Add project root to Python path
project_root = Path(__file__).parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.append(str(project_root))

from audio import AudioError
from audio.effects import StormtrooperEffect
from audio.polly import PollyClient
from audio.processor import process_and_play_text
from quotes import QuoteManager
from src.openai import get_stormtrooper_response
from src.openai.conversation import clear_history, load_history, save_history

# Type alias for sounddevice device info
DeviceInfo = Dict[str, Any]

# Store conversation context
_last_user_input = None
_last_response = None

def setup_directories(clean: bool = False) -> Tuple[Path, Path]:
    """Create and verify required directories exist.
    
    This function ensures the necessary directories for audio file storage
    exist and optionally cleans them by removing existing files.
    
    Args:
        clean: If True, delete all existing files in the directories
    
    Returns:
        Tuple of (polly_raw_dir, processed_dir) paths
        
    Example:
        >>> # Create directories without cleaning
        >>> raw_dir, proc_dir = setup_directories()
        
        >>> # Clean existing files and recreate directories
        >>> raw_dir, proc_dir = setup_directories(clean=True)
    """
    polly_raw_dir = project_root / "assets" / "audio" / "polly_raw"
    processed_dir = project_root / "assets" / "audio" / "processed"
    
    # Clean existing files if requested
    if clean:
        if polly_raw_dir.exists():
            logger.info("Cleaning polly_raw directory...")
            for file in polly_raw_dir.glob("*.wav"):
                file.unlink()
        if processed_dir.exists():
            logger.info("Cleaning processed directory...")
            for file in processed_dir.glob("*.wav"):
                file.unlink()
    
    polly_raw_dir.mkdir(parents=True, exist_ok=True)
    processed_dir.mkdir(parents=True, exist_ok=True)
    
    return polly_raw_dir, processed_dir

def handle_process_quotes(args: argparse.Namespace) -> int:
    """Handle the 'process-quotes' command.
    
    This function processes all quotes from a YAML configuration file,
    generating both raw and processed audio files. It supports:
    - Loading quotes from YAML configuration
    - Generating TTS audio using Amazon Polly
    - Applying Stormtrooper effects
    - Caching processed files
    - Cleaning and regenerating files
    
    Args:
        args: Parsed command line arguments containing:
            - quotes_file: Optional path to quotes YAML file
            - clean: Whether to clean existing files
        
    Returns:
        Exit code (0 for success, non-zero for error)
        
    Example:
        >>> # Process quotes with default settings
        >>> args = parser.parse_args(['process-quotes'])
        >>> handle_process_quotes(args)
        0
        
        >>> # Clean and regenerate all quotes
        >>> args = parser.parse_args(['process-quotes', '--clean'])
        >>> handle_process_quotes(args)
        0
    """
    try:
        # Setup
        quotes_file = args.quotes_file or (project_root / "config" / "quotes.yaml")
        polly_raw_dir, processed_dir = setup_directories(args.clean)
        
        # Initialize components
        quote_manager = QuoteManager(quotes_file)
        polly = PollyClient()
        effect = StormtrooperEffect()
        
        total_quotes = len(quote_manager.quotes)
        generated = 0
        skipped = 0
        failed = 0
        
        logger.info(f"Processing {total_quotes} quotes...")
        
        # Process each quote
        for quote in quote_manager.quotes:
            try:
                # Generate filename base (without extension)
                clean_text = "_".join(quote.text.split()[:3]).lower()
                clean_text = "".join(c for c in clean_text if c.isalnum() or c == "_")
                
                base_name = f"Matthew_neural_{quote.category.value}_{quote.context}_{clean_text}"
                raw_path = polly_raw_dir / f"{base_name}.wav"
                processed_path = processed_dir / f"{base_name}_processed.wav"
                
                # Skip if processed file exists and is newer than raw file
                if processed_path.exists():
                    if not raw_path.exists() or processed_path.stat().st_mtime > raw_path.stat().st_mtime:
                        logger.debug(f"Skipping {base_name} - already processed")
                        skipped += 1
                        continue
                
                # Generate raw audio if needed
                if not raw_path.exists():
                    logger.info(f"Generating audio for: {quote.text}")
                    pcm_data = polly.generate_speech(
                        text=quote.text,
                        urgency=quote.urgency.value,
                        context=quote.context
                    )
                    
                    # Convert PCM bytes to float32 array
                    if not isinstance(pcm_data, bytes):
                        raise AudioError("Expected bytes from Polly TTS")
                    audio_data = np.frombuffer(pcm_data, dtype=np.int16)
                    audio_float = audio_data.astype(np.float32) / 32768.0
                    
                    # Save as WAV
                    sf.write(str(raw_path), audio_float, 16000, format='WAV', subtype='FLOAT')
                
                # Apply effects
                logger.info(f"Applying effects to: {raw_path.name}")
                effect.process_file(
                    str(raw_path),
                    str(processed_path),
                    urgency=quote.urgency
                )
                
                generated += 1
                
            except Exception as e:
                logger.error(f"Failed to process quote: {quote.text}")
                logger.error(f"Error: {str(e)}")
                failed += 1
                continue
        
        # Summary
        logger.info("\nProcessing complete:")
        logger.info(f"Total quotes: {total_quotes}")
        logger.info(f"Generated: {generated}")
        logger.info(f"Skipped: {skipped}")
        logger.info(f"Failed: {failed}")
        
        return 0 if failed == 0 else 1
        
    except Exception as e:
        logger.error(f"Failed to process quotes: {str(e)}")
        return 2

def handle_list_devices(args: argparse.Namespace) -> int:
    """Handle the 'devices' command.
    
    Lists all available audio output devices and their capabilities.
    
    Args:
        args: Parsed command line arguments (unused)
        
    Returns:
        Exit code (0 for success, non-zero for error)
    """
    try:
        import sounddevice as sd
        devices = sd.query_devices()
        
        print("\nAvailable Audio Devices:")
        print("------------------------")
        for i, device in enumerate(devices):
            device_info = cast(DeviceInfo, device)
            if device_info.get('max_output_channels', 0) > 0:  # Only show output devices
                print(f"\nDevice ID: {i}")
                print(f"Name: {device_info.get('name', 'Unknown')}")
                print(f"Sample Rates: {device_info.get('default_samplerate', 0)} Hz")
                print(f"Channels: {device_info.get('max_output_channels', 0)}")
                if i == sd.default.device[1]:
                    print("(Default Output Device)")
        return 0
        
    except Exception as e:
        logger.error(f"Failed to list audio devices: {str(e)}")
        return 1

def handle_config(args: argparse.Namespace) -> int:
    """Handle the 'config' command.
    
    This function manages the configuration settings for the tool.
    It can:
    - Set audio device
    - Show current configuration
    - Initialize a new .env file
    
    Args:
        args: Parsed command line arguments containing:
            - action: The config action to perform (device, show, init)
            - device_id: Optional device ID when action is 'device'
            
    Returns:
        Exit code (0 for success, non-zero for error)
    """
    try:
        from dotenv import find_dotenv, load_dotenv, set_key

        # Find or create .env file
        env_file = find_dotenv()
        if not env_file:
            env_file = str(project_root / ".env")
            with open(env_file, "w", encoding='utf-8') as f:
                f.write("# Trooper CLI Configuration\n")
        
        # Load current configuration
        load_dotenv(env_file)
        
        if args.action == "device":
            if args.device_id is None:
                logger.error("Device ID is required for 'device' action")
                return 1
                
            # Verify device exists
            import sounddevice as sd
            try:
                device_info = cast(DeviceInfo, sd.query_devices(args.device_id))
                if device_info.get('max_output_channels', 0) > 0:
                    # Set the device ID in .env
                    set_key(env_file, "TROOPER_AUDIO_DEVICE", str(args.device_id))
                    print(f"Audio device set to: {device_info.get('name', 'Unknown')}")
                    return 0
                else:
                    logger.error(f"Device {args.device_id} is not an output device")
                    return 1
            except Exception as e:
                logger.error(f"Invalid device ID {args.device_id}: {str(e)}")
                return 1
                
        elif args.action == "show":
            # Show current configuration
            print("\nCurrent Configuration:")
            print("---------------------")
            if os.environ.get("TROOPER_AUDIO_DEVICE"):
                try:
                    import sounddevice as sd
                    device_id = int(os.environ["TROOPER_AUDIO_DEVICE"])
                    device_info = cast(DeviceInfo, sd.query_devices(device_id))
                    print(f"Audio Device: {device_info.get('name', 'Unknown')} (ID: {device_id})")
                except Exception:
                    print(f"Audio Device: {os.environ['TROOPER_AUDIO_DEVICE']} (Invalid)")
            else:
                print("Audio Device: Not configured (using system default)")
                
            print(f"AWS Profile: {os.environ.get('AWS_PROFILE', 'Not configured')}")
            print(f"AWS Region: {os.environ.get('AWS_DEFAULT_REGION', 'Not configured')}")
            return 0
            
        elif args.action == "init":
            # Create new .env with defaults
            defaults = {
                "TROOPER_AUDIO_DEVICE": "",  # Empty means use system default
                "AWS_PROFILE": "trooper",
                "AWS_DEFAULT_REGION": "us-east-1"
            }
            
            for key, value in defaults.items():
                if not os.environ.get(key):
                    set_key(env_file, key, value)
                    
            print(f"Created configuration file: {env_file}")
            return 0
            
        return 1
        
    except Exception as e:
        logger.error(f"Configuration error: {str(e)}")
        return 2

def handle_update(args: argparse.Namespace) -> int:
    """Handle the 'update' command.
    
    This function manages software updates from GitHub.
    It can:
    - Check for available updates
    - Pull and install updates
    - Show update status
    
    Args:
        args: Parsed command line arguments containing:
            - action: The update action to perform (check, pull, status)
            
    Returns:
        Exit code (0 for success, non-zero for error)
    """
    try:
        import subprocess
        from datetime import datetime

        import pkg_resources
        
        def get_git_info() -> tuple[str, str]:
            """Get current git branch and commit."""
            try:
                branch = subprocess.check_output(
                    ["git", "rev-parse", "--abbrev-ref", "HEAD"],
                    cwd=str(project_root)
                ).decode().strip()
                
                commit = subprocess.check_output(
                    ["git", "rev-parse", "--short", "HEAD"],
                    cwd=str(project_root)
                ).decode().strip()
                
                return branch, commit
            except subprocess.CalledProcessError:
                return "unknown", "unknown"
        
        def get_remote_info() -> tuple[str, str, bool]:
            """Get remote branch info and check if updates available."""
            try:
                # Fetch latest without merging
                subprocess.run(
                    ["git", "fetch", "origin", "main"],
                    cwd=str(project_root),
                    check=True,
                    capture_output=True
                )
                
                # Get latest remote commit
                remote_commit = subprocess.check_output(
                    ["git", "rev-parse", "--short", "origin/main"],
                    cwd=str(project_root)
                ).decode().strip()
                
                # Get commit count difference
                diff_count = subprocess.check_output(
                    ["git", "rev-list", "--count", "HEAD..origin/main"],
                    cwd=str(project_root)
                ).decode().strip()
                
                return "main", remote_commit, int(diff_count) > 0
                
            except subprocess.CalledProcessError as e:
                logger.error(f"Failed to get remote info: {e}")
                return "unknown", "unknown", False
        
        # Get current version and git info
        version = pkg_resources.get_distribution("trooper").version
        branch, commit = get_git_info()
        
        if args.action == "check":
            # Check for updates
            remote_branch, remote_commit, has_updates = get_remote_info()
            
            print("\nUpdate Status:")
            print("-------------")
            print(f"Current Version: {version}")
            print(f"Local Branch: {branch} ({commit})")
            print(f"Remote Branch: {remote_branch} ({remote_commit})")
            
            if has_updates:
                print("\nUpdates are available!")
                print("Run 'trooper update pull' to install updates")
            else:
                print("\nYou are up to date!")
            
            return 0
            
        elif args.action == "pull":
            # Pull and install updates
            print("\nChecking for updates...")
            remote_branch, remote_commit, has_updates = get_remote_info()
            
            if not has_updates:
                print("Already up to date!")
                return 0
            
            print("\nPulling updates...")
            try:
                # Pull latest changes
                subprocess.run(
                    ["git", "pull", "origin", "main"],
                    cwd=str(project_root),
                    check=True
                )
                
                print("\nReinstalling package...")
                # Reinstall package
                subprocess.run(
                    ["pip", "install", "-e", "."],
                    cwd=str(project_root),
                    check=True
                )
                
                print("\nUpdate complete!")
                print("Please restart any running instances of trooper")
                return 0
                
            except subprocess.CalledProcessError as e:
                logger.error(f"Update failed: {e}")
                return 1
            
        elif args.action == "status":
            # Show current status
            last_commit_date = subprocess.check_output(
                ["git", "log", "-1", "--format=%cd", "--date=local"],
                cwd=str(project_root)
            ).decode().strip()
            
            print("\nInstallation Status:")
            print("------------------")
            print(f"Version: {version}")
            print(f"Branch: {branch}")
            print(f"Commit: {commit}")
            print(f"Last Updated: {last_commit_date}")
            return 0
            
        return 1
        
    except Exception as e:
        logger.error(f"Update error: {str(e)}")
        return 2

def handle_ask(args: argparse.Namespace) -> int:
    """Handle the 'ask' command.
    
    This function processes user input through the AI pipeline and speaks the response:
    1. Sends user input to OpenAI for Stormtrooper response
    2. Processes the response through TTS pipeline
    3. Plays the processed audio
    
    Args:
        args: Parsed command line arguments containing:
            - text: The user's question/input
            - cliff_clavin_mode: Whether to enable Cliff Clavin mode
            - volume: Optional volume level (1-11)
            - urgency: Voice urgency level
            - context: Voice context
            - reset: Whether to clear conversation history
            - debug: Whether to show debug information
            
    Returns:
        Exit code (0 for success, non-zero for error)
    """
    try:
        # Clear history if requested
        if args.reset:
            clear_history()
            if args.debug:
                logger.info("Conversation history cleared")
        
        # Load conversation history
        previous_input, previous_response = load_history()
        if args.debug and (previous_input or previous_response):
            logger.info("Using conversation history:")
            logger.info(f"Previous input: {previous_input}")
            logger.info(f"Previous response: {previous_response}")
        
        # Get AI response with context
        response, new_user_input, new_response = get_stormtrooper_response(
            args.text,
            cliff_clavin_mode=args.cliff_clavin_mode,
            previous_user_input=previous_input,
            previous_response=previous_response
        )
        
        # Save the new context
        save_history(new_user_input, new_response)
        
        # Process and play the response
        process_and_play_text(
            text=response,
            urgency=args.urgency,
            context=args.context,
            volume=args.volume
        )
        
        return 0
        
    except Exception as e:
        logger.error(f"Failed to process ask command: {str(e)}")
        return 1

def create_parser() -> argparse.ArgumentParser:
    """Create argument parser for CLI.
    
    This function sets up the command-line interface with two main commands:
    - 'say': Convert text to Stormtrooper speech
    - 'process-quotes': Process quotes from YAML configuration
    
    Each command has its own set of options and help text.
    
    Returns:
        Configured argument parser
        
    Example:
        >>> parser = create_parser()
        >>> args = parser.parse_args(['say', 'Stop right there!'])
        >>> args.command
        'say'
        >>> args.text
        'Stop right there!'
    """
    parser = argparse.ArgumentParser(
        description="Stormtrooper Voice Assistant",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic usage (use single quotes around text):
  trooper say 'Stop right there!'
  
  # With volume (1-11):
  trooper say -v 11 'Intruder alert!'
  
  # Full options:
  trooper say --volume 11 --urgency high --context combat 'Enemy spotted!'
  
  # Generate without playing:
  trooper say --no-play --keep 'All clear'
  
  # List available audio devices:
  trooper devices
  
  # Configure audio device:
  trooper config device 1
  
  # Show current configuration:
  trooper config show
  
  # Initialize configuration:
  trooper config init
  
  # Check for updates:
  trooper update check
  
  # Install updates:
  trooper update pull
  
  # Show update status:
  trooper update status
  
  # Process quotes from YAML:
  trooper process-quotes
  
  # Process quotes with custom config:
  trooper process-quotes --quotes-file custom_quotes.yaml --clean
  
Note: If your text contains special characters, wrap it in single quotes (')
      For Windows users, use double quotes (") instead.
"""
    )
    
    # Add subcommands
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # 'say' command
    say_parser = subparsers.add_parser(
        "say",
        help="Convert text to Stormtrooper speech",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    say_parser.add_argument(
        "text",
        help="Text to convert to speech (wrap in quotes if it contains spaces)"
    )
    
    say_parser.add_argument(
        "-v", "--volume",
        type=float,
        choices=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11],
        help="Volume level (1-11, default: 5)"
    )
    
    say_parser.add_argument(
        "-u", "--urgency",
        choices=["low", "normal", "medium", "high"],
        default="normal",
        help="Voice urgency level (default: normal, 'normal' and 'medium' are equivalent)"
    )
    
    say_parser.add_argument(
        "-c", "--context",
        choices=["general", "combat", "alert", "patrol"],
        default="general",
        help="Voice context (default: general)"
    )
    
    say_parser.add_argument(
        "--no-play",
        action="store_true",
        help="Generate audio without playing"
    )
    
    say_parser.add_argument(
        "--keep",
        action="store_true",
        help="Keep generated audio files"
    )
    
    # 'process-quotes' command
    process_quotes_parser = subparsers.add_parser(
        "process-quotes",
        help="Process quotes from YAML file into audio files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description="Generate processed audio files for all quotes in the YAML file."
    )
    
    process_quotes_parser.add_argument(
        "--quotes-file",
        type=Path,
        help="Path to quotes YAML file (default: config/quotes.yaml)"
    )
    
    process_quotes_parser.add_argument(
        "--clean",
        action="store_true",
        help="Delete existing files before processing"
    )
    
    # 'devices' command
    subparsers.add_parser(
        "devices",
        help="List available audio output devices",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    # 'config' command
    config_parser = subparsers.add_parser(
        "config",
        help="Configure tool settings",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    config_subparsers = config_parser.add_subparsers(
        dest="action",
        help="Configuration action to perform"
    )
    
    # 'config device' command
    device_parser = config_subparsers.add_parser(
        "device",
        help="Set audio output device"
    )
    device_parser.add_argument(
        "device_id",
        type=int,
        help="Device ID (from 'trooper devices' output)"
    )
    
    # 'config show' command
    config_subparsers.add_parser(
        "show",
        help="Show current configuration"
    )
    
    # 'config init' command
    config_subparsers.add_parser(
        "init",
        help="Create new configuration file with defaults"
    )

    # 'update' command
    update_parser = subparsers.add_parser(
        "update",
        help="Manage software updates",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    update_subparsers = update_parser.add_subparsers(
        dest="action",
        help="Update action to perform"
    )
    
    # 'update check' command
    update_subparsers.add_parser(
        "check",
        help="Check for available updates"
    )
    
    # 'update pull' command
    update_subparsers.add_parser(
        "pull",
        help="Pull and install updates"
    )
    
    # 'update status' command
    update_subparsers.add_parser(
        "status",
        help="Show current version and update status"
    )

    # 'ask' command
    ask_parser = subparsers.add_parser(
        "ask",
        help="Process user input through AI pipeline",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    ask_parser.add_argument(
        "text",
        help="The user's question/input"
    )
    
    ask_parser.add_argument(
        "--cliff-clavin-mode",
        action="store_true",
        help="Enable Cliff Clavin mode"
    )
    
    ask_parser.add_argument(
        "-v", "--volume",
        type=float,
        choices=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11],
        help="Volume level (1-11, default: 5)"
    )
    
    ask_parser.add_argument(
        "-u", "--urgency",
        choices=["low", "normal", "medium", "high"],
        default="normal",
        help="Voice urgency level (default: normal, 'normal' and 'medium' are equivalent)"
    )
    
    ask_parser.add_argument(
        "-c", "--context",
        choices=["general", "combat", "alert", "patrol"],
        default="general",
        help="Voice context (default: general)"
    )

    ask_parser.add_argument(
        "--reset",
        action="store_true",
        help="Clear conversation history before processing"
    )

    ask_parser.add_argument(
        "--debug",
        action="store_true",
        help="Show debug information about conversation history"
    )

    return parser

def handle_say(args: argparse.Namespace) -> int:
    """Handle the 'say' command.
    
    This function processes a single text input through the TTS pipeline
    with optional volume, urgency, and context settings.
    
    Args:
        args: Parsed command line arguments containing:
            - text: Text to convert to speech
            - volume: Optional volume level (1-11)
            - urgency: Voice urgency level
            - context: Voice context
            - no_play: Whether to skip playback
            - keep: Whether to keep generated files
        
    Returns:
        Exit code (0 for success, non-zero for error)
        
    Example:
        >>> # Basic usage
        >>> args = parser.parse_args(['say', 'Test'])
        >>> handle_say(args)
        0
        
        >>> # With options
        >>> args = parser.parse_args([
        ...     'say',
        ...     '--volume', '11',
        ...     '--urgency', 'high',
        ...     'Alert!'
        ... ])
        >>> handle_say(args)
        0
    """
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

def main() -> int:
    """Run the CLI application.
    
    This function is the entry point for the CLI application.
    It parses command-line arguments and routes to the appropriate
    handler function.
    
    Returns:
        Exit code (0 for success, non-zero for error)
        
    Example:
        >>> # Show help
        >>> sys.argv = ['trooper', '--help']
        >>> main()
        0
        
        >>> # Basic TTS
        >>> sys.argv = ['trooper', 'say', 'Test']
        >>> main()
    """
    parser = create_parser()
    
    try:
        args = parser.parse_args()
    except Exception as e:
        logger.error("Error parsing arguments. Make sure to wrap text in quotes!")
        logger.error("Example: trooper say 'Stop right there!'")
        return 1
    
    if not args.command:
        parser.print_help()
        return 0
        
    if args.command == "say":
        return handle_say(args)
    elif args.command == "process-quotes":
        return handle_process_quotes(args)
    elif args.command == "devices":
        return handle_list_devices(args)
    elif args.command == "config":
        return handle_config(args)
    elif args.command == "update":
        return handle_update(args)
    elif args.command == "ask":
        return handle_ask(args)
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 