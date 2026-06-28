# TS825 Parametrik Bina Enerji Analizi

Bu proje, bina kabuğu ve HVAC seçeneklerini parametreleyerek ısıtma, soğutma ve yaşam döngüsü maliyetini birlikte değerlendiren bir mühendislik analiz aracıdır. Yalıtım kalınlığı, pencere tipi, hareketli yalıtım, kazan verimi ve klima COP değeri değiştikçe enerji tüketimi ve toplam maliyetin nasıl değiştiğini açık biçimde gösterir.

Kısa proje özeti: TS825 sınırlarını referans alan, bina performansını kabuk ve sistem tarafında birlikte inceleyen, sonuçları hem sayısal tablo hem de grafik olarak üreten parametrik bir karşılaştırma çalışmasıdır.

Önerilen proje adı: TS825 Parametrik Bina Enerji Analizi.

## Proje Ne Yapar

- Farklı yalıtım kalınlıkları için duvar ve çatı U-değerlerini hesaplar.
- Tek, çift ve üç cam seçeneklerini karşılaştırır.
- Hareketli yalıtımın ısıtma sezonundaki etkisini ayrıca değerlendirir.
- Farklı kazan verimleri ve klima COP değerleriyle HVAC senaryoları üretir.
- Isıtma ve soğutma yüklerini, yıllık enerji tüketimini ve TL bazında toplam maliyeti hesaplar.
- Sonuçları grafikler halinde `outputs/` klasörüne kaydeder.

## Veri Kaynağı ve TS825 Kullanımı

Modelde kullanılan bazı referans sınırlar ve tasarım kabulleri TS825 yaklaşımına göre tanımlanmıştır. Bu değerler doğrudan standarttan alınan ya da standardın kontrol mantığını temsil eden parametreler olarak `config.py` içinde tutulur.

TS825 ile ilişkili başlıca kullanım alanları şunlardır:

- Duvar, çatı ve pencere için maksimum U-değeri sınırları
- Bölgesel kontrol mantığı ve uygunluk karşılaştırması
- Hesaplarda kullanılan iç ve dış tasarım sıcaklıkları ile sezon oranları

Bu çalışma TS825’nin tüm metnini yeniden üretmez. Standarttaki kontrol mantığının projeye uygulanmış, sadeleştirilmiş bir mühendislik modelini verir. Uygunluk kontrolü, hesaplanan U-değerlerinin TS825 limitleriyle karşılaştırılmasıyla yapılır.

## Hesap Mantığı

Hesap akışı aşağıdaki sırayla ilerler:

1. Önce bina geometrisi çıkarılır.
2. Seçilen yalıtım kalınlığına göre ısıl direnç ve U-değerleri hesaplanır.
3. Pencere tipi ve hareketli yalıtım durumuna göre etkin pencere U-değeri belirlenir.
4. Duvar, çatı ve pencere alanları birleştirilerek toplam ısı geçiş katsayısı, yani UA bulunur.
5. Isıtma ve soğutma için sezonluk yükler hesaplanır.
6. HVAC verimleri devreye girerek yakıt ve elektrik tüketimi bulunur.
7. CAPEX ve OPEX toplanarak toplam maliyet hesaplanır.
8. Son olarak farklı kombinasyonlar sıralanır ve grafiklerle raporlanır.

## Hesapların Nasıl İşlediği

### 1. Bina geometrisi

Geometri hesapları `geometry.py` içinde yapılır. Varsayılan modelde:

- taban alanı 1000 m²
- kat yüksekliği 3 m
- pencere oranı %20

Bu bilgilerden şu alanlar türetilir:

- dış duvar toplam alanı
- pencere alanı
- opak duvar alanı
- çatı alanı
- hacim

Bu adım önemlidir, çünkü sonraki tüm ısı kaybı ve maliyet hesapları alanlara bağlıdır.

### 2. Yalıtımın ısıl direnci ve U-değeri

`thermal.py` içinde yalıtım için temel bağıntı kullanılır:

$$R_{ins} = \frac{L}{k}$$

Burada:

- $L$ yalıtım kalınlığı
- $k$ ısıl iletkenlik katsayısıdır

Toplam direnç şu şekilde kurulur:

$$R_{toplam} = R_{sabit} + R_{ins}$$

Sonra U-değeri hesaplanır:

$$U = \frac{1}{R_{toplam}}$$

Bu mantık hem duvar hem çatı için ayrı sabit yüzey dirençleriyle uygulanır.

### 3. Pencere seçimi ve hareketli yalıtım

Pencereler üç farklı seçenek olarak modellenir:

- tek cam
- çift cam
- üç cam

Hareketli yalıtım varsa, bu durum pencere direncine seri ek direnç olarak eklenir. Böylece etkin pencere U-değeri düşer.

