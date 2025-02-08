# Trooper Voice Assistant

A command-line tool and web interface that converts text to speech with a Stormtrooper voice effect, manages pre-configured quotes, and provides an interactive AI chat experience.

## Features

Core Features:

- Text-to-speech using Amazon Polly's neural voices
- Stormtrooper voice effect processing with configurable parameters
- Interactive AI chat with context memory
- Web interface with real-time audio responses (Linux)
- Pre-configured quotes system with sequence playback
- Volume control (1-11) and voice urgency levels
- Automatic audio caching and management

Voice Customization:

- Multiple voice contexts (general, combat, alert, patrol)
- Urgency levels (low, normal, high)
- Context-aware responses
- Cliff Clavin mode for Star Wars trivia

System Integration:

- Command-line interface with extensive commands
- Systemd service integration (Linux)
- Configurable audio output
- Environment-based configuration
- Automatic updates

## System Requirements

### Operating System Support

- **Linux (Full Support)**
  - All features including web interface
  - Systemd service integration
  - Tested on Ubuntu, Debian, Fedora, RHEL
- **macOS (Partial Support)**
  - Core features and CLI
  - No web interface support
  - Audio compatibility may vary
- **Windows (Limited Support)**
  - Basic CLI functionality
  - Some features may not work
  - No web interface support

### Prerequisites

1. Python 3.11.2 or higher
2. pip (Python package installer)
3. pyenv (Python version manager)
4. AWS account with Polly access (neural voices enabled)
5. Audio output device
6. OpenAI API key (for chat functionality)
7. Git (for installation and updates)

## Quick Start

Get up and running with Trooper CLI in minutes:

```bash
# Clone the repository
git clone https://github.com/yourusername/trooper-cli.git
cd trooper-cli

# Set installation path (optional)
export TROOPER_INSTALL_PATH=$(pwd)  # Use current directory
# or
export TROOPER_INSTALL_PATH=/opt/trooper-cli  # Use custom path

# Install dependencies and CLI
chmod +x install.sh
./install.sh

# Configure environment
cp .env-example .env
# Edit .env with your AWS and OpenAI API credentials
nano .env

# Test the installation
trooper say "Reporting for duty!"

# Start interactive chat
trooper chat start

# Try the web interface (Linux only)
systemctl --user enable trooper-web.service
systemctl --user start trooper-web.service
# Visit http://localhost:5001 in your browser
```

See detailed sections below for complete setup and usage instructions.

## Installation

### System Dependencies

Install required system packages based on your OS:

#### Linux (Ubuntu/Debian)

```bash
sudo apt-get update
sudo apt-get install -y portaudio19-dev python3-pyaudio make build-essential \
    libssl-dev zlib1g-dev libbz2-dev libreadline-dev libsqlite3-dev wget \
    curl llvm libncursesw5-dev xz-utils tk-dev libxml2-dev libxmlsec1-dev \
    libffi-dev liblzma-dev
```

#### Linux (Fedora)

```bash
sudo dnf install portaudio-devel python3-pyaudio
```

#### Linux (CentOS/RHEL)

```bash
sudo yum install portaudio-devel python3-pyaudio
```

#### macOS

```bash
brew install portaudio
```

### Installation Path Configuration

The Trooper CLI supports configurable installation paths through the `TROOPER_INSTALL_PATH` environment variable:

```bash
# In your .env file
TROOPER_INSTALL_PATH=/opt/trooper-cli  # Custom installation directory
```

Default behavior:
- If not set: Uses the directory where the script is installed
- If set: Uses the specified path for all components (CLI, web interface, virtual environment)

This allows for flexible deployment in different environments while maintaining consistent paths across all components.

### Python Environment Setup

1. **Install pyenv** (if not already installed)

   macOS:

   ```bash
   brew install pyenv
   
   # Add to shell configuration
   echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.zshrc
   echo 'command -v pyenv >/dev/null || export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.zshrc
   echo 'eval "$(pyenv init -)"' >> ~/.zshrc
   source ~/.zshrc
   ```

   Linux:

   ```bash
   curl https://pyenv.run | bash
   
   # Add to shell configuration
   echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.bashrc
   echo 'command -v pyenv >/dev/null || export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.bashrc
   echo 'eval "$(pyenv init -)"' >> ~/.bashrc
   source ~/.bashrc
   ```

