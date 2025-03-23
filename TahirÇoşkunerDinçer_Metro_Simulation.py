from collections import defaultdict, deque
import heapq
from typing import Dict, List, Set, Tuple, Optional

class Istasyon:
    def __init__(self, idx: str, ad: str, hat: str):
        self.idx = idx
        self.ad = ad
        self.hat = hat
        self.komsular: List[Tuple['Istasyon', int]] = []  # (istasyon, süre) tuple'ları

    def komsu_ekle(self, istasyon: 'Istasyon', sure: int):
        self.komsular.append((istasyon, sure))

class MetroAgi:
    def __init__(self):
        self.istasyonlar: Dict[str, Istasyon] = {}
        self.hatlar: Dict[str, List[Istasyon]] = defaultdict(list)

    def istasyon_ekle(self, idx: str, ad: str, hat: str) -> None:
        if idx not in self.istasyonlar:           
            istasyon = Istasyon(idx, ad, hat)
            self.istasyonlar[idx] = istasyon
            self.hatlar[hat].append(istasyon)
# "id"- "idx" olarak uyguladı ki parametre ismi matchlensin.

    def baglanti_ekle(self, istasyon1_id: str, istasyon2_id: str, sure: int) -> None:
        istasyon1 = self.istasyonlar[istasyon1_id]
        istasyon2 = self.istasyonlar[istasyon2_id]
        istasyon1.komsu_ekle(istasyon2, sure)
        istasyon2.komsu_ekle(istasyon1, sure)
    
    def en_az_aktarma_bul(self, baslangic_id: str, hedef_id: str) -> Optional[List[Istasyon]]:
        """BFS algoritması kullanarak en az aktarmalı rotayı bulur"""
        if baslangic_id not in self.istasyonlar or hedef_id not in self.istasyonlar:
            return None
            
        baslangic = self.istasyonlar[baslangic_id]
        hedef = self.istasyonlar[hedef_id]
        
        # BFS algoritmasıa bir queue oluşturdum: (istasyon, rota) olarak
        kuyruk = deque([(baslangic, [baslangic])])
        ziyaret_edildi = {baslangic}
        
        while kuyruk:
            istasyon, rota = kuyruk.popleft()
            
            # Hedef istasyona vardım mı varmadım mıya baktım.
            if istasyon.idx == hedef_id:
                return rota
                
            # Komşu istasyonları kontrol ettim.
            for komsu, _ in istasyon.komsular:
                if komsu not in ziyaret_edildi:
                    ziyaret_edildi.add(komsu)
                    yeni_rota = rota + [komsu]
                    kuyruk.append((komsu, yeni_rota))
                    
        # Rota bulunamadı
        return None

    def en_hizli_rota_bul(self, baslangic_id: str, hedef_id: str) -> Optional[Tuple[List[Istasyon], int]]:
        """A* algoritması kullanarak en hızlı rotayı bulur"""
        if baslangic_id not in self.istasyonlar or hedef_id not in self.istasyonlar:
            return None

        baslangic = self.istasyonlar[baslangic_id]
        hedef = self.istasyonlar[hedef_id]
        
        # Hat değişimlerine göre heuristik hesapladım
        def heuristik(istasyon):
            # En iyi senaryoda direkt hedefe varırken hat "değişimi" yapmak durumunda mı değil miyi düşünerek, bunun gerekip gerekmediğine göre ek maliyet ekledim.
            hat_degisimi_maliyeti = 0 if istasyon.hat == hedef.hat else 2
            return hat_degisimi_maliyeti
        
        # Öncelikler adına bir kuyruk oşuşturdum: (f_skoru, istasyon_id, istasyon, rota, g_skoru)
        # f_skoru = g_skoru + h_skoru (gerçek maliyeti ve tahmini maliyetinin toplamı)
        # istasyon_id, aynı f_skoru'na sahip durumlar adına kararlı sıralama sağladı - İngilizce terminoloji kullanmak daha iyi olurdu diye düşündüm amma projeye uyumlu olması açısından kullanmadım:) -
        baslangic_f_skor = heuristik(baslangic)
        pq = [(baslangic_f_skor, id(baslangic), baslangic, [baslangic], 0)]
        
        # Tümistasyonlara en iyi g_skoru (başlangıçtan o istasyona olan en kısa yol)
        g_skorlari = {baslangic.idx: 0}
        
        while pq:
            _, _, istasyon, rota, g_skor = heapq.heappop(pq)
            
            # Hedef istasyona vardım mı varmadım mı?
            if istasyon.idx == hedef_id:
                return (rota, g_skor)
                
            # Daha önceden daha iyi bir yol varsa yolu skipledim.
            if g_skor > g_skorlari.get(istasyon.idx, float('inf')):
                continue
                
            # Komşulara baktım.
            for komsu, sure in istasyon.komsular:
                yeni_g_skor = g_skor + sure
                
                # Kıyasladım. Daha önceki yoldan daha mı kısa diye yol
                if yeni_g_skor < g_skorlari.get(komsu.idx, float('inf')):
                    g_skorlari[komsu.idx] = yeni_g_skor
                    yeni_rota = rota + [komsu]
                    
                    # A* adına biraz önce belirttiğim f_skoru = g_skoru + h_skoru
                    f_skoru = yeni_g_skor + heuristik(komsu)
                    heapq.heappush(pq, (f_skoru, id(komsu), komsu, yeni_rota, yeni_g_skor))
        
        # Bulunamadıysa none returnlendi.
        return None
    # Eğer sadece g-score(başlangıçtan beir olan konum) kullansaydım Dijkstra'ya kayabilirdi.

