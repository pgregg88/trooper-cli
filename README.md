# Trooper Voice Assistant

A command-line tool that converts text to speech with a Stormtrooper voice effect and manages a collection of pre-configured quotes.

## Features

- Text-to-speech using Amazon Polly's neural voices
- Stormtrooper voice effect processing
- Volume control (1-11)
- Multiple voice contexts (general, combat, alert, patrol)
- Urgency levels (low, normal, high)
- Pre-configured quotes system with YAML configuration
- Audio file management and caching
- Command-line interface

## Installation

### Prerequisites

1. Python 3.11.2 (recommended) or higher
2. pip (Python package installer)
3. pyenv (Python version manager)
4. AWS account with Polly access (neural voices enabled)
5. Audio output device
6. OpenAI API key (for chat functionality)
7. System Dependencies:
   - **Linux (Ubuntu/Debian):**
     ```bash
     sudo apt-get install portaudio19-dev python3-pyaudio
     ```
   - **Linux (Fedora):**
     ```bash
     sudo dnf install portaudio-devel python3-pyaudio
     ```
   - **Linux (CentOS/RHEL):**
     ```bash
     sudo yum install portaudio-devel python3-pyaudio
     ```
   - **macOS:**
     ```bash
     brew install portaudio
     ```

### Installing pyenv

1. **macOS (using Homebrew)**

   ```bash
   # Install Homebrew if not already installed
   /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

   # Install pyenv
   brew install pyenv

   # Add pyenv to your shell configuration
   echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.zshrc
   echo 'command -v pyenv >/dev/null || export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.zshrc
   echo 'eval "$(pyenv init -)"' >> ~/.zshrc

   # Reload shell configuration
   source ~/.zshrc
   ```

2. **Linux**

   ```bash
   # Install dependencies
   sudo apt-get update
   sudo apt-get install -y make build-essential libssl-dev zlib1g-dev \
   libbz2-dev libreadline-dev libsqlite3-dev wget curl llvm \
   libncursesw5-dev xz-utils tk-dev libxml2-dev libxmlsec1-dev libffi-dev liblzma-dev

   # Install pyenv
   curl https://pyenv.run | bash

   # Add pyenv to your shell configuration
   echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.bashrc
   echo 'command -v pyenv >/dev/null || export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.bashrc
   echo 'eval "$(pyenv init -)"' >> ~/.bashrc

   # Reload shell configuration
   source ~/.bashrc
   ```

3. **Windows**

   ```powershell
   # Using PowerShell (Run as Administrator)

   # Install pyenv-win using PowerShell
   Invoke-WebRequest -UseBasicParsing -Uri "https://raw.githubusercontent.com/pyenv-win/pyenv-win/master/pyenv-win/install-pyenv-win.ps1" -OutFile "./install-pyenv-win.ps1"; &"./install-pyenv-win.ps1"

   # After installation, close and reopen PowerShell, then verify installation:
   pyenv --version

   # If you get execution policy errors, you may need to run:
   Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

   # Common issues and fixes:
   # 1. If pyenv command is not found after installation:
   #    - Check if these environment variables are set:
   #      PYENV: %USERPROFILE%\.pyenv\pyenv-win
   #      PYENV_HOME: %USERPROFILE%\.pyenv\pyenv-win
   #      Path: includes %USERPROFILE%\.pyenv\pyenv-win\bin and %USERPROFILE%\.pyenv\pyenv-win\shims
   
   # 2. If you need to set environment variables manually:
   [System.Environment]::SetEnvironmentVariable('PYENV', $env:USERPROFILE + "\.pyenv\pyenv-win", 'User')
   [System.Environment]::SetEnvironmentVariable('PYENV_HOME', $env:USERPROFILE + "\.pyenv\pyenv-win", 'User')
   $path = [System.Environment]::GetEnvironmentVariable('Path', 'User')
   [System.Environment]::SetEnvironmentVariable('Path', $path + ";" + $env:USERPROFILE + "\.pyenv\pyenv-win\bin;" + $env:USERPROFILE + "\.pyenv\pyenv-win\shims", 'User')
   ```

### Step-by-Step Installation

1. **Clone the Repository**

   ```bash
   git clone <repository-url>
   cd trooper
   
   # Set up environment configuration
   cp .env-example .env
   # Edit .env with your configuration values
   ```

2. **Set Up Python Environment**

   ```bash
   # Install Python 3.11.2 if not already installed
   pyenv install 3.11.2

   # Set local Python version
   pyenv local 3.11.2

   # Verify Python version
   python --version  # Should show Python 3.11.2

   # If you get a "command not found" error after installing pyenv:
   # 1. Make sure you've reloaded your shell configuration
   # 2. Try opening a new terminal window
   # 3. Verify pyenv is in your PATH: echo $PATH
   ```