2. **Install Python and Create Environment**

   ```bash
   # Install Python 3.11.2
   pyenv install 3.11.2
   pyenv local 3.11.2
   
   # Create virtual environment
   python -m venv .venv
   
   # Activate environment
   source .venv/bin/activate  # Linux/macOS
   .venv\Scripts\activate     # Windows
   ```

### Package Installation

1. **Install Trooper CLI**

   ```bash
   # Install in development mode
   pip install -e .
   ```

2. **Verify Installation**

   ```bash
   which trooper  # Should point to .venv/bin/trooper
   trooper --help
   ```

### System Integration

1. **CLI Integration**
   The installation script creates a wrapper at `/usr/local/bin/trooper` that handles:
   - Virtual environment activation
   - Project path resolution
   - Command execution

2. **Web Interface (Linux Only)**

   ```bash
   # Enable and start the service
   systemctl --user enable trooper-web.service
   systemctl --user start trooper-web.service
   
   # Verify status
   systemctl --user status trooper-web.service
   ```

   The web interface:
   - Runs on <http://localhost:5001> by default
   - Starts automatically on login
   - Auto-restarts on crashes
   - Provides systemd logging

### Configuration

1. **Environment Setup**

   ```bash
   # Copy example configuration
   cp .env-example .env
   
   # Edit with your settings
   nano .env
   ```

   Key environment variables:
   - `TROOPER_INSTALL_PATH`: Installation directory
   - `TROOPER_WEB_PORT`: Web interface port (default: 5001)
   - `TROOPER_WEB_HOST`: Web interface host (default: 0.0.0.0)
   - `TROOPER_AUDIO_DEVICE`: Audio output device ID
   - `TROOPER_CLIFF_MODE`: Enable Cliff Clavin mode (0/1)
   - `AWS_PROFILE`: AWS credentials profile
   - `AWS_DEFAULT_REGION`: AWS region for Polly
   - `OPENAI_API_KEY`: OpenAI API key

2. **AWS Configuration**

   ```bash
   # Configure AWS CLI
   pip install awscli
   aws configure --profile trooper
   
   # Test configuration
   aws polly describe-voices --engine neural --profile trooper
   ```

3. **OpenAI Setup**

   ```bash
   # Add to .env file
   echo "OPENAI_API_KEY=your_api_key_here" >> .env
   
   # Test configuration
   trooper ask "Test message"
   ```

4. **Audio Configuration**

   ```bash
   # List available devices
   trooper devices
   
   # Set default device
   trooper config device <device_id>
   ```

### Troubleshooting Installation

1. **Permission Issues**

   ```bash
   # Fix script permissions
   chmod +x install.sh trooper.sh
   
   # Fix CLI wrapper permissions
   sudo chmod +x /usr/local/bin/trooper
   ```

2. **Virtual Environment Issues**

   ```bash
   # Recreate environment
   rm -rf .venv
   python -m venv .venv
   source .venv/bin/activate
   pip install -e .
   ```

3. **Web Service Issues (Linux)**

   ```bash
   # Check service status
   systemctl --user status trooper-web.service
   
   # View logs
   journalctl --user -u trooper-web.service
   ```

## Usage

### Command Reference

Trooper CLI provides several commands for different functionalities:

#### Core Commands

1. **say** - Convert text to Stormtrooper speech

   ```bash
   trooper say [options] "text"
   
   Options:
   -v, --volume     Volume level (1-11, default: 5)
   -u, --urgency    Voice urgency (low, normal, high)
   -c, --context    Voice context (general, combat, alert, patrol)
   --no-play        Generate audio without playing
   --keep           Keep generated audio files
   
   Examples:
   trooper say "Stop right there!"
   trooper say -v 11 --urgency high --context combat "Enemy spotted!"
   ```

2. **ask** - Get a single AI response

   ```bash
   trooper ask [options] "question"
   
   Options:
   --cliff-clavin-mode    Enable Star Wars trivia mode
   -v, --volume           Volume level (1-11)
   -u, --urgency          Voice urgency
   -c, --context          Voice context
   --reset                Clear conversation history
   --debug                Show debug information
   
   Examples:
   trooper ask "What's your designation?"
   trooper ask --cliff-clavin-mode "Tell me about TIE Fighters"
   ```

3. **chat** - Interactive conversation mode

   ```bash
   trooper chat [command] [options]
   
   Commands:
   start              Start chat session
   mode               Toggle Cliff Clavin mode
   
   Options:
   --cliff-mode       Start in Cliff Clavin mode
   -v, --verbose      Enable verbose logging
   
   Examples:
   trooper chat start
   trooper chat start --cliff-mode
   trooper chat mode
   ```

