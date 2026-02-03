[readme.md](https://github.com/user-attachments/files/25053960/readme.md)
# Collatz Tabanlı Anahtar Dizisi Üreteci (CollatzRNG)

Bu proje, **Collatz sanısının matematiksel formalizasyonunu** bir “durum (state) güncelleme” mekanizması olarak kullanıp, her adımda kullanıcı tarafından tasarlanan bir **g(n) çıktı fonksiyonu** ile **byte (0–255)** üreten deterministik bir üreteç (PRNG/keystream generator) tasarlar.

> Not: Bu tasarım bir ödev/deney amaçlıdır. Kriptografik olarak güvenli olduğu iddia edilmez; güvenlik kanıtı yoktur.

---

## Temel Alınan Matematik: Collatz Dönüşümü

Collatz sanısında tanımlanan fonksiyon:

- Eğer `n` çift ise:  
  **C(n) = n / 2**
- Eğer `n` tek ise:  
  **C(n) = 3n + 1**

Bu dönüşüm tekrar tekrar uygulandığında (sanı doğru kabul edilirse) sayılar **1’e yaklaşır** ve sonunda **4 → 2 → 1** döngüsüne girer.

Bu projede Collatz, “rastgelelik kanıtı olan bir kaynak” olarak değil; **deterministik ama doğrusal olmayan bir state güncelleme fonksiyonu** olarak kullanılır.

---

## Genel Fikir: State + Output Fonksiyonu

Üreteç iki ana parçadan oluşur:

1. **State (durum):** Büyük bir tamsayı `state`
2. **g(n) fonksiyonu:** `state` üzerinden 8-bit (1 byte) çıktı üreten fonksiyon

Her iterasyonda:
- `state`’ten bir byte üretilir (anahtar dizisinin elemanı)
- Sonra `state`, Collatz adımı ile güncellenir
- `state` çok küçülürse veya 4-2-1 döngüsüne yaklaşırsa, kısa periyoda girmemesi için “tuzlama” ile tekrar büyütülür

---

## g(n) Çıktı Fonksiyonu (Byte Üretimi)

Bu projede kullanılan g(n):

- `part1 = n mod 2^16`  → `n`’nin son 16 bitini alır
- `part2 = (3n + 1) >> 4` → `3n+1` dönüşümünü de dahil edip sağa kaydırarak karıştırır
- çıktı:  
  **g(n) = (part1 XOR part2) mod 256**

Sözel amaç:
- Düşük bitleri (son 16 bit) ve `3n+1` türevini birleştirerek **miksleme (mixing)** etkisi oluşturmak
- Sonucu 8-bit’e indirerek her adımda bir byte üretmek

---

## Döngü Kırma / Kilitlenmeyi Önleme (4-2-1 Problemi)

Collatz iterasyonu, state’i çoğu zaman hızla küçültüp **4-2-1 döngüsüne** sokar. Eğer state bu döngüye girerse üreteç **kısa periyotlu** ve tekrar eden çıktı üretmeye başlar.

Bu yüzden şu kontrol yapılır:

- Eğer `state <= 4` ise state “yeniden zıplatılır”:
  - `state = (state XOR SALT) + output + 1`

Burada:
- `SALT`: sabit bir büyük sayı (tuz)
- `output`: o adımda üretilen byte (geri besleme etkisi)

Amaç:
- 4-2-1 gibi kısa döngülere kilitlenmeyi engelleyip state’i tekrar büyük değerlere taşımak
- Üreteci yeni bir Collatz yürüyüşüne sokmak

---

## Algoritma Tarifi (Pseudo-code)

**Girdi:**
- `seed` (başlangıç tohumu, pozitif tamsayı)  
  Seed verilmezse zaman tabanlı bir değer kullanılabilir.
- `L` (üretilecek byte sayısı)

**Sabit:**
- `SALT` (seçilen tuz sabiti)

**Çıktı:**
- `output[1..L]` (anahtar dizisi)

**Adımlar:**
1. `state ← seed`
2. `for i = 1..L`:
   1. `byte ← g(state)`
   2. `state ← C(state)`   // Collatz state güncellemesi
   3. `if state ≤ 4 then`
      - `state ← (state XOR SALT) + byte + 1`
   4. `output[i] ← byte`
3. `output` dizisini döndür

---

## Örnek Çıktı

Seed olarak `987654321987654321` kullanıldığında ilk 10 byte:

- Dizi:
  `[48, 151, 75, 164, 243, 249, 124, 190, 223, 158]`

- Hex:
  `30 97 4B A4 F3 F9 7C BE DF 9E`

---

## Kısıtlar / Notlar

- Üreteç deterministiktir: **Seed aynıysa çıktı aynıdır.**
- Bu çalışma bir “Collatz formalizasyonu





ALGORITHM CollatzRNG_Keystream(seed, L):
    INPUT:
        seed : positive integer
        L    : number of bytes to generate
    CONSTANT:
        SALT = 0x5A1F3C9E2B4D

    FUNCTION CollatzStep(n):
        IF n mod 2 == 0 THEN
            RETURN n / 2
        ELSE
            RETURN 3*n + 1
        ENDIF

    FUNCTION g(n):
        part1 <- n AND 0xFFFF              // last 16 bits
        part2 <- (3*n + 1) >> 4            // shift-mix
        RETURN (part1 XOR part2) AND 0xFF  // reduce to 8 bits

    state <- seed
    output <- empty list

    FOR i <- 1 TO L DO
        byte <- g(state)                  // 1) harvest 8-bit output
        state <- CollatzStep(state)       // 2) update state with Collatz

        IF state <= 4 THEN                // 3) avoid 4-2-1 loop / tiny state
            state <- (state XOR SALT) + byte + 1
        ENDIF

        APPEND byte TO output
    ENDFOR

    RETURN output
