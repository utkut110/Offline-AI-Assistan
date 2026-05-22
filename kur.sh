#!/bin/bash
# Yerel AI Asistan - Linux/macOS Kurulum ve Çalıştırma

set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color
BOLD='\033[1m'

echo -e "${CYAN}${BOLD}"
echo "╔══════════════════════════════════════════════╗"
echo "║   YEREL YAPAY ZEKA ASİSTANI - KURULUM       ║"
echo "╚══════════════════════════════════════════════╝"
echo -e "${NC}"

# Python kontrolü
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}[HATA] Python3 kurulu değil!${NC}"
    echo "Kurulum:"
    echo "  Ubuntu/Debian: sudo apt install python3"
    echo "  macOS: brew install python3"
    exit 1
fi
echo -e "${GREEN}[OK] Python3 bulundu: $(python3 --version)${NC}"

# Ollama kurulu mu?
if ! command -v ollama &> /dev/null; then
    echo -e "${YELLOW}[UYARI] Ollama kurulu değil. Kuruluyor...${NC}"
    
    if [[ "$OSTYPE" == "darwin"* ]]; then
        if command -v brew &> /dev/null; then
            brew install ollama
        else
            echo "macOS için: https://ollama.com/download/mac"
            exit 1
        fi
    else
        curl -fsSL https://ollama.com/install.sh | sh
    fi
    echo -e "${GREEN}[OK] Ollama kuruldu.${NC}"
fi

echo -e "${GREEN}[OK] Ollama bulundu: $(ollama --version)${NC}"

# Ollama servisini başlat
if ! curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
    echo -e "${YELLOW}Ollama servisi başlatılıyor...${NC}"
    ollama serve &
    sleep 3
fi

# Model kontrolü
MODELLER=$(ollama list 2>/dev/null | tail -n +2 | awk '{print $1}')

if [ -z "$MODELLER" ]; then
    echo -e "${YELLOW}Hiç model kurulu değil.${NC}"
    echo -e "llama3.1 modeli indiriliyor (~5GB)..."
    echo -e "${YELLOW}Bu işlem birkaç dakika sürebilir.${NC}"
    ollama pull llama3.1
    echo -e "${GREEN}[OK] llama3.1 indirildi!${NC}"
else
    echo -e "${GREEN}[OK] Kurulu modeller:${NC}"
    echo "$MODELLER" | while read m; do echo "  • $m"; done
fi

echo ""
echo -e "${GREEN}${BOLD}"
echo "╔══════════════════════════════════════════════╗"
echo "║         KURULUM TAMAMLANDI! ✓                ║"
echo "╚══════════════════════════════════════════════╝"
echo -e "${NC}"
echo -e "Başlatmak için: ${CYAN}python3 ai_asistan.py${NC}"
echo ""

# Hemen başlatmak ister mi?
read -p "Şimdi başlatmak ister misiniz? (e/h): " cevap
if [[ "$cevap" == "e" || "$cevap" == "E" ]]; then
    python3 "$(dirname "$0")/ai_asistan.py"
fi
