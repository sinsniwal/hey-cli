#!/usr/bin/env bash
{ # Wrap the entire script in a block to prevent stdin consumption issues with curl | bash

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 0. Detect Architecture for macOS
BREW_CMD="brew"
if [ "$(uname -s)" = "Darwin" ]; then
    # If on Apple Silicon (detected by sysctl) but running as x86_64, use arch -arm64
    if [ "$(uname -m)" = "x86_64" ] && [ "$(sysctl -in sysctl.proc_translated 2>/dev/null)" = "1" ]; then
        echo -e "${BLUE}Detected Rosetta 2 emulation. Switching to native ARM mode...${NC}"
        BREW_CMD="arch -arm64 brew"
    fi
fi

echo -e "${BLUE}Welcome to the hey-cli cross-platform installer!${NC}"
echo -e "This script will setup Python, uv, Ollama, and explicitly build hey-cli locally.\n"

# 1. Check Python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Error: python3 is not installed. Please install Python 3.9+ first.${NC}"
    exit 1
fi
echo -e "✔️  Python 3 found."

# 2. Setup uv
if ! command -v uv &> /dev/null; then
    echo -e "${BLUE}uv not found. Attempting to install via official script...${NC}"
    curl -LsSf https://astral.sh/uv/install.sh | sh
    # Ensure uv is in the PATH for this session
    export PATH="$HOME/.local/bin:$PATH"
    
    if ! command -v uv &> /dev/null; then
        echo -e "${RED}uv installation failed or not in PATH. Please install uv manually: https://docs.astral.sh/uv/getting-started/installation/${NC}"
        exit 1
    fi
else
    echo -e "✔️  uv found."
fi

# 3. Setup Ollama
if ! command -v ollama &> /dev/null; then
    echo -e "\n${BLUE}Ollama is not installed. Installing official Ollama daemon...${NC}"
    if [ "$(uname -s)" = "Darwin" ]; then
        echo -e "${RED}Automatic Ollama installation on macOS via bash script is unsupported.${NC}"
        echo -e "Please download Ollama for macOS here: https://ollama.com/download/mac"
        echo -e "Once installed, run this script again!"
        exit 1
    else
        curl -fsSL https://ollama.com/install.sh | sh
    fi
else
    echo -e "✔️  Ollama found."
fi

# Ensure Ollama is running before proceeding
echo -e "\n${BLUE}Verifying Ollama server status...${NC}"
if ! curl -s http://localhost:11434/api/tags > /dev/null; then
    echo -e "Ollama server is not running. Attempting to start..."
    if [[ "$OSTYPE" == "darwin"* ]]; then
        open -a Ollama
    elif command -v systemctl &> /dev/null; then
        sudo systemctl start ollama || true
    else
        ollama serve > /dev/null 2>&1 &
    fi
    
    echo -n "Waiting for Ollama to boot"
    MAX_RETRIES=10
    COUNT=0
    until curl -s http://localhost:11434/api/tags > /dev/null || [ $COUNT -eq $MAX_RETRIES ]; do
        echo -n "."
        sleep 2
        ((COUNT++))
    done
    echo ""
fi

if ! curl -s http://localhost:11434/api/tags > /dev/null; then
    echo -e "${RED}Warning: Could not connect to Ollama server at localhost:11434.${NC}"
    echo -e "Please ensure Ollama is running and try again."
fi

# 4. Authenticate with Ollama
echo -e "\n${BLUE}Authenticating with Ollama...${NC}"
echo -e "If prompted, sign in with your Ollama account."
ollama login || echo -e "${RED}Warning: Authentication skipped. You may see 401 errors if your Ollama instance requires auth.${NC}"
echo -e "✔️  Authentication complete."

# 5. Pull Default Model
MODEL="gpt-oss:20b-cloud"
echo -e "\n${BLUE}Pulling default language model ($MODEL). This may take several minutes depending on your network...${NC}"
# We append || true so the script doesn't crash if the daemon isn't fully booted
ollama pull "$MODEL" || echo -e "${RED}Warning: Could not pull $MODEL. Ensure 'ollama serve' is running in the background.${NC}"

# 6. Install hey-cli
echo -e "\n${BLUE}Installing hey-cli-python...${NC}"
if [ "$(uname -s)" = "Darwin" ] && [ "$(uname -m)" = "x86_64" ] && [ "$(sysctl -in sysctl.proc_translated 2>/dev/null)" = "1" ]; then
    arch -arm64 uv tool install hey-cli-python --force
else
    uv tool install hey-cli-python --force
fi

echo -e "\n${GREEN}============ SUCCESS =============${NC}"
echo -e "hey-cli is successfully installed!"
echo -e "You may need to restart your terminal or run ${BLUE}source ~/.bashrc${NC} (or .zshrc) for the 'hey' command to be recognized."
echo -e "Test it out by typing: ${BLUE}hey hi${NC}"

} # End of script block