4. **sequence** - Play quote sequences

   ```bash
   trooper sequence [options]
   
   Options:
   -c, --category    Quote category
   --context         Quote context
   -n, --count       Number of quotes (default: 3)
   -v, --volume      Volume level (1-11)
   --tags            Filter quotes by tags
   
   Commands:
   play              Play a sequence (default)
   stop              Stop current sequence
   
   Examples:
   trooper sequence -c combat -n 3
   trooper sequence -c patrol --tags alert warning
   trooper sequence stop
   ```

#### System Commands

1. **devices** - List audio devices

   ```bash
   trooper devices
   ```

2. **config** - Manage configuration

   ```bash
   trooper config [command] [options]
   
   Commands:
   device [id]       Set audio output device
   show              Show current configuration
   init              Create new configuration file
   
   Examples:
   trooper config device 1
   trooper config show
   ```

3. **update** - Manage software updates

   ```bash
   trooper update [command]
   
   Commands:
   check             Check for updates
   pull              Install updates
   status            Show version status
   
   Examples:
   trooper update check
   trooper update pull
   ```

4. **process-quotes** - Process quote audio files

   ```bash
   trooper process-quotes [options]
   
   Options:
   --quotes-file     Custom quotes YAML file
   --clean           Regenerate all audio files
   
   Examples:
   trooper process-quotes
   trooper process-quotes --clean
   ```

#### Global Options

These options are available for all commands:

```bash
-v, --verbose       Enable verbose logging
-h, --help         Show command help
```

### Basic Commands

1. **Basic Text-to-Speech**

   ```bash
   trooper say 'Stop right there!'
   ```

2. **Adjust Volume (1-11)**

   ```bash
   trooper say -v 11 'Intruder alert!'
   ```

3. **Set Urgency and Context**

   ```bash
   trooper say --volume 11 --urgency high --context combat 'Enemy spotted!'
   ```

### Quote Sequences

The `sequence` command plays a series of related quotes with proper timing and transitions:

1. **Basic Sequence**

   ```bash
   # Play 3 combat quotes
   trooper sequence -c combat

   # Play 5 patrol quotes
   trooper sequence -c patrol -n 5
   ```

2. **Filtered Sequences**

   ```bash
   # Play quotes with specific tags
   trooper sequence -c combat --tags alert tactical

   # Play quotes from specific context
   trooper sequence -c patrol --context inspection
   ```

3. **Sequence Options**

   - `-c, --category`: Quote category (combat, patrol, etc.)
   - `--context`: Specific context within category
   - `-n, --count`: Number of quotes (default: 3)
   - `-v, --volume`: Volume level (1-11)
   - `--tags`: Filter quotes by tags

4. **Examples**

   ```bash
   # High-volume combat sequence
   trooper sequence -c combat -v 11 -n 4

   # Patrol sequence with specific tags
   trooper sequence -c patrol --tags alert warning -n 3

   # Mixed category sequence
   trooper sequence --tags imperial threat
   ```

The sequence system automatically:

- Avoids repeating recent quotes
- Maintains appropriate pauses between quotes
- Respects quote relationships (can_follow rules)
- Manages audio file cleanup

### Quotes System

The Trooper CLI includes a sophisticated quote system that allows you to manage and play pre-recorded Stormtrooper quotes.

#### Quote Configuration

Quotes are defined in YAML format in the `quotes.yml` file:

```yaml
categories:
  combat:
    - text: "Enemy spotted!"
      tags: [alert, combat]
      context: combat
      urgency: high
    
  patrol:
    - text: "Area secure."
      tags: [status, patrol]
      context: patrol
      urgency: normal

  alert:
    - text: "Intruder detected!"
      tags: [alert, security]
      context: alert
      urgency: high
```

#### Quote Properties

- **text**: The actual quote text (required)
- **tags**: List of tags for filtering (optional)
- **context**: Voice context for the quote (optional)
- **urgency**: Voice urgency level (optional)
- **volume**: Override default volume (optional)

#### Audio File Management

Audio files are automatically generated and cached:

```text
audio/
├── cache/
│   ├── combat/
│   │   └── enemy_spotted.wav
│   ├── patrol/
│   │   └── area_secure.wav
│   └── alert/
│       └── intruder_detected.wav
└── custom/
    └── your_custom_files.wav
```

#### Managing Quotes

