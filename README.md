# Derli — Akıllı Dosya Düzenleyici

Türkçe ve Almanca arayüzlü, bilgisayarında çalışan dosya düzenleme uygulaması. Python standart kütüphanesiyle yazılmıştır; ek paket, hesap veya internet bağlantısı gerektirmez. Arayüz yerel tarayıcıda açılır.

## Başlatma

Python **3.10 veya üzeri** gerekir. ZIP veya Linux için hazırlanan `.tar.gz` paketini bir klasöre çıkar.

### Ubuntu / Linux

Uygulama klasöründe terminal aç ve çalıştır:

```sh
sh Baslat.sh
```

Python kurulu değilse önce `sudo apt install python3` kullan. Uygulamayı **sudo olmadan**, kendi kullanıcı hesabınla çalıştır. Başlatıcı tarayıcıyı otomatik açar. Grafik arayüz bulunmayan sistemlerde `sh Baslat.sh --no-browser` kullanabilirsin; arayüze aynı bilgisayardan `http://127.0.0.1:8765` adresiyle erişilir.

Ubuntu'nun `~/.config/user-dirs.dirs` dosyasındaki `XDG_DOWNLOAD_DIR` ayarı okunur. Böylece İndirilenler, Downloads veya başka bir ada sahip indirme klasörünün yolu otomatik önerilir. `XDG_CONFIG_HOME` desteklenir. Ayar yoksa `~/Downloads` önerilir; tam yolu elle değiştirebilirsin.

### Diğer sistemler

- **Windows:** `Baslat.bat` dosyasına çift tıkla. Python yüklü değilse önce python.org üzerinden yükle.
- **macOS / Linux:** Terminalde uygulama klasörüne geç ve `python3 app.py` çalıştır. macOS'ta `Baslat.command` da kullanılabilir; gerekirse önce `chmod +x Baslat.command` çalıştır.
- Tarayıcı açılmazsa `http://127.0.0.1:8765` adresine git.
- Kapatmak için terminalde **Ctrl+C** kullan. Tarayıcı sekmesini kapatmak sunucuyu durdurmaz.

```sh
python3 app.py --folder "/tam/yol/Downloads"
python3 app.py --port 8766
python3 app.py --no-browser
```

Windows terminalinde `python3` yerine `py -3` veya `python` kullanılabilir. Program Ubuntu 24.04 konteynerinde Python 3.12 ile, yönetici olmayan kullanıcı altında 11 otomatik testten geçirilmiştir. Başlatıcının yerel sunucuyu açması ve dil dosyalarını sunması test edilmiştir. Türkçe/Almanca arayüz ve mobil görünüm ayrıca Debian üzerinde Chromium ile kontrol edilmiştir. Ubuntu masaüstünde tarayıcının otomatik açılması ve Windows/macOS üzerinde doğrudan test yapılmamıştır.

## Dil seçimi

Sağ üstteki **Dil / Sprache** menüsünden **Türkçe** veya **Deutsch** seç. Seçim tarayıcıda saklanır ve aynı yerel adres tekrar açıldığında hatırlanır. Menü, dosya kategorileri, önizlemeler, sonuçlar, uygulama hata mesajları, işlem geçmişi, tarih ve sayı biçimleri seçilen dile göre gösterilir. İşletim sisteminin teknik hata açıklamaları özgün biçimde kalabilir.

Dosyaların gerçek adları ve yolları çevrilmez. Düzenleme hedefleri iki dilde de aynı klasör adlarını kullanır (ör. `Belgeler`, `Görseller`); dil değiştirmek dosyaları yeniden taşımaz.

## Kullanım

1. İndirilenler klasörünün **tam yolunu** gir ve **Klasörü aç** düğmesine bas. İlk tarama hiçbir dosyayı değiştirmez. Windows örneği: `C:\Users\Adın\Downloads`; macOS örneği: `/Users/ad/Downloads`.
2. **Düzenlemeyi önizle** ile taşınacak dosyaları incele. **Onayla ve taşı** ile uygula.
3. **Aynı dosyalar** bölümünde içerik bakımından eş dosyaları gör. **Karantinayı önizle** ile her grubun en eski kopyası korunarak diğerlerinin karantinaya taşınmasını incele.
4. **İşlem geçmişi** bölümünden taşıma işlemlerini geri al. İlk konumda başka bir dosya varsa üzerine yazılmaz; ilgili kayıt atlanır.
5. İstersen **Otomatik düzenle** anahtarını aç. Program çalışırken her 15 saniyede ana klasördeki dosyalar türlerine göre düzenlenir. Uygulama tekrar açıldığında otomatik mod kapalıdır; işletim sistemi başlangıcında otomatik çalıştırma kurulmaz.