3. **Create and Activate Virtual Environment**

   ```bash
   # Create virtual environment
   python -m venv .venv

   # Activate it
   # On macOS/Linux:
   source .venv/bin/activate
   # On Windows:
   .venv\Scripts\activate

   # Verify you're using the virtual environment
   which python  # Should point to .venv/bin/python
   ```

4. **Install the Package**

   ```bash
   # Install in development mode
   pip install -e .

   # If you get permission errors:
   # 1. Make sure your virtual environment is activated
   # 2. Try: pip install --user -e .
   ```

5. **Configure AWS Credentials**

   The tool requires AWS credentials with access to Amazon Polly neural voices. Configure these in one of these ways:

   a. Using AWS CLI with a specific profile (recommended):

   ```bash
   # Install AWS CLI if not already installed
   pip install awscli

   # Configure a specific profile for trooper
   aws configure --profile trooper

   # Set the profile in your environment
   export AWS_PROFILE=trooper
   # Or add to your shell configuration:
   echo 'export AWS_PROFILE=trooper' >> ~/.zshrc  # for zsh
   echo 'export AWS_PROFILE=trooper' >> ~/.bashrc  # for bash
   ```

   b. Environment variables:

   ```bash
   export AWS_ACCESS_KEY_ID="your_access_key"
   export AWS_SECRET_ACCESS_KEY="your_secret_key"
   export AWS_DEFAULT_REGION="us-east-1"  # Region must support neural voices
   ```

   c. Credentials file:

   ```ini
   # ~/.aws/credentials
   [trooper]
   aws_access_key_id = your_access_key
   aws_secret_access_key = your_secret_key
   region = us-east-1  # Region must support neural voices
   ```

6. **Configure OpenAI API**

   The chat functionality requires an OpenAI API key. Configure it in one of these ways:

   a. Environment variable:
   ```bash
   export OPENAI_API_KEY="your_api_key"
   # Or add to your shell configuration:
   echo 'export OPENAI_API_KEY="your_api_key"' >> ~/.zshrc  # for zsh
   echo 'export OPENAI_API_KEY="your_api_key"' >> ~/.bashrc  # for bash
   ```

   b. Add to .env file:
   ```ini
   OPENAI_API_KEY=your_api_key
   ```

7. **Verify Installation**

   ```bash
   # Check if trooper command is available
   which trooper  # Should point to .venv/bin/trooper

   # Check help
   trooper --help

   # Common issues:
   # 1. Command not found: Make sure virtual environment is activated
   # 2. Import errors: Try reinstalling the package
   # 3. AWS errors: Verify credentials and region
   ```

### Troubleshooting

1. **Python Version Issues**

   ```bash
   # List available Python versions
   pyenv versions

   # Show current Python version
   pyenv version

   # If Python version is not changing:
   pyenv rehash
   exec "$SHELL"  # Reload shell
   ```

2. **Virtual Environment Issues**

   ```bash
   # If venv creation fails:
   python -m pip install --upgrade pip
   python -m pip install --upgrade virtualenv

   # If activation fails:
   # 1. Remove existing venv
   rm -rf .venv
   # 2. Create new venv
   python -m venv .venv
   ```

3. **AWS Configuration Issues**

   ```bash
   # Test AWS configuration
   aws polly describe-voices --engine neural --profile trooper

   # If region doesn't support neural voices, try:
   aws configure set region us-east-1 --profile trooper
   ```

4. **OpenAI API Issues**

   ```bash
   # Test OpenAI configuration
   trooper ask "Test message"

   # Common issues:
   # 1. API key not found: Check OPENAI_API_KEY in environment or .env file
   # 2. Rate limits: Check your OpenAI account usage and limits
   # 3. API errors: Verify your API key is valid and has sufficient credits
   ```

## Usage

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

The `process-quotes` command generates audio files for pre-configured quotes:

1. **Process All Quotes**

   ```bash
   trooper process-quotes
   ```

2. **Regenerate All Quotes**

   ```bash
   trooper process-quotes --clean
   ```

3. **Use Custom Quotes File**

   ```bash
   trooper process-quotes --quotes-file custom_quotes.yaml
   ```

### Quotes Configuration

Quotes are configured in YAML format (`config/quotes.yaml`):

```yaml
quotes:
  - text: "Stop right there!"
    category: patrol
    context: spotted_patrol
    urgency: high

  - text: "All clear, resuming patrol."
    category: patrol
    context: status_update
    urgency: low
```

### Audio File Organization

Generated audio files are organized in two directories:

- `assets/audio/polly_raw/`: Raw audio files from Amazon Polly
- `assets/audio/processed/`: Processed audio files with Stormtrooper effect

Files are named using this pattern:
`{voice}_{engine}_{category}_{context}_{text_preview}_processed.wav`

### Command Options

#### Say Command

- `-v, --volume`: Set volume level (1-11, default: 5)
- `-u, --urgency`: Set urgency level (low, normal, high)
- `-c, --context`: Set voice context (general, combat, alert, patrol)
- `--no-play`: Generate audio without playing
- `--keep`: Keep generated audio files

#### Process-Quotes Command

- `--quotes-file`: Path to custom quotes YAML file
- `--clean`: Delete existing files before processing

### Audio Device Configuration

The tool supports multiple ways to select the audio output device:

1. **List Available Devices**

   ```bash
   # Show all available audio output devices
   trooper devices
   ```

2. **Environment Variable**

   ```bash
   # Set the audio device by ID (from 'trooper devices' output)
   export TROOPER_AUDIO_DEVICE=1
   
   # Test the selected device
   trooper say 'Testing audio device'
   ```

3. **Automatic Selection**
   If no device is specified, the tool will try:
   1. Use `TROOPER_AUDIO_DEVICE` if set
   2. Use system default output device
   3. Fall back to first available output device

Common audio device issues:

1. **Wrong Output Device**

   ```bash
   # List available devices
   trooper devices
   
   # Set the correct device ID
   export TROOPER_AUDIO_DEVICE=1  # Replace with your desired device ID
   ```

2. **No Audio Output**
   - Verify the device exists: `trooper devices`
   - Check system volume
   - Try a different device ID
   - Verify audio file generation: `trooper say --no-play --keep 'Test'`

## Troubleshooting Commands

### Common Issues

1. **Command Not Found**

   ```bash
   # Solution: Make sure virtual environment is activated
   source .venv/bin/activate  # macOS/Linux
   .venv\Scripts\activate     # Windows
   ```

2. **Import Errors**

   ```bash
   # Solution: Reinstall the package
   pip uninstall trooper
   pip install -e .
   ```

3. **Audio Device Issues**
   - Check if your system's audio device is working
   - Try adjusting volume
   - Check system audio settings

   ```bash
   # Test audio
   trooper say --volume 5 'Test'
   ```

4. **AWS Polly Issues**
   - Verify AWS credentials are properly configured
   - Check AWS IAM permissions for Polly
   - Ensure region supports neural voices
   - Check AWS service quotas and limits

   ```bash
   # Test AWS configuration
   aws polly describe-voices --engine neural
   ```

5. **Quote Processing Issues**
   - Check YAML file syntax
   - Verify audio directories exist and are writable
   - Check disk space for audio files
   - Use `--clean` flag to regenerate problematic files

### Audio Quality Issues

1. **Volume Too Low**

   ```bash
   # Increase volume (max 11)
   trooper say -v 11 'Test volume'
   ```

2. **Audio Distortion**

   ```bash
   # Try lower volume
   trooper say -v 5 'Test audio'
   ```

3. **Playback Issues**

   ```bash
   # Generate file without playing
   trooper say --no-play --keep 'Test'
   # Then play with system audio player
   ```

## Development

### Development Setup

1. **Install Development Dependencies**

   ```bash
   # After activating your virtual environment
   pip install -r requirements.txt
   ```

2. **Configure IDE (VS Code)**
   - Open the project in VS Code
   - Select the Python interpreter from your virtual environment
   - Install recommended VS Code extensions:
     - Python
     - Pylance

### Code Quality Tools

We use two main tools to maintain code quality:

1. **Pylint**
   - Code style checking and error detection
   - Configuration in `.pylintrc`
   - Run with:

     ```bash
     pylint src/
     ```

2. **MyPy**
   - Static type checking
   - Helps catch type-related errors early
   - Run with:

     ```bash
     mypy src/
     ```

### VS Code Integration

The project includes VS Code settings (`.vscode/settings.json`) that configure:

- Python interpreter path
- Linting with Pylint
- Type checking with MyPy
- Auto-formatting on save
- Import organization

### Development Best Practices

1. **Type Hints**
   - Use type hints for all function parameters and return values
   - Example:

     ```python
     def process_audio(data: np.ndarray, sample_rate: int) -> np.ndarray:
         ...
     ```

2. **Documentation**
   - Add docstrings to all functions and classes
   - Follow Google docstring format
   - Include examples in docstrings for complex functions

3. **Error Handling**
   - Use custom exceptions where appropriate
   - Log errors with loguru
   - Provide helpful error messages

4. **Code Organization**
   - Keep modules focused and single-purpose
   - Use clear, descriptive names
   - Follow Python naming conventions

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
