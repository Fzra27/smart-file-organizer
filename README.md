# Derli — Akıllı Dosya Düzenleyici

Türkçe ve Almanca arayüzlü, bilgisayarında çalışan dosya düzenleme uygulaması. Dosya işlemleri Python standart kütüphanesiyle çalışır; masaüstü penceresi GTK/WebKit sistem paketlerini kullanır. Hesap gerekmez. İlk kurulumdan sonra internet bağlantısı gerektirmez.

## Ubuntu masaüstü sürümü (v1.2)

Uygulama varsayılan olarak **kendi GTK/WebKit penceresinde**, **koyu temayla** açılır. Normal başlangıçta tarayıcı açılmaz. Türkçe ve Almanca seçenekleri korunur.

Bir defalık kurulum, uygulama klasöründe:

```sh
sh Kur-Ubuntu.sh
```

Bu komut Ubuntu paket yöneticisinden `python3`, `python3-gi`, `gir1.2-gtk-3.0` ve `gir1.2-webkit2-4.1` yükler; kullanıcı hesabının Uygulamalar menüsüne **Derli** kısayolu ekler. Paket kurulumu için sudo parolan istenir. Kurulum internet gerektirir; normal kullanım yereldir. Uygulama klasörünü taşırsan menü kısayolunu güncellemek için `python3 install_desktop.py` çalıştır.

Ardından Uygulamalar menüsünden **Derli** aç veya terminalde:

```sh
sh Baslat.sh
```

Pencereyi kapatınca yerel sunucu ve otomatik düzenleme sona erer. Önceki tarayıcı sürümü terminalde hâlâ çalışıyorsa **Ctrl+C** ile durdur. Port doluysa `sh Baslat.sh --port 0` kullanılabilir; bu durumda uygulama boş bir port seçer. Dil tercihi kullanılan yerel adrese göre saklanır.

Python 3.10+ gerekir. Linux başlatıcısı Ubuntu'nun GI paketleriyle uyumlu olan `/usr/bin/python3` kullanır. Windows/macOS için GTK kurulumu bu sürümde sağlanmaz; açıkça istenirse `python app.py --browser` ile web arayüzü kullanılabilir.

### İsteğe bağlı sunucu / tarayıcı modu

```sh
python3 app.py --folder "/tam/yol/Downloads"
python3 app.py --no-browser
python3 app.py --browser
```

`--no-browser` yalnızca yerel sunucuyu başlatır, `--browser` açıkça web tarayıcısı ister. Sunucu modunda adres `http://127.0.0.1:8765`, durdurma **Ctrl+C**. Varsayılan başlangıç masaüstü penceresidir. Masaüstü bileşenleri eksikse kurulum komutu gösterilir; kendiliğinden tarayıcıya geçilmez.

Ubuntu'nun `~/.config/user-dirs.dirs` dosyasındaki `XDG_DOWNLOAD_DIR` ayarı okunur. `XDG_CONFIG_HOME` desteklenir. Ayar yoksa `~/Downloads` önerilir; tam yolu elle değiştirebilirsin.

## Ne işe yarar?

1. **Düzenler:** Ana klasördeki `fatura.pdf` dosyasını `Belgeler/`, `foto.jpg` dosyasını `Görseller/` klasörüne taşır. Alt klasörlerini yeniden düzenlemez. Önizlemeden sonra onay verirsin.
2. **Kopyaları bulur:** Dosya isimleri farklı olsa da tüm içeriklerin SHA-256 özetlerini karşılaştırır. Her grupta en eski kopya korunur, diğerleri onayınla karantinaya taşınır. Geri alma geçmişten yapılır.
3. **Alanı analiz eder:** En büyük dosyaları, dosya türlerinin toplam boyutunu ve diskteki gerçek boş alanı gösterir.

**Karantina alan boşaltmaz.** Uygulama kalıcı silme yapmaz. Alan kazanmak için karantinadaki kopyaları kontrol edip kendin silmelisin. Otomatik mod başlangıçta kapalıdır; açarsan yalnızca uygulama çalışırken her 15 saniyede ana klasörü düzenler. Bilgisayar açılışında kendi kendine çalışmaz.

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

Proje ek bağımlılık gerektirmez. `app.py` dosya işlemlerini ve yerel sunucuyu, `desktop.py` GTK/WebKit penceresini, `static/` arayüzü içerir. GitHub'a kaynak olarak aktarılmaya hazırdır; uygulama GitHub hesabına erişmez.

```sh
python3 -m unittest -v
node --check static/app.js
node --check static/i18n.js
```

Testler: önizleme, dosya adı çakışmaları, geri alma, SHA-256 ile kopya tespiti, karantina, değişen dosyalar, korunan kopyanın doğrulanması, sembolik bağlantılar, otomatik mod, yerel API oturumu, XDG indirme klasörü ve Linux başlatıcısı. Testler geçici klasörlerde çalışır.

## v1.2 doğrulaması

GTK/WebKit penceresi Ubuntu 24.04 konteynerinde yönetici olmayan kullanıcı ve sanal ekranla açılarak test edildi: koyu arka plan, açıklama bölümü ve Almanca geçişi doğrulandı. Masaüstünde varsayılan tarayıcı kullanılmadığı kontrol edildi. 13 otomatik kontrol Debian ortamında geçti; dosya işlemleri ve arayüzün TR/DE akışları da doğrulandı. Donanım hızlandırması ve Ubuntu masaüstü menüsü gerçek kullanıcı cihazında ayrıca denenmelidir.