1. **Add New Quotes**
   - Add entries to `quotes.yml`
   - Run `trooper process-quotes`

2. **Regenerate Audio**
   - Use `trooper process-quotes --clean`
   - Audio files will be regenerated

3. **Custom Audio**
   - Place WAV files in `audio/custom/`
   - Reference in `quotes.yml` with `file: custom/filename.wav`

#### Playing Quotes

1. **Single Quote**

   ```bash
   trooper sequence -c combat -n 1
   ```

2. **Quote Sequence**

   ```bash
   trooper sequence -c patrol -n 3
   ```

3. **Filtered Quotes**

   ```bash
   trooper sequence --tags alert combat
   ```

#### Best Practices

1. Keep quotes short and clear
2. Use appropriate categories and tags
3. Maintain consistent naming conventions
4. Regular backup of `quotes.yml`
5. Test new quotes before deployment

### Audio System

The Trooper CLI uses a sophisticated audio system for text-to-speech conversion and playback.

#### Audio Configuration

Configure audio settings in your `.env` file:

```bash
# Audio Settings
TROOPER_AUDIO_DEVICE=default    # Audio output device
TROOPER_VOLUME=5                # Default volume (1-11)
TROOPER_CACHE_DIR=audio/cache   # Audio cache directory
```

#### Audio Devices

List and manage audio devices:

```bash
# List available devices
trooper devices

# Set default device
trooper config device <device_id>
```

#### Voice Parameters

1. **Volume Levels**
   - Range: 1-11 (Spinal Tap style)
   - Default: 5
   - Override: `-v` or `--volume` flag

2. **Urgency Levels**
   - low: Casual conversation
   - normal: Standard reporting
   - high: Combat or alerts

3. **Voice Contexts**
   - general: Default context
   - combat: Battle situations
   - alert: Warning messages
   - patrol: Routine duties

#### Audio Caching

The system automatically caches generated audio:

1. **Cache Location**
   - Default: `audio/cache/`
   - Organized by categories
   - Automatic cleanup of old files

2. **Cache Management**

   ```bash
   # Clear cache
   rm -rf audio/cache/*
   
   # Regenerate cache
   trooper process-quotes --clean
   ```

#### Performance Optimization

1. **Memory Usage**
   - Cached files reduce CPU load
   - Automatic garbage collection
   - Configurable cache size

2. **Playback Settings**
   - Buffer size optimization
   - Device-specific settings
   - Latency management

#### Troubleshooting

1. **No Audio Output**
   - Check device selection
   - Verify volume levels
   - Test system audio

2. **Poor Audio Quality**
   - Check input text formatting
   - Verify urgency settings
   - Test different contexts

3. **High Latency**
   - Check cache status
   - Verify device settings
   - Monitor system resources

## Advanced Features

This section covers advanced features and customization options.

### Cliff Clavin Mode

The Cliff Clavin mode transforms your Stormtrooper into a Star Wars trivia expert:

1. **Activation**

   ```bash
   # Command line
   trooper ask --cliff-clavin-mode "Tell me about TIE Fighters"
   
   # Chat mode
   trooper chat start --cliff-mode
   
   # Web interface
   Toggle "Cliff Mode" button
   ```

2. **Configuration**

   ```bash
   # Environment variable
   TROOPER_CLIFF_MODE=1
   
   # Token limits
   TROOPER_CLIFF_TOKEN_LIMIT=200
   ```

3. **Best Practices**
   - Use specific questions
   - Allow context building
   - Engage with responses

### Custom Voice Profiles

Create and manage custom voice profiles:

1. **Profile Configuration**

   ```yaml
   # profiles.yml
   profiles:
     combat:
       urgency: high
       volume: 8
       context: combat
     
     patrol:
       urgency: normal
       volume: 5
       context: patrol
   ```

2. **Usage**

   ```bash
   trooper say --profile combat "Enemy spotted!"
   trooper say --profile patrol "Area secure"
   ```

### Sequence Automation

Create complex quote sequences:

1. **Sequence Definition**

   ```yaml
   # sequences.yml
   sequences:
     patrol_start:
       - category: patrol
         context: start
         delay: 1
       - category: status
         context: report
         delay: 2
   ```

2. **Execution**

   ```bash
   trooper sequence patrol_start
   trooper sequence --random patrol
   ```

### Web Interface Customization

Customize the web interface:

1. **Theme Configuration**

   ```bash
   # .env
   TROOPER_THEME=dark
   TROOPER_ACCENT_COLOR=#FF0000
   ```

