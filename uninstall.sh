#!/usr/bin/env bash
set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${BLUE}hey-cli Uninstaller${NC}"
echo -e "This will remove hey-cli and its configuration files.\n"

REMOVED=0

# 1. Homebrew
if command -v brew &> /dev/null && brew list hey-cli &> /dev/null 2>&1; then
    echo -e "${BLUE}Removing hey-cli via Homebrew...${NC}"
    brew uninstall hey-cli
    echo -e "${GREEN}[OK] Homebrew package removed.${NC}"
    REMOVED=1
fi

# 2. uv
if command -v uv &> /dev/null; then
    if uv tool list 2>/dev/null | grep -q "hey-cli-python"; then
        echo -e "${BLUE}Removing hey-cli via uv...${NC}"
        uv tool uninstall hey-cli-python
        echo -e "${GREEN}[OK] uv package removed.${NC}"
        REMOVED=1
    fi
fi

# 3. pipx
if command -v pipx &> /dev/null && pipx list 2>/dev/null | grep -q "hey-cli-python"; then
    echo -e "${BLUE}Removing hey-cli via pipx...${NC}"
    pipx uninstall hey-cli-python
    echo -e "${GREEN}[OK] pipx package removed.${NC}"
    REMOVED=1
fi

# 4. pip (fallback)
if pip show hey-cli-python &> /dev/null 2>&1; then
    echo -e "${BLUE}Removing hey-cli via pip...${NC}"
    pip uninstall hey-cli-python -y
    echo -e "${GREEN}[OK] pip package removed.${NC}"
    REMOVED=1
fi

if [ "$REMOVED" -eq 0 ]; then
    echo -e "${YELLOW}No hey-cli installation found (checked Homebrew, uv, pipx, pip).${NC}"
fi

# 4. Config files
echo ""
CONFIG_FILES=(
    "$HOME/.hey-rules.json"
    "$HOME/.hey_history.json"
)

for f in "${CONFIG_FILES[@]}"; do
    if [ -f "$f" ]; then
        echo -e "${YELLOW}Found config: $f${NC}"
    fi
done

read -p "Remove configuration files? [y/N]: " REMOVE_CONFIG
if [[ "$REMOVE_CONFIG" =~ ^[Yy]$ ]]; then
    for f in "${CONFIG_FILES[@]}"; do
        if [ -f "$f" ]; then
            rm "$f"
            echo -e "${GREEN}[OK] Removed $f${NC}"
        fi
    done
else
    echo -e "Keeping configuration files."
fi

echo -e "\n${GREEN}============ DONE =============${NC}"
echo -e "hey-cli has been uninstalled."
echo -e "Ollama and your models were ${YELLOW}not${NC} removed. To remove Ollama, visit: https://ollama.com"