# Örnek Kullanım
if __name__ == "__main__":
    metro = MetroAgi()
    
    # İstasyonlar ekleme
    # Kırmızı Hat
    metro.istasyon_ekle("K1", "Kızılay", "Kırmızı Hat")
    metro.istasyon_ekle("K2", "Ulus", "Kırmızı Hat")
    metro.istasyon_ekle("K3", "Demetevler", "Kırmızı Hat")
    metro.istasyon_ekle("K4", "OSB", "Kırmızı Hat")
    
    # Mavi Hat
    metro.istasyon_ekle("M1", "AŞTİ", "Mavi Hat")
    metro.istasyon_ekle("M2", "Kızılay", "Mavi Hat")  # Aktarma noktası
    metro.istasyon_ekle("M3", "Sıhhiye", "Mavi Hat")
    metro.istasyon_ekle("M4", "Gar", "Mavi Hat")
    
    # Turuncu Hat
    metro.istasyon_ekle("T1", "Batıkent", "Turuncu Hat")
    metro.istasyon_ekle("T2", "Demetevler", "Turuncu Hat")  # Aktarma noktası
    metro.istasyon_ekle("T3", "Gar", "Turuncu Hat")  # Aktarma noktası
    metro.istasyon_ekle("T4", "Keçiören", "Turuncu Hat")
    
    # Bağlantılar ekleme
    # Kırmızı Hat bağlantıları
    metro.baglanti_ekle("K1", "K2", 4)  # Kızılay -> Ulus
    metro.baglanti_ekle("K2", "K3", 6)  # Ulus -> Demetevler
    metro.baglanti_ekle("K3", "K4", 8)  # Demetevler -> OSB
    
    # Mavi Hat bağlantıları
    metro.baglanti_ekle("M1", "M2", 5)  # AŞTİ -> Kızılay
    metro.baglanti_ekle("M2", "M3", 3)  # Kızılay -> Sıhhiye
    metro.baglanti_ekle("M3", "M4", 4)  # Sıhhiye -> Gar
    
    # Turuncu Hat bağlantıları
    metro.baglanti_ekle("T1", "T2", 7)  # Batıkent -> Demetevler
    metro.baglanti_ekle("T2", "T3", 9)  # Demetevler -> Gar
    metro.baglanti_ekle("T3", "T4", 5)  # Gar -> Keçiören
    
    # Hat aktarma bağlantıları (aynı istasyon farklı hatlar)
    metro.baglanti_ekle("K1", "M2", 2)  # Kızılay aktarma
    metro.baglanti_ekle("K3", "T2", 3)  # Demetevler aktarma
    metro.baglanti_ekle("M4", "T3", 2)  # Gar aktarma
    
    # Test senaryoları
    print("\n=== Test Senaryoları ===")
    
    # Senaryo 1: AŞTİ'den OSB'ye
    print("\n1. AŞTİ'den OSB'ye:")
    rota = metro.en_az_aktarma_bul("M1", "K4")
    if rota:
        print("En az aktarmalı rota:", " -> ".join(i.ad for i in rota))
    
    sonuc = metro.en_hizli_rota_bul("M1", "K4")
    if sonuc:
        rota, sure = sonuc
        print(f"En hızlı rota ({sure} dakika):", " -> ".join(i.ad for i in rota))
    
    # Senaryo 2: Batıkent'ten Keçiören'e
    print("\n2. Batıkent'ten Keçiören'e:")
    rota = metro.en_az_aktarma_bul("T1", "T4")
    if rota:
        print("En az aktarmalı rota:", " -> ".join(i.ad for i in rota))
    
    sonuc = metro.en_hizli_rota_bul("T1", "T4")
    if sonuc:
        rota, sure = sonuc
        print(f"En hızlı rota ({sure} dakika):", " -> ".join(i.ad for i in rota))
    
    # Senaryo 3: Keçiören'den AŞTİ'ye
    print("\n3. Keçiören'den AŞTİ'ye:")
    rota = metro.en_az_aktarma_bul("T4", "M1")
    if rota:
        print("En az aktarmalı rota:", " -> ".join(i.ad for i in rota))
    
    sonuc = metro.en_hizli_rota_bul("T4", "M1")
    if sonuc:
        rota, sure = sonuc
        print(f"En hızlı rota ({sure} dakika):", " -> ".join(i.ad for i in rota))