2. **Custom Templates**
   - Override default templates
   - Add custom CSS/JS
   - Modify layout

### Advanced Audio Processing

Fine-tune audio processing:

1. **Audio Parameters**

   ```bash
   # .env
   TROOPER_AUDIO_QUALITY=high
   TROOPER_SAMPLE_RATE=48000
   TROOPER_BUFFER_SIZE=2048
   ```

2. **Effects Chain**
   - Custom audio effects
   - Voice modulation
   - Sound mixing

### API Integration

Extend functionality with APIs:

1. **Custom Endpoints**

   ```python
   # custom_endpoints.py
   @app.route('/custom')
   def custom_endpoint():
       return jsonify({"status": "ok"})
   ```

2. **Webhook Support**
   - Event notifications
   - Integration triggers
   - Status updates

### Performance Tuning

Optimize for your environment:

1. **Cache Configuration**

   ```bash
   # .env
   TROOPER_CACHE_SIZE=1GB
   TROOPER_CACHE_TTL=7d
   TROOPER_PRELOAD=1
   ```

2. **Resource Management**
   - Memory optimization
   - CPU utilization
   - Network usage

### Development Tools

Advanced development features:

1. **Debug Tools**

   ```bash
   # Enable development mode
   export TROOPER_DEV=1
   
   # Start debug server
   trooper debug server
   ```

2. **Testing Utilities**
   - Mock responses
   - Performance profiling
   - Coverage analysis

## Performance & Maintenance

This section covers performance optimization and system maintenance.

### Performance Monitoring

1. **System Resources**

   ```bash
   # Monitor CPU and memory
   top -p $(pgrep -f trooper)
   
   # Check disk usage
   du -sh audio/cache/
   ```

2. **Response Times**
   - API latency
   - Audio generation speed
   - Playback performance

3. **Resource Limits**

   ```bash
   # Environment settings
   TROOPER_MAX_MEMORY=1GB
   TROOPER_MAX_CACHE=5GB
   TROOPER_MAX_PROCESSES=4
   ```

### Cache Management

1. **Audio Cache**

   ```bash
   # Clear cache
   trooper cache clear
   
   # Optimize cache
   trooper cache optimize
   
   # View cache stats
   trooper cache status
   ```

2. **Cache Configuration**

   ```bash
   # .env settings
   TROOPER_CACHE_STRATEGY=lru
   TROOPER_CACHE_MAX_AGE=7d
   TROOPER_CACHE_MIN_FREE=1GB
   ```

### System Maintenance

1. **Regular Tasks**

   ```bash
   # Daily maintenance
   trooper maintenance daily
   
   # Weekly cleanup
   trooper maintenance weekly
   ```

2. **Backup Management**

   ```bash
   # Backup configuration
   trooper backup config
   
   # Backup audio cache
   trooper backup cache
   ```

### Log Management

1. **Log Rotation**

   ```bash
   # Configure rotation
   TROOPER_LOG_MAX_SIZE=100MB
   TROOPER_LOG_BACKUP_COUNT=5
   ```

2. **Log Analysis**

   ```bash
   # View recent errors
   trooper logs --level ERROR
   
   # Search logs
   trooper logs --search "audio device"
   ```

### Health Checks

1. **System Status**

   ```bash
   # Check all components
   trooper status
   
   # Detailed health report
   trooper health --verbose
   ```

2. **Monitoring Endpoints**

   ```bash
   # Health endpoint
   curl http://localhost:5001/health
   
   # Metrics endpoint
   curl http://localhost:5001/metrics
   ```

### Performance Optimization

1. **Audio Processing**
   - Buffer size tuning
   - Sample rate optimization
   - Compression settings

2. **API Optimization**
   - Request batching
   - Response caching
   - Connection pooling

### System Updates

1. **Software Updates**

   ```bash
   # Check for updates
   trooper update check
   
   # Apply updates
   trooper update apply
   ```

2. **Dependencies**

   ```bash
   # Update dependencies
   pip install -U -r requirements.txt
   
   # Check for vulnerabilities
   safety check
   ```

### Disaster Recovery

1. **Backup Strategy**
   - Configuration files
   - Audio cache
   - Custom profiles
   - Log files

2. **Recovery Procedures**
   - System restore
   - Cache rebuild
   - Configuration reset

## Development

This section provides information for developers who want to contribute to or modify the Trooper CLI.

### Development Setup

