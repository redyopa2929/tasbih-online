# Tasbih Online — Penghitung Dzikir Digital di Terminal (Python)

**Tasbih online** ini adalah tasbih digital sederhana untuk terminal: tekan Enter untuk menambah hitungan, lalu aplikasi memberi tanda saat target 33, 99, atau 100 tercapai. Ada preset **dzikir setelah shalat 33 kali** (tasbih, tahmid, takbir, lalu tahlil hingga genap 100), lengkap dengan teks Arab, latin, dan artinya. Riwayat harian tersimpan di komputer Anda sendiri. Jadi Anda tidak perlu menghitung di kepala dan bisa tetap fokus pada bacaan.

> 🛠️ Tool gratis & open source ini adalah karya **[JoinBareng](https://joinbareng.com)** — platform patungan langganan premium di Indonesia.

## Daftar Isi

- [Apa Itu Tasbih Online Ini](#apa-itu-tasbih-online-ini)
- [Fitur Utama](#fitur-utama)
- [Cara Install dan Menjalankan](#cara-install-dan-menjalankan)
- [Cara Pakai dan Contoh Output Asli](#cara-pakai-dan-contoh-output-asli)
- [Dzikir Setelah Shalat dan Dalilnya](#dzikir-setelah-shalat-dan-dalilnya)
- [Cara Menghitung Putaran Secara Manual](#cara-menghitung-putaran-secara-manual)
- [Tabel Referensi Bacaan Dzikir](#tabel-referensi-bacaan-dzikir)
- [Tasbih Fisik vs Tasbih Digital](#tasbih-fisik-vs-tasbih-digital)
- [Privasi Data Anda](#privasi-data-anda)
- [Tips dan Kesalahan Umum](#tips-dan-kesalahan-umum)
- [FAQ](#faq)
- [Metodologi Pengujian dan Sumber](#metodologi-pengujian-dan-sumber)
- [Tentang Pembuat](#tentang-pembuat)
- [Disclaimer](#disclaimer)
- [Kontribusi](#kontribusi)
- [Lisensi](#lisensi)
- [Dukung Proyek Ini](#dukung-proyek-ini)
- [Tools Lainnya dari Seri Ini](#tools-lainnya-dari-seri-ini)

## Apa Itu Tasbih Online Ini

Banyak orang mencari "tasbih online" karena ingin menghitung dzikir tanpa membawa butiran tasbih dan tanpa iklan aplikasi ponsel. Proyek ini menjawabnya dengan cara paling ringan: satu berkas Python, tanpa pustaka tambahan, dan bisa jalan di Windows, macOS, maupun Linux.

Walaupun namanya tasbih online, aplikasinya justru berjalan **tanpa internet**. Kata "online" kami pakai karena itulah istilah yang dicari orang saat butuh penghitung dzikir di perangkat digital. Setelah diunduh, tasbih online ini bisa dipakai di laptop kantor atau komputer masjid yang punya Python 3.8 ke atas.

Cara kerjanya mirip counter dzikir genggam: setiap Enter menambah satu. Saat target tercapai, terminal membunyikan bel (karakter `\a`), menampilkan pesan, dan mencatat sudah berapa **putaran** selesai, misalnya tiga kali 33.

## Fitur Utama

Berikut kemampuan tasbih online ini:

- **Hitung dzikir dengan Enter.** Tidak memakai `curses` atau `getch`, sehingga perilakunya sama di semua sistem operasi.
- **Perintah singkat:** `u` = undo, `r` = reset (dengan konfirmasi), `t` = ganti target, `q` = selesai dan simpan.
- **Target fleksibel:** 33, 99, 100, atau angka lain hingga 1.000.000.
- **Bel dan pesan** saat target tercapai, plus penanda putaran (berapa kali 33).
- **Preset dzikir setelah shalat:** Subḥānallāh 33×, Alḥamdulillāh 33×, Allāhu akbar 33×, lalu tahlil penutup hingga genap 100.
- **Varian 34 takbir** (33 + 33 + 34) sesuai riwayat Ka‘b bin ‘Ujrah.
- **Daftar dzikir singkat** dengan teks Arab berharakat, latin, dan arti: tasbih, tahmid, takbir, tahlil, istighfar, dan shalawat.
- **Riwayat lokal** dalam berkas JSON, dicatat per tanggal dan per dzikir. Perintah `--riwayat` menampilkan ringkasan hari ini, 7 hari terakhir, dan total.
- **Kode terbuka**, hanya memakai standard library, dan diuji dengan 22 unit test.

## Cara Install dan Menjalankan

Pastikan Python 3.8 atau yang lebih baru sudah terpasang. Cek dengan `python3 --version`. Pengguna Windows biasanya memakai perintah `python` atau `py`.

```bash
git clone https://github.com/redyopa2929/tasbih-online.git
cd tasbih-online
python3 tasbih.py
```

Tanpa argumen, aplikasi membuka menu interaktif dalam Bahasa Indonesia. Bantuan lengkap bisa dilihat dengan `python3 tasbih.py -h`. Tidak ada `pip install` yang perlu dijalankan.

## Cara Pakai dan Contoh Output Asli

Semua output di bawah ini disalin apa adanya dari aplikasi. Ketukan Enter disimulasikan lewat `printf` (pipe), sehingga prompt `>` tampil menempel dengan status. Saat dipakai langsung di terminal, setiap Enter membuat baris baru.

### Menu interaktif

```text
$ python3 tasbih.py
=== Tasbih Online v1.0.0 — penghitung dzikir di terminal ===
1. Hitung dzikir bebas (pilih dzikir & target)
2. Dzikir setelah shalat: 33 tasbih, 33 tahmid, 33 takbir + tahlil = 100
3. Dzikir setelah shalat varian 34 takbir (33 + 33 + 34)
4. Daftar dzikir singkat
5. Lihat riwayat
0. Keluar
Pilih [1]:
```

### Hitung dzikir bebas dengan target

Contoh ini memakai target 3 agar singkat. Masukannya: empat kali Enter, satu kali `u`, lalu `q`.

```text
$ printf "\n\n\n\nu\nq\n" | python3 tasbih.py --target 3 --file riwayat-demo.json

== Tasbih | target 3 ==
  سُبْحَانَ اللَّهِ
  Subḥānallāh
  Artinya: "Mahasuci Allah"
Enter = +1 | u = undo | r = reset | t = ganti target | q = selesai & simpan
>   1/3 | putaran 0 | total 1
>   2/3 | putaran 0 | total 2
>   ** Target 3 tercapai — putaran ke-1. Lanjutkan (Enter) atau q untuk selesai.
  3/3 | putaran 1 | total 3
>   1/3 | putaran 1 | total 4
>   3/3 | putaran 1 | total 3
> Selesai: Tasbih 3 kali.
Tersimpan ke riwayat-demo.json: Tasbih +3
```

Untuk dzikir lain, pakai `--dzikir`, misalnya `python3 tasbih.py --dzikir istighfar --target 100`.

### Preset dzikir setelah shalat 33 kali

Perintah `--shalat` menjalankan urutan 33-33-33 ditambah satu tahlil penutup. Output 100 ketukan di bawah ini dipotong pada bagian `...`; sisanya asli.

```text
$ python3 tasbih.py --shalat --file riwayat-demo.json

== Dzikir setelah shalat | total 100 ==
Tasbih 33x -> Tahmid 33x -> Takbir 33x -> Tahlil penutup 1x
Enter = +1 | u = undo | r = reset | q = selesai & simpan

[1/4] Tasbih 33x
  سُبْحَانَ اللَّهِ
  Subḥānallāh
  Artinya: "Mahasuci Allah"
>   [1/4] Subḥānallāh | 1/33 | total 1/100
>   [1/4] Subḥānallāh | 2/33 | total 2/100
...
>   [1/4] Subḥānallāh | 32/33 | total 32/100
>   ** Tasbih 33x selesai (total 33/100).

[2/4] Berikutnya: Tahmid 33x
  الْحَمْدُ لِلَّهِ
...
>   ** Takbir 33x selesai (total 99/100).

[4/4] Berikutnya: Tahlil penutup 1x
  لَا إِلَهَ إِلَّا اللَّهُ وَحْدَهُ لَا شَرِيكَ لَهُ، لَهُ الْمُلْكُ وَلَهُ الْحَمْدُ، وَهُوَ عَلَى كُلِّ شَيْءٍ قَدِيرٌ
  Lā ilāha illallāhu waḥdahu lā syarīka lah, lahul-mulku wa lahul-ḥamdu, wa huwa ‘alā kulli syai’in qadīr
  Artinya: "Tiada tuhan (yang berhak disembah) selain Allah semata, tiada sekutu bagi-Nya. Milik-Nya kerajaan dan milik-Nya segala puji, dan Dia Mahakuasa atas segala sesuatu."
>   ** Tahlil penutup 1x selesai (total 100/100).
Alhamdulillah, rangkaian selesai: 100 dzikir.
Tersimpan ke riwayat-demo.json: Tasbih +33, Tahmid +33, Takbir +33, Tahlil penutup +1
```

Varian 34 takbir dijalankan dengan `python3 tasbih.py --takbir-34`. Pada mode preset, `u` bisa mundur ke langkah sebelumnya, jadi kelebihan satu ketukan saat pindah dari tasbih ke tahmid tetap bisa dikoreksi.

### Melihat riwayat

```text
$ python3 tasbih.py --riwayat --file riwayat-demo.json
Riwayat dzikir — berkas: riwayat-demo.json
Hari ini (21-10-2026): 203 kali
  - Tasbih                             69
  - Takbir                             67
  - Tahmid                             66
  - Tahlil penutup                      1
7 hari terakhir: 203 kali
  - Tasbih                             69
  - Takbir                             67
  - Tahmid                             66
  - Tahlil penutup                      1
Total sepanjang waktu: 203 kali
  - Tasbih                             69
  - Takbir                             67
  - Tahmid                             66
  - Tahlil penutup                      1
```

Angka 203 berasal dari tiga sesi uji di atas: 3 tasbih, satu rangkaian 100, dan satu rangkaian varian 34 takbir.

### Daftar opsi

| Opsi | Fungsi |
|---|---|
| `--dzikir KUNCI` | pilih dzikir: tasbih, tahmid, takbir, tahlil, istighfar, shalawat, tahlil-penutup |
| `--target N` | target per putaran (33, 99, 100, atau angka lain) |
| `--shalat` / `--takbir-34` | preset dzikir setelah shalat |
| `--daftar` | tampilkan daftar dzikir singkat |
| `--riwayat` | ringkasan hari ini, 7 hari, dan total |
| `--file BERKAS` | lokasi riwayat (default `~/.tasbih_online_riwayat.json`) |
| `--tanpa-simpan` / `--tanpa-bel` | tidak menyimpan riwayat / mematikan bel |

## Dzikir Setelah Shalat dan Dalilnya

Bagian ini merangkum riwayat yang menjadi dasar preset. Nomor hadis mengikuti penomoran Muhammad Fuad ‘Abdul Baqi seperti di sunnah.com, dan terjemahannya adalah terjemahan kami atas teks Arab. Untuk pemahaman fikih yang lebih dalam, rujuklah kitab syarah atau tanyakan kepada ustadz.

### HR. Muslim no. 597: 33-33-33 digenapkan 100 dengan tahlil

Dari **Abu Hurairah**, Rasulullah ﷺ bersabda: *"Barang siapa bertasbih kepada Allah setiap selesai shalat 33 kali, bertahmid 33 kali, dan bertakbir 33 kali, itu 99, lalu menggenapkan seratus dengan mengucapkan lā ilāha illallāhu waḥdahu lā syarīka lah, lahul-mulku wa lahul-ḥamdu wa huwa ‘alā kulli syai’in qadīr, maka diampuni kesalahan-kesalahannya walaupun sebanyak buih di lautan."* (HR. Muslim no. 597, Kitab al-Masajid; [sunnah.com/muslim:597a](https://sunnah.com/muslim:597a)). Urutan inilah yang dipakai mode `--shalat`.

### HR. Muslim no. 596: varian 34 takbir

Dari **Ka‘b bin ‘Ujrah**, Rasulullah ﷺ bersabda: *"Ada bacaan-bacaan penyerta (mu‘aqqibāt) yang orang yang mengucapkannya setiap selesai shalat wajib tidak akan merugi: 33 kali tasbih, 33 kali tahmid, dan 34 kali takbir."* (HR. Muslim no. 596; [sunnah.com/muslim:596a](https://sunnah.com/muslim:596a)). Karena itu tersedia opsi `--takbir-34`. Totalnya juga 100, tetapi tanpa tahlil penutup.

### Riwayat lain yang berkaitan

- **HR. Muslim no. 595** (Abu Hurairah): kisah kaum fakir Muhajirin yang diajari bertasbih, bertakbir, dan bertahmid 33 kali setiap selesai shalat ([sunnah.com/muslim:595a](https://sunnah.com/muslim:595a)).
- **HR. Muslim no. 591** (Tsauban): selesai shalat, Rasulullah ﷺ beristighfar tiga kali. Al-Auza‘i menjelaskan lafaznya: *astagfirullāh, astagfirullāh* ([sunnah.com/muslim:591](https://sunnah.com/muslim:591)).
- **HR. Bukhari no. 6357** (Ka‘b bin ‘Ujrah): pengajaran shalawat yang diawali *Allāhumma ṣalli ‘alā Muḥammad wa ‘alā āli Muḥammad* ([sunnah.com/bukhari:6357](https://sunnah.com/bukhari:6357)). Lafaz shalawat di aplikasi ini adalah bagian pembukanya yang pendek.

## Cara Menghitung Putaran Secara Manual

Logika penghitung sangat sederhana dan bisa Anda cek sendiri:

- **putaran** = hitungan ÷ target, dibulatkan ke bawah
- **posisi dalam putaran** = sisa bagi hitungan terhadap target (tampil sebagai `33/33` tepat ketika target tercapai)

Contoh: Anda menekan Enter 100 kali dengan target 33.

1. 100 ÷ 33 = 3,03, dibulatkan ke bawah menjadi **3 putaran**.
2. Sisa bagi: 100 − (3 × 33) = 100 − 99 = **1**.
3. Status yang tampil: `1/33 | putaran 3 | total 100`.

Hasil ini sama persis dengan test `test_putaran_berapa_kali_33`. Untuk preset dzikir setelah shalat, totalnya 33 + 33 + 33 + 1 = 100. Untuk varian takbir, totalnya 33 + 33 + 34 = 100.

## Tabel Referensi Bacaan Dzikir

| Kunci | Arab | Latin | Arti | Jumlah di preset |
|---|---|---|---|---|
| tasbih | سُبْحَانَ اللَّهِ | Subḥānallāh | Mahasuci Allah | 33 |
| tahmid | الْحَمْدُ لِلَّهِ | Alḥamdulillāh | Segala puji bagi Allah | 33 |
| takbir | اللَّهُ أَكْبَرُ | Allāhu akbar | Allah Mahabesar | 33 (atau 34) |
| tahlil-penutup | لَا إِلَهَ إِلَّا اللَّهُ وَحْدَهُ لَا شَرِيكَ لَهُ ... | Lā ilāha illallāhu waḥdahu lā syarīka lah ... | Tiada tuhan selain Allah semata ... | 1 |
| tahlil | لَا إِلَهَ إِلَّا اللَّهُ | Lā ilāha illallāh | Tiada tuhan (yang berhak disembah) selain Allah | bebas |
| istighfar | أَسْتَغْفِرُ اللَّهَ | Astagfirullāh | Aku memohon ampun kepada Allah | bebas |
| shalawat | اللَّهُمَّ صَلِّ عَلَى مُحَمَّدٍ | Allāhumma ṣalli ‘alā Muḥammad | Ya Allah, limpahkanlah shalawat kepada Muhammad | bebas |

Transliterasi latin mengikuti kebiasaan di Indonesia (ش ditulis *sy*, غ ditulis *g*). Tampilan huruf Arab di terminal bergantung pada font dan dukungan teks kanan-ke-kiri; jika harakat tampak bergeser, rujuk tabel ini atau sumber hadisnya.

## Tasbih Fisik vs Tasbih Digital

Pertanyaan ini sering muncul, jadi kami jawab secara netral dan tanpa berfatwa.

**Tasbih fisik** (untaian butir) tidak butuh listrik, terasa nyata di tangan, dan tidak membuat mata terpaku pada layar. Kekurangannya, mudah lupa sudah putaran ke berapa jika jumlahnya besar.

**Tasbih digital**, baik counter genggam, aplikasi ponsel, maupun tasbih online seperti proyek ini, unggul dalam pencatatan: hitungan tidak hilang, ada pengingat target dan riwayat harian. Kekurangannya, perangkat bisa memancing distraksi seperti notifikasi.

Ada pula cara yang tidak memerlukan alat apa pun, yaitu menghitung dengan jari. **Abdullah bin ‘Amr** menuturkan bahwa ia melihat Rasulullah ﷺ menghitung tasbih; dalam redaksi Ibnu Qudamah disebutkan "dengan tangan kanannya" (HR. Abu Dawud no. 1502, dinilai sahih oleh Al-Albani; [sunnah.com/abudawud:1502](https://sunnah.com/abudawud:1502)).

Soal hukum memakai alat bantu hitung, para ulama memiliki pembahasan tersendiri. Kami tidak dalam kapasitas memutuskannya. Silakan bertanya kepada ustadz atau guru ngaji yang Anda percaya. Bagi kami, alat apa pun hanyalah sarana. Yang utama tetap bacaan dan kehadiran hati.

## Privasi Data Anda

- Tasbih online ini **tidak mengirim data apa pun** ke internet. Kodenya tidak memakai modul jaringan sama sekali; silakan periksa sendiri di `tasbih.py`.
- Riwayat disimpan di berkas JSON milik Anda, secara default `~/.tasbih_online_riwayat.json`. Isinya hanya tanggal, nama dzikir, dan jumlah.
- Berkas ditulis secara atomik (berkas sementara lalu diganti), jadi riwayat tidak mudah rusak bila komputer mati mendadak.
- Ingin tanpa jejak? Pakai `--tanpa-simpan`, atau hapus saja berkas riwayatnya.

## Tips dan Kesalahan Umum

Hal-hal berikut paling sering ditanyakan saat pertama kali memakai tasbih online di terminal.

- **Lupa menekan `q`.** Riwayat baru disimpan saat Anda keluar dengan `q`. Ctrl+C juga menyimpan hitungan yang sudah ada. Jika jendela terminal ditutup paksa, hitungan sesi itu tidak tersimpan.
- **Reset tanpa sengaja.** Itu sebabnya `r` selalu meminta konfirmasi `y/n`. Jika Anda hanya kelebihan satu ketukan, gunakan `u` saja.
- **Bel tidak berbunyi.** Sebagian terminal mematikan suara bel. Aktifkan "audible bell" di pengaturan terminal, atau andalkan pesan `** Target ... tercapai`.
- **Folder sinkron.** Jika `--file` diarahkan ke folder cloud pribadi, data riwayat ikut tersinkron ke layanan tersebut.
- **Mengejar angka, lupa makna.** Penghitung hanya alat bantu. Bacalah perlahan, dan lihat kolom arti di tabel referensi agar dzikir lebih bermakna.

## FAQ

**Apakah tasbih online ini butuh koneksi internet?**
Tidak. Meskipun disebut tasbih online, aplikasi ini sepenuhnya offline setelah diunduh.

**Bisakah dipakai sebagai counter dzikir untuk 1.000 kali istighfar?**
Bisa. Jalankan `python3 tasbih.py --dzikir istighfar --target 1000`. Atau pakai target 100 jika ingin pengingat setiap seratus kali.

**Bagaimana cara hitung dzikir setelah shalat 33 kali secara otomatis berurutan?**
Gunakan `python3 tasbih.py --shalat`. Aplikasi otomatis berpindah dari tasbih ke tahmid, takbir, lalu tahlil penutup.

**Kenapa ada versi 33 takbir dan 34 takbir?**
Keduanya berasal dari riwayat sahih yang berbeda: HR. Muslim no. 597 (33 takbir + tahlil) dan HR. Muslim no. 596 (34 takbir). Aplikasi menyediakan keduanya tanpa mengunggulkan salah satunya.

**Apakah ini bisa jadi tasbih digital online di HP?**
Bisa jika ponsel Anda punya terminal dengan Python, tetapi proyek ini dirancang untuk komputer.

**Di mana data penghitung dzikir online ini disimpan? Apakah ada dzikir online yang tersinkron ke server?**
Tidak ada server. Data hanya ada di komputer Anda, dalam berkas JSON yang lokasinya bisa diubah dengan `--file`.

**Apakah aplikasi ini menggantikan bimbingan guru?**
Tidak. Ini hanya alat bantu menghitung. Untuk adab, hukum, dan keutamaan dzikir, bertanyalah kepada ustadz.

## Metodologi Pengujian dan Sumber

Logika inti tasbih online ini (penghitung, sesi berurutan, dan riwayat) ditulis sebagai fungsi dan kelas murni tanpa input/output, sehingga bisa diuji otomatis. Jalankan:

```bash
python3 -m unittest discover -s tests -v
```

Hasil pada versi ini: `Ran 22 tests ... OK`. Beberapa kasus yang diuji:

- 33 ketukan bertarget 33 memicu tepat satu notifikasi; 100 ketukan menghasilkan 3 putaran dengan posisi 1/33, sama dengan hitungan manual di atas.
- Undo tidak pernah membuat hitungan negatif, dan pada preset bisa mundur ke langkah sebelumnya.
- Preset berjumlah tepat 100 dengan urutan tasbih, tahmid, takbir, tahlil penutup; varian 34 takbir juga 100.
- Ringkasan 7 hari mencakup hari ini dan 6 hari sebelumnya.
- Simpan/muat riwayat diuji di folder sementara (`tempfile`); berkas rusak menghasilkan pesan ramah dan exit code 1 tanpa menimpa data.
- Simulasi sesi lewat `main()` dengan masukan tiruan memastikan hitungan benar-benar tersimpan, termasuk saat stdin habis (EOF).

Teks Arab setiap dzikir kami cocokkan huruf demi huruf dengan matan hadis pada dataset terbuka [hadith-api](https://github.com/fawazahmed0/hadith-api). Nomor hadis dan perawinya kami cek silang dengan sunnah.com. Perbedaan yang ada hanya gaya penulisan harakat (misalnya letak syaddah pada *illā*), bukan perbedaan lafaz.

Sumber rujukan:

- Sahih Muslim no. 591, 595, 596, 597 — [sunnah.com/muslim:591](https://sunnah.com/muslim:591), [sunnah.com/muslim:595a](https://sunnah.com/muslim:595a), [sunnah.com/muslim:596a](https://sunnah.com/muslim:596a), [sunnah.com/muslim:597a](https://sunnah.com/muslim:597a)
- Sahih al-Bukhari no. 6357 — [sunnah.com/bukhari:6357](https://sunnah.com/bukhari:6357)
- Sunan Abi Dawud no. 1502 — [sunnah.com/abudawud:1502](https://sunnah.com/abudawud:1502)
- Dokumentasi `unittest` Python — [docs.python.org/3/library/unittest.html](https://docs.python.org/3/library/unittest.html)

## Tentang Pembuat

Proyek ini adalah karya [JoinBareng](https://joinbareng.com) dan dikelola oleh [@redyopa2929](https://github.com/redyopa2929). JoinBareng adalah *platform patungan langganan premium (Netflix, Spotify, YouTube Premium, ChatGPT, dll.) plus marketplace akun digital yang aman dan transparan.* Seri tools Python ini kami buat sebagai alat kecil yang berguna sehari-hari, terbuka untuk diperiksa siapa saja.

## Disclaimer

Aplikasi ini alat bantu hitung, bukan sumber fatwa. Rujukan hadis dicantumkan agar pembaca bisa memeriksa sendiri; terjemahannya bersifat bebas. Untuk hukum, tata cara, dan keutamaan ibadah, rujuklah ulama atau ustadz yang kompeten. Temukan kekeliruan teks Arab, latin, atau terjemahan? Mohon laporkan agar segera kami perbaiki.

## Kontribusi

Laporan bug, koreksi teks, dan saran fitur untuk tasbih online ini sangat kami hargai. Silakan buka issue di [github.com/redyopa2929/tasbih-online/issues](https://github.com/redyopa2929/tasbih-online/issues). Pull request juga diterima; pastikan semua test lulus dan tidak menambah dependency eksternal.

## Lisensi

Dirilis dengan lisensi MIT. Lihat berkas [LICENSE](LICENSE). Anda bebas memakai, mengubah, dan membagikan kode ini.

## Dukung Proyek Ini

Jika tasbih online ini bermanfaat, beri ⭐ **star** pada repositori agar lebih mudah ditemukan orang lain. Ingin berhemat untuk langganan aplikasi premium, termasuk aplikasi kajian atau murottal favorit Anda? Coba patungan di [JoinBareng](https://joinbareng.com), supaya biaya langganan terasa lebih ringan dan sisa anggarannya bisa dialihkan untuk sedekah.

## Tools Lainnya dari Seri Ini

- [Kalkulator Jadian](https://github.com/redyopa2929/kalkulator-jadian) — hitung lama hari jadian & anniversary
- [Kalkulator Jasmani Polri](https://github.com/redyopa2929/kalkulator-jasmani-polri) — hitung nilai kesamaptaan jasmani
- [Hitung WR ML](https://github.com/redyopa2929/hitung-wr-ml) — hitung win rate Mobile Legends
- [Kalkulator Selamatan](https://github.com/redyopa2929/kalkulator-selamatan) — hitung selamatan orang meninggal adat Jawa
- [Terbilang Online](https://github.com/redyopa2929/terbilang-online) — ubah angka ke huruf / terbilang rupiah
- [Kalkulator Saham](https://github.com/redyopa2929/kalkulator-saham) — average down, compounding, ARA/ARB
- [Kalkulator Bangunan](https://github.com/redyopa2929/kalkulator-bangunan) — keramik, hebel, kubikasi, besi
- [Konversi Koordinat](https://github.com/redyopa2929/konversi-koordinat) — DMS, desimal, UTM
- [Cek Weton](https://github.com/redyopa2929/cek-weton) — cek weton & neptu dari tanggal lahir

Terakhir diperbarui: 21 Oktober 2026
