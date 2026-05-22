#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
╔══════════════════════════════════════════════════════════════╗
║           YEREL YAPAY ZEKA ASİSTANI - Offline AI            ║
║           Ollama tabanlı | CMD kontrolü | Türkçe            ║
╚══════════════════════════════════════════════════════════════╝
"""

import sys
import os
import json
import time
import argparse
import subprocess
import platform
from datetime import datetime
from pathlib import Path

# Renkli terminal çıktısı
class Renk:
    SIFIRLA    = "\033[0m"
    KALIN      = "\033[1m"
    MAVİ       = "\033[94m"
    YEŞİL      = "\033[92m"
    SARI       = "\033[93m"
    KIRMIZI    = "\033[91m"
    MOR        = "\033[95m"
    SİYAN      = "\033[96m"
    BEYAZ      = "\033[97m"
    GRİ        = "\033[90m"

# Windows'ta ANSI renkleri etkinleştir
if platform.system() == "Windows":
    os.system("color")
    import ctypes
    kernel32 = ctypes.windll.kernel32
    kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)

def banner():
    print(f"""
{Renk.SİYAN}{Renk.KALIN}
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║       🤖  YEREL YAPAY ZEKA ASİSTANI  🤖                      ║
║           Tamamen Offline Çalışır                            ║
║           Claude Sonnet Seviyesinde Zeka                     ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
{Renk.SIFIRLA}""")

def ollama_kurulu_mu():
    """Ollama'nın sistemde kurulu olup olmadığını kontrol eder."""
    try:
        sonuc = subprocess.run(
            ["ollama", "--version"],
            capture_output=True, text=True, timeout=5
        )
        return sonuc.returncode == 0
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False

def ollama_calisiyor_mu():
    """Ollama servisinin çalışıp çalışmadığını kontrol eder."""
    try:
        import urllib.request
        urllib.request.urlopen("http://localhost:11434/api/tags", timeout=3)
        return True
    except:
        return False

