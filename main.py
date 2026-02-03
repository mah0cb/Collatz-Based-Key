import time
import matplotlib.pyplot as plt

class CollatzRNG:
    def __init__(self, seed=None):
        if seed is None:
            # Seed yoksa zamanı kullan (basit başlangıç)
            self.state = int(time.time() * 1000)
        else:
            self.state = seed

        # 1'e ulaşıldığında döngüyü kırmak için kullanılan "Tuz" sabiti
        self.SALT = 0x5A1F3C9E2B4D

    def _collatz_step(self, n):
        """Matematiksel C(n) fonksiyonu"""
        if n % 2 == 0:
            return n // 2
        else:
            return 3 * n + 1

    def _g_function(self, n):
        """
        Tasarlanan g(n) fonksiyonu.
        n'den 8 bitlik (1 byte) rastgelelik çıkarır.
        Formül: ( (n mod 2^16) XOR ((3n+1) >> 4) ) mod 256
        """
        # 1. Parça: Sayının son 16 biti
        part1 = n & 0xFFFF

        # 2. Parça: Sayısal dönüşüm ve bit kaydırma (Mixing)
        part2 = (3 * n + 1) >> 4

        # XOR ile karıştırma ve 8 bite indirme
        result = (part1 ^ part2) & 0xFF
        return result

    def next_byte(self):
        """Bir sonraki rastgele byte'ı üretir."""
        # 1. Mevcut durumdan entropy (rastgelelik) hasat et
        output = self._g_function(self.state)

        # 2. Collatz adımını uygula (State update)
        self.state = self._collatz_step(self.state)

        # 3. Kilitlenme (Loop) Kontrolü
        # Collatz 4-2-1 döngüsüne girerse veya sayı çok küçülürse
        if self.state <= 4:
            # Durumu tuzla karıştırıp yukarı fırlat
            self.state = (self.state ^ self.SALT) + output + 1

        return output

    def next_bytes(self, length):
        """Belirtilen uzunlukta byte dizisi üretir."""
        return [self.next_byte() for _ in range(length)]


# --- TEST ---
# Üreteci başlat (Büyük bir asal sayı seed olarak verilebilir)
rng = CollatzRNG(seed=987654321987654321)

# 10 adet rastgele sayı üret
random_sequence = rng.next_bytes(10)

print("Üretilen Rastgele Dizi (Anahtar):")
print(random_sequence)
print("\nHex Formatında:")
print(" ".join(f"{x:02X}" for x in random_sequence))

# Dağılım kontrolü (Basitçe görselleştirmek için)
print("\n100 Sayılık Örnek Dağılım:")


data = rng.next_bytes(100)
print(data[:20], "...")  # İlk 20 tanesini göster