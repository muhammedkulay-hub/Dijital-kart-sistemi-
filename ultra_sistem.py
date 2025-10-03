#!/data/data/com.termux/files/usr/bin/python3
import json
import hashlib
import os
from datetime import datetime, timedelta
import random

class UltraSistem:
    def __init__(self):
        self.kartlar = {}
        self.paylasimlar = {}
        self.acil_durum = False
        self.harcama_gecmisi = []
        self.dosya = "ultra_veri.json"
        self.yukle()
    
    def yukle(self):
        if os.path.exists(self.dosya):
            with open(self.dosya, 'r') as f:
                data = json.load(f)
                self.kartlar = data.get("kartlar", {})
                self.paylasimlar = data.get("paylasimlar", {})
                self.acil_durum = data.get("acil_durum", False)
                self.harcama_gecmisi = data.get("harcama_gecmisi", [])
    
    def kaydet(self):
        with open(self.dosya, 'w') as f:
            json.dump({
                "kartlar": self.kartlar,
                "paylasimlar": self.paylasimlar,
                "acil_durum": self.acil_durum,
                "harcama_gecmisi": self.harcama_gecmisi
            }, f)
    
    def kart_ekle(self, ad, no):
        if self.acil_durum:
            print("🚨 ACİL DURUM: Kart eklenemez!")
            return None
            
        kart_id = hashlib.md5(no.encode()).hexdigest()[:8]
        self.kartlar[kart_id] = {
            "ad": ad, "no": no, "durum": "pasif",
            "limit_gunluk": 1000, "limit_tek": 500,
            "olusturulma": datetime.now().isoformat()
        }
        self.kaydet()
        print(f"✅ {ad} eklendi! ID: {kart_id}")
        return kart_id
    
    def kart_degistir(self, kart_id):
        if self.acil_durum:
            print("🚨 ACİL DURUM: Kart değiştirilemez!")
            return False
            
        if kart_id in self.kartlar:
            for kid in self.kartlar:
                self.kartlar[kid]["durum"] = "pasif"
            self.kartlar[kart_id]["durum"] = "aktif"
            self.kaydet()
            print(f"🔄 Aktif: {self.kartlar[kart_id]['ad']}")
            return True
        print("❌ Kart yok!")
        return False
    
    def kart_sil(self, kart_id):
        if kart_id in self.kartlar:
            ad = self.kartlar[kart_id]["ad"]
            del self.kartlar[kart_id]
            self.kaydet()
            print(f"🗑️ Silindi: {ad}")
            return True
        print("❌ Kart yok!")
        return False
    
    def acil_durum_aktif(self):
        self.acil_durum = True
        for kid in self.kartlar:
            self.kartlar[kid]["durum"] = "bloke"
        self.kaydet()
        print("🚨 ACİL DURUM AKTİF! Tüm kartlar BLOKE!")
    
    def acil_durum_kapat(self):
        self.acil_durum = False
        self.kaydet()
        print("✅ Acil durum kapatıldı")
    
    def paylasim_olustur(self, kart_id, alici, sure, limit):
        if kart_id not in self.kartlar:
            print("❌ Kart yok!")
            return None
            
        paylasim_id = hashlib.md5(f"{kart_id}{alici}".encode()).hexdigest()[:6]
        self.paylasimlar[paylasim_id] = {
            "kart_id": kart_id,
            "alici": alici,
            "baslangic": datetime.now().isoformat(),
            "bitis": (datetime.now() + timedelta(hours=sure)).isoformat(),
            "limit": limit,
            "kullanilan": 0,
            "durum": "aktif"
        }
        self.kaydet()
        print(f"🎁 {alici} için paylaşım oluşturuldu! ID: {paylasim_id}")
        return paylasim_id
    
    def akilli_kart_sec(self, mekan_tipi):
        mekan_kartlari = {
            "market": ["kredi", "bank"],
            "akaryakit": ["hadi", "kredi"],
            "online": ["bank", "kredi"],
            "restoran": ["kredi", "hadi"]
        }
        
        if mekan_tipi in mekan_kartlari:
            for kart_tipi in mekan_kartlari[mekan_tipi]:
                for kid, kart in self.kartlar.items():
                    if kart_tipi in kart["ad"].lower():
                        self.kart_degistir(kid)
                        print(f"🤖 Akıllı seçim: {kart['ad']} ({mekan_tipi})")
                        return True
        print("❌ Uygun kart bulunamadı")
        return False
    
    def harcama_ekle(self, tutar, mekan):
        aktif_kart = None
        for kid, kart in self.kartlar.items():
            if kart["durum"] == "aktif":
                aktif_kart = kart
                break
        
        if aktif_kart:
            self.harcama_gecmisi.append({
                "tarih": datetime.now().isoformat(),
                "kart": aktif_kart["ad"],
                "tutar": tutar,
                "mekan": mekan
            })
            self.kaydet()
            print(f"💰 Harcama kaydedildi: {tutar}TL - {mekan}")
    
    def rapor_goster(self):
        print("\n📊 HARCAMA RAPORU")
        print("=" * 30)
        
        toplam = 0
        kart_toplam = {}
        
        for harcama in self.harcama_gecmisi[-10:]:  # Son 10 harcama
            tarih = datetime.fromisoformat(harcama["tarih"]).strftime("%d.%m %H:%M")
            print(f"📅 {tarih} - {harcama['kart']} - {harcama['tutar']}TL - {harcama['mekan']}")
            toplam += harcama["tutar"]
            
            if harcama["kart"] in kart_toplam:
                kart_toplam[harcama["kart"]] += harcama["tutar"]
            else:
                kart_toplam[harcama["kart"]] = harcama["tutar"]
        
        print(f"\n💰 TOPLAM: {toplam}TL")
        for kart, tutar in kart_toplam.items():
            print(f"  {kart}: {tutar}TL")
    
    def sesli_komut(self, komut):
        komut = komut.lower()
        
        if "acil durum" in komut or "bloke" in komut:
            self.acil_durum_aktif()
            return "🚨 Acil durum aktif!"
        
        elif "rapor" in komut or "harcama" in komut:
            self.rapor_goster()
            return "📊 Rapor gösteriliyor"
        
        elif "market" in komut:
            self.akilli_kart_sec("market")
            return "🛒 Market için kart seçildi"
        
        elif "akaryakıt" in komut or "benzin" in komut:
            self.akilli_kart_sec("akaryakit")
            return "⛽ Akaryakıt için kart seçildi"
        
        else:
            for kid, kart in self.kartlar.items():
                if kart["ad"].lower() in komut:
                    self.kart_degistir(kid)
                    return f"🔄 {kart['ad']} aktif edildi"
            
            return "❌ Anlayamadım"
    
    def listele(self):
        print("\n📋 KARTLAR:")
        for kid, kart in self.kartlar.items():
            if self.acil_durum:
                durum = "🔴 BLOKE"
            else:
                durum = "🟢" if kart["durum"] == "aktif" else "⚫"
            print(f"  {durum} {kart['ad']} ({kid})")
        
        print("\n👥 PAYLAŞIMLAR:")
        for pid, paylas in self.paylasimlar.items():
            if datetime.now() < datetime.fromisoformat(paylas["bitis"]):
                kart_adi = self.kartlar[paylas["kart_id"]]["ad"]
                print(f"  📤 {paylas['alici']} → {kart_adi} ({paylas['limit']}TL)")