def ollama_baslat():
    """Ollama servisini arka planda başlatır."""
    try:
        if platform.system() == "Windows":
            subprocess.Popen(
                ["ollama", "serve"],
                creationflags=subprocess.CREATE_NO_WINDOW,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
        else:
            subprocess.Popen(
                ["ollama", "serve"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
        time.sleep(2)
        return True
    except Exception as e:
        return False

def mevcut_modeller():
    """Sisteme indirilen modelleri listeler."""
    try:
        import urllib.request, json
        req = urllib.request.urlopen("http://localhost:11434/api/tags", timeout=5)
        data = json.loads(req.read())
        return [m["name"] for m in data.get("models", [])]
    except:
        return []

def model_indir(model_adi):
    """Belirtilen modeli indirir ve yükleme ilerlemesini gösterir."""
    print(f"\n{Renk.SARI}📥 '{model_adi}' modeli indiriliyor...{Renk.SIFIRLA}")
    print(f"{Renk.GRİ}Bu işlem model boyutuna göre birkaç dakika sürebilir.{Renk.SIFIRLA}\n")
    
    try:
        process = subprocess.Popen(
            ["ollama", "pull", model_adi],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1
        )
        for satir in process.stdout:
            print(f"\r{Renk.SİYAN}{satir.strip()}{Renk.SIFIRLA}", end="", flush=True)
        process.wait()
        print()
        return process.returncode == 0
    except Exception as e:
        print(f"{Renk.KIRMIZI}Hata: {e}{Renk.SIFIRLA}")
        return False

def ai_yanit_al(model, mesajlar, sistem_prompt, streaming=True):
    """Ollama API'ye istek gönderir ve yanıt alır."""
    import urllib.request, json
    
    url = "http://localhost:11434/api/chat"
    
    payload = {
        "model": model,
        "messages": mesajlar,
        "system": sistem_prompt,
        "stream": streaming,
        "options": {
            "temperature": 0.7,
            "top_p": 0.9,
            "repeat_penalty": 1.1,
        }
    }
    
    veri = json.dumps(payload).encode("utf-8")
    istek = urllib.request.Request(
        url,
        data=veri,
        headers={"Content-Type": "application/json"},
        method="POST"
    )
    
    tam_yanit = ""
    
    try:
        with urllib.request.urlopen(istek, timeout=120) as yanit:
            print(f"\n{Renk.YEŞİL}🤖 Asistan:{Renk.SIFIRLA} ", end="", flush=True)
            
            if streaming:
                for satir in yanit:
                    satir = satir.decode("utf-8").strip()
                    if satir:
                        try:
                            veri_dict = json.loads(satir)
                            if "message" in veri_dict and "content" in veri_dict["message"]:
                                parcali = veri_dict["message"]["content"]
                                print(parcali, end="", flush=True)
                                tam_yanit += parcali
                            if veri_dict.get("done", False):
                                break
                        except json.JSONDecodeError:
                            continue
                print()  # Yeni satır
            else:
                veri_str = yanit.read().decode("utf-8")
                veri_dict = json.loads(veri_str)
                tam_yanit = veri_dict["message"]["content"]
                print(tam_yanit)
                
    except urllib.error.URLError as e:
        print(f"\n{Renk.KIRMIZI}Bağlantı hatası: {e}{Renk.SIFIRLA}")
        return None
    except Exception as e:
        print(f"\n{Renk.KIRMIZI}Hata: {e}{Renk.SIFIRLA}")
        return None
    
    return tam_yanit

def gecmis_kaydet(gecmis, dosya_adi=None):
    """Konuşma geçmişini JSON dosyasına kaydeder."""
    if dosya_adi is None:
        zaman = datetime.now().strftime("%Y%m%d_%H%M%S")
        dosya_adi = f"konusma_{zaman}.json"
    
    kayit_dizini = Path.home() / ".ai_asistan" / "konusmalar"
    kayit_dizini.mkdir(parents=True, exist_ok=True)
    
    dosya_yolu = kayit_dizini / dosya_adi
    
    with open(dosya_yolu, "w", encoding="utf-8") as f:
        json.dump({
            "tarih": datetime.now().isoformat(),
            "mesajlar": gecmis
        }, f, ensure_ascii=False, indent=2)
    
    return str(dosya_yolu)

def gecmis_yukle(dosya_yolu):
    """Kaydedilmiş konuşmayı yükler."""
    try:
        with open(dosya_yolu, "r", encoding="utf-8") as f:
            veri = json.load(f)
        return veri.get("mesajlar", [])
    except Exception as e:
        print(f"{Renk.KIRMIZI}Geçmiş yüklenemedi: {e}{Renk.SIFIRLA}")
        return []

def model_sec(modeller):
    """Kullanıcıdan model seçmesini ister."""
    onerilir = {
        "llama3.2":      "Meta Llama 3.2 3B  | 2GB  | Hızlı, hafif",
        "llama3.1":      "Meta Llama 3.1 8B  | 5GB  | Dengeli ✨ ÖNERİLEN",
        "mistral":       "Mistral 7B         | 4GB  | Çok iyi anlama",
        "qwen2.5":       "Qwen 2.5 7B        | 5GB  | Çok dilli, kod",
        "deepseek-r1":   "DeepSeek R1 7B     | 5GB  | Derin düşünme",
        "phi3":          "Microsoft Phi-3    | 2GB  | Küçük ama güçlü",
        "gemma2":        "Google Gemma 2 9B  | 6GB  | Google kalitesi",
        "codellama":     "Code Llama 7B      | 4GB  | Kod yazımı uzmanı",
    }
    
    print(f"\n{Renk.KALIN}{Renk.MAVİ}📋 Mevcut Modeller:{Renk.SIFIRLA}")
    
    if modeller:
        print(f"\n{Renk.YEŞİL}✅ Sisteminizde kurulu:{Renk.SIFIRLA}")
        for i, m in enumerate(modeller, 1):
            print(f"  {Renk.KALIN}{i}.{Renk.SIFIRLA} {m}")
    
    print(f"\n{Renk.SARI}📥 İndirebileceğiniz önerilen modeller:{Renk.SIFIRLA}")
    for ad, aciklama in onerilir.items():
        kurulu = "✅" if any(ad in m for m in modeller) else "📥"
        print(f"  {kurulu} {Renk.KALIN}{ad}{Renk.SIFIRLA} — {aciklama}")
    
    print(f"\n{Renk.GRİ}Model adı yazın veya kurulu model numarasını girin:{Renk.SIFIRLA}")
    print(f"{Renk.GRİ}(Boş bırakırsanız llama3.1 kullanılır){Renk.SIFIRLA}")
    
    secim = input(f"\n{Renk.SİYAN}Model > {Renk.SIFIRLA}").strip()
    
    if not secim:
        return "llama3.1"
    
    # Numara girilmişse kurulu listeden al
    if secim.isdigit() and modeller:
        idx = int(secim) - 1
        if 0 <= idx < len(modeller):
            return modeller[idx]
    
    return secim

def komutlari_goster():
    """Kullanılabilir komutları listeler."""
    print(f"""
{Renk.MAVİ}{Renk.KALIN}━━━━━━━━━━━━━━━━ KOMUTLAR ━━━━━━━━━━━━━━━━{Renk.SIFIRLA}
  {Renk.SARI}/yardim{Renk.SIFIRLA}         — Bu menüyü göster
  {Renk.SARI}/kaydet{Renk.SIFIRLA}         — Konuşmayı kaydet
  {Renk.SARI}/temizle{Renk.SIFIRLA}        — Konuşma geçmişini sıfırla
  {Renk.SARI}/model{Renk.SIFIRLA}          — Model değiştir
  {Renk.SARI}/modeller{Renk.SIFIRLA}       — Kurulu modelleri listele
  {Renk.SARI}/indir <model>{Renk.SIFIRLA}  — Yeni model indir
  {Renk.SARI}/sistem <metin>{Renk.SIFIRLA} — Sistem promptunu değiştir
  {Renk.SARI}/bilgi{Renk.SIFIRLA}          — Mevcut ayarları göster
  {Renk.SARI}/cik{Renk.SIFIRLA}            — Programdan çık
{Renk.MAVİ}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{Renk.SIFIRLA}
""")

def ana_dongu(model, sistem_prompt, gecmis=None):
    """Ana sohbet döngüsü."""
    if gecmis is None:
        gecmis = []
    
    aktif_model = model
    aktif_sistem = sistem_prompt
    
    print(f"\n{Renk.YEŞİL}✅ Asistan hazır! Model: {Renk.KALIN}{aktif_model}{Renk.SIFIRLA}")
    print(f"{Renk.GRİ}Komutlar için /yardim yazın | Çıkmak için /cik{Renk.SIFIRLA}\n")
    print(f"{Renk.MAVİ}{'━' * 60}{Renk.SIFIRLA}")
    
    while True:
        try:
            print()
            kullanici_girdisi = input(f"{Renk.MOR}👤 Siz:{Renk.SIFIRLA} ").strip()
            
            if not kullanici_girdisi:
                continue
            
            # Komut işleme
            if kullanici_girdisi.startswith("/"):
                parcalar = kullanici_girdisi.split(" ", 1)
                komut = parcalar[0].lower()
                arguman = parcalar[1] if len(parcalar) > 1 else ""
                
                if komut == "/cik":
                    kaydet_mi = input(f"\n{Renk.SARI}Konuşmayı kaydetmek ister misiniz? (e/h): {Renk.SIFIRLA}").lower()
                    if kaydet_mi == "e":
                        yol = gecmis_kaydet(gecmis)
                        print(f"{Renk.YEŞİL}✅ Kaydedildi: {yol}{Renk.SIFIRLA}")
                    print(f"\n{Renk.SİYAN}Güle güle! 👋{Renk.SIFIRLA}\n")
                    sys.exit(0)
                    
                elif komut == "/yardim":
                    komutlari_goster()
                    
                elif komut == "/kaydet":
                    yol = gecmis_kaydet(gecmis)
                    print(f"{Renk.YEŞİL}✅ Konuşma kaydedildi: {yol}{Renk.SIFIRLA}")
                    
                elif komut == "/temizle":
                    gecmis = []
                    print(f"{Renk.YEŞİL}✅ Konuşma geçmişi temizlendi.{Renk.SIFIRLA}")
                    
                elif komut == "/model":
                    modeller = mevcut_modeller()
                    aktif_model = model_sec(modeller)
                    if aktif_model not in modeller:
                        indir_mi = input(f"{Renk.SARI}Bu model kurulu değil. İndirilsin mi? (e/h): {Renk.SIFIRLA}").lower()
                        if indir_mi == "e":
                            model_indir(aktif_model)
                        else:
                            aktif_model = model
                    print(f"{Renk.YEŞİL}✅ Model değiştirildi: {aktif_model}{Renk.SIFIRLA}")
                    
                elif komut == "/modeller":
                    modeller = mevcut_modeller()
                    if modeller:
                        print(f"\n{Renk.YEŞİL}Kurulu modeller:{Renk.SIFIRLA}")
                        for m in modeller:
                            isaret = "▶" if m.startswith(aktif_model.split(":")[0]) else " "
                            print(f"  {isaret} {m}")
                    else:
                        print(f"{Renk.SARI}Hiç model kurulu değil.{Renk.SIFIRLA}")
                        
                elif komut == "/indir":
                    if arguman:
                        basarili = model_indir(arguman)
                        if basarili:
                            print(f"{Renk.YEŞİL}✅ Model indirildi: {arguman}{Renk.SIFIRLA}")
                            kullan_mi = input(f"Bu modeli şimdi kullanmak ister misiniz? (e/h): ").lower()
                            if kullan_mi == "e":
                                aktif_model = arguman
                    else:
                        print(f"{Renk.KIRMIZI}Kullanım: /indir <model_adı>{Renk.SIFIRLA}")
                        
                elif komut == "/sistem":
                    if arguman:
                        aktif_sistem = arguman
                        print(f"{Renk.YEŞİL}✅ Sistem promptu güncellendi.{Renk.SIFIRLA}")
                    else:
                        print(f"{Renk.SARI}Mevcut sistem promptu:{Renk.SIFIRLA}")
                        print(aktif_sistem)
                        
                elif komut == "/bilgi":
                    print(f"""
{Renk.MAVİ}━━━━━━━━ Mevcut Ayarlar ━━━━━━━━{Renk.SIFIRLA}
Model       : {Renk.KALIN}{aktif_model}{Renk.SIFIRLA}
Mesaj sayısı: {len(gecmis)}
Sistem      : {aktif_sistem[:80]}...
{Renk.MAVİ}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{Renk.SIFIRLA}""")
                    
                else:
                    print(f"{Renk.KIRMIZI}Bilinmeyen komut. /yardim yazın.{Renk.SIFIRLA}")
                    
                continue
            
            # Normal mesaj
            gecmis.append({"role": "user", "content": kullanici_girdisi})
            
            yanit = ai_yanit_al(aktif_model, gecmis, aktif_sistem)
            
            if yanit:
                gecmis.append({"role": "assistant", "content": yanit})
            else:
                gecmis.pop()  # Başarısız istek geçmişten kaldırılır
                print(f"{Renk.KIRMIZI}⚠ Yanıt alınamadı. Ollama çalışıyor mu?{Renk.SIFIRLA}")
                
        except KeyboardInterrupt:
            print(f"\n\n{Renk.SARI}Ctrl+C algılandı. Çıkmak için /cik yazın.{Renk.SIFIRLA}")
            continue
        except EOFError:
            break

def main():
    parser = argparse.ArgumentParser(
        description="Offline Yerel Yapay Zeka Asistanı",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Örnekler:
  python ai_asistan.py
  python ai_asistan.py --model llama3.1
  python ai_asistan.py --model mistral --sistem "Sen bir Python uzmanısın."
  python ai_asistan.py --yukle konusma_20241201.json
        """
    )
    
    parser.add_argument(
        "--model", "-m",
        default=None,
        help="Kullanılacak Ollama modeli (varsayılan: llama3.1)"
    )
    parser.add_argument(
        "--sistem", "-s",
        default=None,
        help="Sistem promptu (asistanın kişiliği)"
    )
    parser.add_argument(
        "--yukle", "-y",
        default=None,
        help="Önceki konuşmayı yükle (JSON dosya yolu)"
    )
    parser.add_argument(
        "--liste", "-l",
        action="store_true",
        help="Kurulu modelleri listele ve çık"
    )
    
    args = parser.parse_args()
    
    banner()
    
    # Ollama kurulu mu?
    if not ollama_kurulu_mu():
        print(f"""
{Renk.KIRMIZI}❌ Ollama kurulu değil!{Renk.SIFIRLA}

{Renk.SARI}Kurulum için:{Renk.SIFIRLA}
  🪟 Windows : https://ollama.com/download/windows adresinden indirin
  🍎 macOS   : brew install ollama
  🐧 Linux   : curl -fsSL https://ollama.com/install.sh | sh

{Renk.GRİ}Kurduktan sonra tekrar çalıştırın.{Renk.SIFIRLA}
""")
        sys.exit(1)
    
    # Ollama servisi çalışıyor mu?
    print(f"{Renk.GRİ}🔄 Ollama servisi kontrol ediliyor...{Renk.SIFIRLA}")
    if not ollama_calisiyor_mu():
        print(f"{Renk.SARI}⚡ Ollama başlatılıyor...{Renk.SIFIRLA}")
        if ollama_baslat():
            print(f"{Renk.YEŞİL}✅ Ollama başlatıldı.{Renk.SIFIRLA}")
        else:
            print(f"{Renk.KIRMIZI}❌ Ollama başlatılamadı! Manuel olarak 'ollama serve' çalıştırın.{Renk.SIFIRLA}")
            sys.exit(1)
    else:
        print(f"{Renk.YEŞİL}✅ Ollama çalışıyor.{Renk.SIFIRLA}")
    
    # Modelleri listele
    modeller = mevcut_modeller()
    
    if args.liste:
        if modeller:
            print(f"\n{Renk.YEŞİL}Kurulu modeller:{Renk.SIFIRLA}")
            for m in modeller:
                print(f"  • {m}")
        else:
            print(f"{Renk.SARI}Hiç model kurulu değil. 'ollama pull llama3.1' ile indirin.{Renk.SIFIRLA}")
        sys.exit(0)
    
    # Model seç
    if args.model:
        secili_model = args.model
    elif modeller:
        # Otomatik en iyi modeli seç
        tercih_sirasi = ["llama3.1", "llama3.2", "mistral", "qwen2.5", "gemma2", "phi3"]
        secili_model = modeller[0]  # Varsayılan: ilk kurulu
        for tercih in tercih_sirasi:
            for m in modeller:
                if tercih in m:
                    secili_model = m
                    break
    else:
        print(f"\n{Renk.SARI}⚠ Hiç model kurulu değil.{Renk.SIFIRLA}")
        print(f"Önerilen model indirilsin mi? (llama3.1 ~5GB)")
        indir_mi = input(f"{Renk.SİYAN}(e/h): {Renk.SIFIRLA}").lower()
        if indir_mi == "e":
            if model_indir("llama3.1"):
                secili_model = "llama3.1"
            else:
                print(f"{Renk.KIRMIZI}Model indirilemedi.{Renk.SIFIRLA}")
                sys.exit(1)
        else:
            secili_model = model_sec([])
    
    # Model kurulu mu kontrol et
    if secili_model not in modeller:
        print(f"\n{Renk.SARI}'{secili_model}' modeli kurulu değil.{Renk.SIFIRLA}")
        indir_mi = input(f"İndirilsin mi? (e/h): ").lower()
        if indir_mi == "e":
            if not model_indir(secili_model):
                print(f"{Renk.KIRMIZI}Model indirilemedi.{Renk.SIFIRLA}")
                sys.exit(1)
        else:
            sys.exit(0)
    
    # Sistem promptu
    varsayilan_sistem = """Sen Türkçe konuşan, son derece yetenekli ve yardımsever bir yapay zeka asistanısın.
Adın ARIA (Akıllı Robot İletişim Ajanı).

Özellikllerin:
- Türkçe ve İngilizce dahil birçok dilde akıcı iletişim kurarsın
- Kod yazma, analiz, yaratıcı yazarlık, matematik, bilim konularında uzmansın
- Dürüst, açık ve net cevaplar verirsin
- Gerektiğinde adım adım açıklama yaparsın
- Kullanıcının sorularını tam anlamıyla kavramaya çalışırsın

Her zaman yardımcı olmaya çalış, bilmediğin şeyleri dürüstçe söyle."""
    
    aktif_sistem = args.sistem if args.sistem else varsayilan_sistem
    
    # Önceki konuşmayı yükle
    gecmis = []
    if args.yukle:
        gecmis = gecmis_yukle(args.yukle)
        if gecmis:
            print(f"{Renk.YEŞİL}✅ Konuşma yüklendi: {len(gecmis)} mesaj{Renk.SIFIRLA}")
    
    # Ana döngüyü başlat
    ana_dongu(secili_model, aktif_sistem, gecmis)

if __name__ == "__main__":
    main()