Bu yöntem özellikle ısıtma sezonu için kullanılır. Soğutma sezonunda ise hareketli yalıtım etkisi uygulanmaz; çünkü modelde pencerenin açık ya da gölgesiz davranması varsayılır.

### 4. Toplam UA hesabı

Binanın kabuk kaybı şu şekilde hesaplanır:

$$UA_{toplam} = U_{duvar}A_{duvar} + U_{çatı}A_{çatı} + U_{pencere}A_{pencere}$$

Bu değer birim olarak W/K verir. Yani sıcaklık farkı başına ne kadar ısı kaybı olduğunu gösterir.

UA değeri yükseldikçe bina kabuğu daha fazla ısı geçirir; dolayısıyla enerji ihtiyacı artar.

### 5. Isıtma ve soğutma yükleri

Sezonluk yük hesabında temel denklem şu şekildedir:

$$Q = \frac{UA \cdot \Delta T \cdot t}{1000}$$

Burada:

- $Q$ sezonluk yük, kWh/yıl
- $UA$ toplam ısı geçiş katsayısı, W/K
- $\Delta T$ iç-dış sıcaklık farkı, K
- $t$ sezon süresi, saat

Bu modelde:

- kış için tasarım sıcaklık farkı kullanılır
- yaz için tasarım sıcaklık farkı kullanılır
- nötr sezon yükü sıfır kabul edilir

Yani bina yıl boyunca üç bölgeye ayrılmış gibi düşünülür: ısıtma dönemi, soğutma dönemi ve nötr dönem.

### 6. HVAC tüketimi

Sezonluk yükler doğrudan enerji tüketimi değildir. HVAC verimi işin içine girince tüketim belirlenir:

- kazan için:

$$E_{gaz} = \frac{Q_{ısıtma}}{\eta}$$

- klima için:

$$E_{elektrik} = \frac{Q_{soğutma}}{COP}$$

Verim veya COP yükseldikçe aynı ısıtma ve soğutma yükü için gereken enerji azalır.

### 7. Maliyet hesabı

`lcc.py` içinde CAPEX ve OPEX ayrı ayrı kurulur:

- CAPEX: ilk yatırım maliyeti
- OPEX: yıllık işletme maliyeti

CAPEX içine şu bileşenler girer:

- yalıtım maliyeti
- pencere maliyeti
- hareketli yalıtım maliyeti
- kazan maliyeti
- klima maliyeti

OPEX ise şu iki parçanın toplamıdır:

- yıllık ısıtma yakıt gideri
- yıllık soğutma elektrik gideri

Sonuçta toplam maliyet şu şekilde alınır:

$$Toplam\ Maliyet = CAPEX + OPEX$$

### 8. Sıralama mantığı

Kod iki farklı açıdan en iyi kombinasyonları seçer:

- en düşük toplam enerji tüketimi
- maliyet ve performans arasında dengeli bileşik skor

Bu sayede sadece en ucuz ya da sadece en verimli senaryo değil, iki yaklaşım birlikte değerlendirilebilir.

## Proje Dosyaları

- `main.py` - Tüm analizi çalıştıran giriş noktası
- `config.py` - Varsayılan girdiler, sınırlar ve maliyet parametreleri
- `geometry.py` - Bina geometrisi hesapları
- `thermal.py` - U-değeri, UA ve sezonluk yük hesapları
- `cases.py` - Parametrik senaryoların üretilmesi
- `lcc.py` - Yaşam döngüsü maliyeti hesabı
- `reporting.py` - Grafiklerin oluşturulması
- `outputs/` - Üretilen görseller ve analiz çıktıları

## Çıktılar

Çalıştırma sonunda `outputs/` klasöründe şu tip grafikler oluşur:

- ısıtma yükü ile yalıtım kalınlığı ilişkisi
- soğutma yükü ile yalıtım kalınlığı ilişkisi
- pencere tipine göre ısıtma yükü
- maliyet ve performans saçılım grafiği
- UA bileşen kırılımı
- kazan verimi etkisi
- klima COP etkisi
- hareketli yalıtım faydası
- HVAC akış diyagramı

## Kurulum

Python 3.10 veya daha yeni bir sürüm önerilir.

Gerekli paketler:

- `pandas`
- `numpy`
- `matplotlib`

Kurulum:

```bash
pip install -r requirements.txt
```

## Çalıştırma

```bash
python main.py
```

Program tamamlandığında analiz biter ve grafikler `outputs/` klasörüne yazılır.

## Notlar

- Üretilen grafikler versiyon kontrolüne dahil edilmez.
- Proje dış veri dosyasına ihtiyaç duymaz; tüm varsayılanlar `config.py` içindedir.
- İstenirse bir sonraki adımda README’ye Türkçe örnek sonuç ekranı ve GitHub kapak metni de eklenebilir.