## Düzenleme kuralları

- Ana klasördeki dosyalar Belgeler, Görseller, Videolar, Müzikler, Arşivler, Uygulamalar, Kod ve Diğer klasörlerine taşınır. Mevcut alt klasörler yeniden düzenlenmez.
- Alan analizi ve kopya taraması alt klasörleri de kapsar. Gizli dosya/klasörler, sembolik bağlantılar ve `.part`, `.crdownload`, `.download`, `.tmp`, `.temp` dosyaları işlenmez.
- Son 10 saniyede değişmiş dosyalar düzenlenmez. Dosyaları yazan diğer uygulamaları kapatmak, özellikle büyük kopyalama işlemlerinde daha güvenilir sonuç verir.
- Aynı isimde hedef varsa `(1)`, `(2)` gibi ekler kullanılır. Taşıma mevcut hedefin üzerine yazmaz. Taşıma için aynı dosya sisteminde hard link desteği gerekir; desteklenmeyen dosya sistemlerinde işlem hata verir ve kaynak yerinde kalır. Harici disk bağlama noktaları arasındaki taşıma desteklenmez.
- Kopyalar önce dosya boyutuna, ardından tüm içeriğin SHA-256 özetine göre karşılaştırılır. Taşımadan önce içerik ve korunacak kopya yeniden doğrulanır. Büyük klasörlerde ilk tarama zaman alabilir; SHA-256 için tüm aday dosyalar okunur.
- Önizleme 5 dakika geçerlidir. Önizlemeden sonra değişen kaynak dosyalar atlanır. Açık bir manuel önizleme varken otomatik düzenleme bekler.

## Karantina ve alan kazanımı

Kopyalar seçilen klasörün içindeki **`.akilli-duzenleyici/karantina`** dizinine taşınır. **Karantinaya taşıma disk alanını boşaltmaz.** Arayüzdeki “Geri kazanılabilir alan”, fazla kopyaların toplam boyutudur. Dosyaları kontrol ettikten sonra karantina klasörünü işletim sisteminden kendin silebilirsin. Kalıcı silme sonrasında ilgili dosyalar uygulamadan geri alınamaz.

İşlem kayıtları `.akilli-duzenleyici/history` altında JSON olarak saklanır. Geri alma için bu kayıtları koru. Program diskteki dosyaları ve kayıtları yeni açılışta yeniden okuyabilir; daha önce düzenlediğin klasör yolunu tekrar gir. Gizli karantina klasörü analiz toplamına dahil edilmez; disk boş alanı tüm diskin gerçek boş alanını gösterir.

## Yerel erişim

Sunucu yalnızca `127.0.0.1` üzerinde dinler. Değişiklik istekleri her açılışta üretilen oturum anahtarıyla ve Host doğrulamasıyla korunur. Telemetri, harici font veya buluta dosya yükleme yoktur. Kullanıcı hesabının okuyup yazabildiği klasörlerde çalışır.

## Geliştirme / GitHub

Proje ek bağımlılık gerektirmez. `app.py` dosya işlemlerini ve HTTP sunucusunu, `static/` arayüzü içerir. GitHub'a kaynak olarak aktarılmaya hazırdır; uygulama GitHub hesabına erişmez.

```sh
python3 -m unittest -v
node --check static/app.js
node --check static/i18n.js
```

Testler: önizleme, dosya adı çakışmaları, geri alma, SHA-256 ile kopya tespiti, karantina, değişen dosyalar, korunan kopyanın doğrulanması, sembolik bağlantılar, otomatik mod, yerel API oturumu, XDG indirme klasörü ve Linux başlatıcısı. Testler geçici klasörlerde çalışır.