1. **Clone the Repository**

   ```bash
   git clone https://github.com/yourusername/trooper-cli.git
   cd trooper-cli
   ```

2. **Create Development Environment**

   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/macOS
   # or
   .\venv\Scripts\activate  # Windows
   ```

3. **Install Development Dependencies**

   ```bash
   pip install -e ".[dev]"
   ```

### Project Structure

```bash
trooper-cli/
├── src/
│   ├── cli/            # Command-line interface
│   ├── audio/          # Audio processing
│   ├── openai/         # AI integration
│   ├── web/            # Web interface
│   └── utils/          # Shared utilities
├── tests/              # Test suite
├── docs/               # Documentation
└── scripts/            # Development scripts
```

### Testing

1. **Run Test Suite**

   ```bash
   pytest
   pytest tests/test_audio.py  # Single module
   pytest -v                   # Verbose output
   ```

2. **Coverage Report**

   ```bash
   pytest --cov=src tests/
   ```

### Code Style

1. **Format Code**

   ```bash
   black src/ tests/
   isort src/ tests/
   ```

2. **Lint Code**

   ```bash
   flake8 src/ tests/
   pylint src/ tests/
   ```

### Documentation

1. **Build Documentation**

   ```bash
   cd docs
   make html
   ```

2. **View Documentation**

   ```bash
   python -m http.server -d docs/_build/html
   ```

### Git Workflow

1. **Create Feature Branch**

   ```bash
   git checkout -b feature/your-feature
   ```

2. **Commit Changes**

   ```bash
   git add .
   git commit -m "feat: your feature description"
   ```

3. **Push Changes**

   ```bash
   git push origin feature/your-feature
   ```

### Release Process

1. **Update Version**
   - Update version in `setup.py`
   - Update CHANGELOG.md

2. **Create Release**

   ```bash
   git tag -a v1.0.0 -m "Release v1.0.0"
   git push origin v1.0.0
   ```

3. **Build Distribution**

   ```bash
   python -m build
   ```

### Contributing Guidelines

1. **Before Contributing**
   - Read CONTRIBUTING.md
   - Check existing issues
   - Discuss major changes

2. **Pull Request Process**
   - Follow code style
   - Add tests
   - Update documentation
   - Request review

3. **Code Review**
   - Address feedback
   - Keep changes focused
   - Maintain clean history

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

### Configuration Management

The tool supports persistent configuration through a `.env` file. You can manage settings using the `config` command:

1. **Initialize Configuration**

   ```bash
   # Create a new .env file from example
   cp .env-example .env
   
   # Edit the .env file with your settings
   # Or use the config command:
   trooper config init
   ```

2. **Set Audio Device**

   ```bash
   # List available devices
   trooper devices
   
   # Set the audio device by ID
   trooper config device 1
   ```

3. **View Configuration**

   ```bash
   # Show current settings
   trooper config show
   ```

The configuration file (`.env`) stores:

- `TROOPER_AUDIO_DEVICE`: Audio output device ID
- `AWS_PROFILE`: AWS profile for Polly access
- `AWS_DEFAULT_REGION`: AWS region for Polly (must support neural voices)

You can also edit the `.env` file directly with any text editor.

### Software Updates

The tool includes built-in update management through the `update` command:

1. **Check for Updates**

   ```bash
   # Check if updates are available
   trooper update check
   ```

2. **Install Updates**

   ```bash
   # Pull and install latest updates
   trooper update pull
   ```

3. **View Status**

   ```bash
   # Show current version and update status
   trooper update status
   ```

The update system:

- Checks GitHub for new versions
- Safely pulls updates
- Reinstalls the package automatically
- Maintains your local configuration

Note: After updating, you may need to:

1. Restart any running instances of trooper
2. Reactivate your virtual environment
3. Check the changelog for breaking changes

## Audio Files

Audio files for the Stormtrooper voice assistant are organized in the `audio/` directory, with subdirectories matching the categories in `quotes.yaml`:

```bash
audio/
├── combat/
├── patrol/
├── humor/
├── monologues/
└── stall/
```

Each audio file should be referenced in `quotes.yaml` using the `audio_file` field, which specifies the path relative to the `audio/` directory. For example:

```yaml
categories:
  combat:
    contexts:
      attack:
        - text: "For the Empire!"
          urgency: high
          tags: ["aggressive"]
          audio_file: "combat/for_the_empire.wav"