# Ana sistem
sistem = UltraSistem()

while True:
    print("\n" + "="*50)
    print("🚀 ULTRA KART SİSTEMİ")
    if sistem.acil_durum:
        print("🚨 🚨 🚨 ACİL DURUM AKTİF 🚨 🚨 🚨")
    print("="*50)
    
    sistem.listele()
    
    print("\n1- Kart Ekle")
    print("2- Kart Değiştir")
    print("3- Kart Sil")
    print("4- Paylaşım Oluştur")
    print("5- Akıllı Kart Seç")
    print("6- Harcama Ekle")
    print("7- Rapor Göster")
    print("8- Sesli Komut")
    print("9- Acil Durum Aç/Kapat")
    print("0- Çıkış")
    
    sec = input("\nSeçim: ")
    
    if sec == "1":
        ad = input("Kart adı: ")
        no = input("Kart no: ")
        sistem.kart_ekle(ad, no)
    
    elif sec == "2":
        kid = input("Kart ID: ")
        sistem.kart_degistir(kid)
    
    elif sec == "3":
        kid = input("Silinecek Kart ID: ")
        sistem.kart_sil(kid)
    
    elif sec == "4":
        kid = input("Paylaşılacak Kart ID: ")
        alici = input("Alıcı adı: ")
        sure = int(input("Süre (saat): "))
        limit = int(input("Limit (TL): "))
        sistem.paylasim_olustur(kid, alici, sure, limit)
    
    elif sec == "5":
        print("Mekan tipleri: market, akaryakit, online, restoran")
        mekan = input("Mekan tipi: ")
        sistem.akilli_kart_sec(mekan)
    
    elif sec == "6":
        tutar = int(input("Tutar (TL): "))
        mekan = input("Mekan: ")
        sistem.harcama_ekle(tutar, mekan)
    
    elif sec == "7":
        sistem.rapor_goster()
    
    elif sec == "8":
        komut = input("Sesli komut: ")
        sonuc = sistem.sesli_komut(komut)
        print(sonuc)
    
    elif sec == "9":
        if sistem.acil_durum:
            sistem.acil_durum_kapat()
        else:
            sistem.acil_durum_aktif()
    
    elif sec == "0":
        print("👋 Güle güle!")
        break

    input("\nDevam etmek için Enter...")

