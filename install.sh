#!/usr/bin/env bash
set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}Welcome to the hey-cli cross-platform installer!${NC}"
echo -e "This script will setup Python, pipx, Ollama, and explicitly build hey-cli locally.\n"

# 1. Check Python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Error: python3 is not installed. Please install Python 3.9+ first.${NC}"
    exit 1
fi
echo -e "✔️  Python 3 found."

# 2. Setup pipx
if ! command -v pipx &> /dev/null; then
    echo -e "${BLUE}pipx not found. Attempting to install via system package manager...${NC}"
    OS="$(uname -s)"
    if [ "$OS" = "Darwin" ]; then
        if command -v brew &> /dev/null; then
            brew install pipx
        else
            echo -e "${RED}Homebrew not found. Please install pipx manually: https://pipx.pypa.io/stable/installation/${NC}"
            exit 1
        fi
    elif [ "$OS" = "Linux" ]; then
        if command -v apt-get &> /dev/null; then
            sudo apt-get update && sudo apt-get install -y pipx
        elif command -v dnf &> /dev/null; then
            sudo dnf install -y pipx
        elif command -v pacman &> /dev/null; then
            sudo pacman -Sy --noconfirm python-pipx
        elif command -v zypper &> /dev/null; then
            sudo zypper install -y python3-pipx
        else
             echo -e "${RED}Unsupported Linux package manager. Please install pipx manually.${NC}"
             exit 1
        fi
    fi
    pipx ensurepath
else
    echo -e "✔️  pipx found."
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
pipx install hey-cli-python --force

echo -e "\n${GREEN}============ SUCCESS =============${NC}"
echo -e "hey-cli is successfully installed!"
echo -e "You may need to restart your terminal or run ${BLUE}source ~/.bashrc${NC} (or .zshrc) for the 'hey' command to be recognized."
echo -e "Test it out by typing: ${BLUE}hey is my docker hub running?${NC}"