```

## Quote Sequence Rules

Quotes can be configured with sequence rules to control their playback:

- `audio_file`: Path to the WAV file relative to the `audio/` directory
- `can_follow`: List of quote IDs that this quote can follow
- `min_pause`: Minimum pause in seconds before playing this quote
- `max_pause`: Maximum pause in seconds before playing this quote

Example:

```yaml
- text: "Did you hear something?"
  urgency: medium
  tags: ["suspicious"]
  audio_file: "patrol/hear_something.wav"
  can_follow: ["patrol_start", "footsteps"]
  min_pause: 2
  max_pause: 5
```

## Validation

The `validate.py` script checks the structure and content of `quotes.yaml`, ensuring:

1. All required fields are present (text, urgency, tags)
2. Valid urgency levels (low, medium, high, normal)
3. Tags are provided as lists
4. Optional sequence fields have correct types:
   - `audio_file`: string
   - `can_follow`: list
   - `min_pause`: number
   - `max_pause`: number

Run validation with:

```bash
python3 validate.py
```

## Chat Mode

The chat mode provides an interactive conversation interface with the Stormtrooper:

```bash
# Start chat mode
trooper chat start

# Start in Cliff Clavin mode
trooper chat start --cliff-mode

# Toggle Cliff mode during session
trooper chat mode
```

### Chat Features

- Interactive conversation
- Context preservation
- Mode switching
- Audio response playback
- Clean exit with Ctrl+C

### Cliff Clavin Mode

When enabled, the Stormtrooper will occasionally include obscure Star Wars trivia in responses.

## Performance Optimization

### Audio Caching

The system automatically caches processed audio to improve response times:

- Up to 10 most recent responses cached
- Automatic cache cleanup
- Memory usage monitoring
- Device verification

### Error Handling

The system includes robust error handling for:

- Audio device issues (falls back to default device)
- Network interruptions
- Memory constraints
- File system errors

### Best Practices

1. Use consistent volume levels
2. Clear chat history when switching contexts
3. Monitor memory usage for long sessions
4. Use appropriate urgency levels for context

### Web Interface

The Trooper CLI includes a web interface that provides a graphical way to interact with the Stormtrooper AI. The web interface is currently supported on Linux systems only.

#### Features

- Real-time chat with audio responses
- Toggle Cliff Clavin (trivia) mode
- Toggle standup mode
- View and manage conversation history
- Adjustable audio settings
- Mobile-friendly responsive design

#### Configuration

The web interface can be configured using environment variables in your `.env` file:

```bash
# Web Interface Configuration
TROOPER_WEB_PORT=5001        # Web server port (default: 5001)
TROOPER_WEB_HOST=0.0.0.0     # Web server host (default: 0.0.0.0)
TROOPER_INSTALL_PATH=/opt/trooper-cli  # Installation directory
```

#### Installation (Linux Only)

1. Configure installation path and environment:

   ```bash
   # Set up environment
   cp .env-example .env
   # Edit .env with your settings
   nano .env
   ```

2. Install the systemd service:

   ```bash
   # The install script will handle this automatically
   ./install.sh
   ```

3. Enable and start the service:

   ```bash
   systemctl --user enable trooper-web
   systemctl --user start trooper-web
   ```

4. Check service status:

   ```bash
   systemctl --user status trooper-web
   ```

The web interface will be available at:
- Local: http://localhost:5001 (or your configured port)
- Network: http://<your-ip>:5001

### Troubleshooting

#### Installation Issues

1. **Command Not Found**

   ```bash
   # Check if TROOPER_INSTALL_PATH is set correctly
   echo $TROOPER_INSTALL_PATH
   
   # Verify virtual environment exists
   ls -l $TROOPER_INSTALL_PATH/.venv
   
   # Reinstall CLI wrapper
   sudo ./install.sh
   ```

2. **Import Errors**

   ```bash
   # Verify installation path
   echo $TROOPER_INSTALL_PATH
   
   # Reinstall in the correct location
   export TROOPER_INSTALL_PATH=/your/desired/path
   ./install.sh
   ```

3. **Missing Dependencies**

   ```bash
   # Ensure you're in the correct directory
   cd $TROOPER_INSTALL_PATH
   
   # Install all dependencies
   pip install -r requirements.txt
   ```

#### Web Interface Issues

1. **Service Won't Start**

   ```bash
   # Check environment file
   systemctl --user show-environment | grep TROOPER
   
   # Verify paths in service file
   cat ~/.config/systemd/user/trooper-web.service
   
   # Check service status
   systemctl --user status trooper-web
   
   # View logs
   journalctl --user -u trooper-web
   ```

2. **Port Conflicts**

   ```bash
   # Check port usage
   sudo lsof -i :5001
   
   # Configure different port in .env
   TROOPER_WEB_PORT=5002
   
   # Restart service
   systemctl --user restart trooper-web
   ```

3. **Path-Related Issues**

   ```bash
   # Verify installation path
   echo $TROOPER_INSTALL_PATH
   
   # Check if virtual environment exists
   ls -l $TROOPER_INSTALL_PATH/.venv
   
   # Reinstall with correct path
   export TROOPER_INSTALL_PATH=/correct/path
   ./install.sh
   ```

## Troubleshooting

This section covers common issues and their solutions.

### Installation Issues

1. **Command Not Found**

   ```bash
   # Verify virtual environment is activated
   source venv/bin/activate  # Linux/macOS
   # or
   .\venv\Scripts\activate  # Windows
   
   # Verify installation
   pip list | grep trooper
   ```

2. **Import Errors**

   ```bash
   # Verify installation path
   echo $TROOPER_INSTALL_PATH
   
   # Reinstall in the correct location
   export TROOPER_INSTALL_PATH=/your/desired/path
   ./install.sh
   ```

3. **Missing Dependencies**

   ```bash
   # Ensure you're in the correct directory
   cd $TROOPER_INSTALL_PATH
   
   # Install all dependencies
   pip install -r requirements.txt
   ```

### Audio Issues

1. **No Audio Output**
   - Check system audio
   - Verify audio device:

     ```bash
     trooper devices
     trooper config device <id>
     ```

   - Test with maximum volume:

     ```bash
     trooper say -v 11 "Test"
     ```

2. **Poor Audio Quality**
   - Check input text formatting
   - Try different urgency levels
   - Verify audio device capabilities
   - Test with different volume levels

3. **Audio Device Problems**

   ```bash
   # List available devices
   trooper devices
   
   # Set specific device
   export TROOPER_AUDIO_DEVICE=1
   
   # Test configuration
   trooper say "Testing audio device"
   ```

### API Integration Issues

1. **AWS Polly**
   - Verify credentials:

     ```bash
     aws configure list
     aws polly describe-voices
     ```

   - Check IAM permissions
   - Verify region support
   - Monitor service quotas

2. **OpenAI API**
   - Verify API key
   - Check rate limits
   - Monitor usage
   - Test connection:

     ```bash
     trooper ask "Test message"
     ```

### Web Interface Issues

1. **Service Won't Start**

   ```bash
   # Check environment file
   systemctl --user show-environment | grep TROOPER
   
   # Verify paths in service file
   cat ~/.config/systemd/user/trooper-web.service
   
   # Check service status
   systemctl --user status trooper-web
   
   # View logs
   journalctl --user -u trooper-web
   ```

2. **Port Conflicts**

   ```bash
   # Check port usage
   sudo lsof -i :5001
   
   # Configure different port in .env
   TROOPER_WEB_PORT=5002
   
   # Restart service
   systemctl --user restart trooper-web
   ```

3. **Path-Related Issues**

   ```bash
   # Verify installation path
   echo $TROOPER_INSTALL_PATH
   
   # Check if virtual environment exists
   ls -l $TROOPER_INSTALL_PATH/.venv
   
   # Reinstall with correct path
   export TROOPER_INSTALL_PATH=/correct/path
   ./install.sh
   ```

### Quote System Issues

1. **Quote Processing**

   ```bash
   # Regenerate all quotes
   trooper process-quotes --clean
   
   # Verify YAML syntax
   trooper process-quotes --debug
   ```

2. **Missing Audio Files**
   - Check directory permissions
   - Verify disk space
   - Regenerate specific categories
   - Check file naming

### Common Error Messages

1. **"Failed to initialize audio device"**
   - Verify device exists
   - Check permissions
   - Try different device

2. **"API rate limit exceeded"**
   - Wait and retry
   - Check quota usage
   - Implement rate limiting

3. **"Invalid configuration"**
   - Verify .env file
   - Check YAML syntax
   - Validate settings

### Getting Help

1. **Debug Mode**

   ```bash
   # Enable debug logging
   export TROOPER_DEBUG=1
   
   # Run with verbose output
   trooper -v command
   ```

2. **Logging**
   - Check log files
   - Enable debug logging
   - Monitor system logs

3. **Support**
   - Check documentation
   - Search issues
   - Create detailed bug report
