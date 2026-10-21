#!/usr/bin/env python3
"""Tasbih Online — penghitung dzikir (tasbih digital) untuk terminal.

Tekan Enter untuk +1, ketik `u` (undo), `r` (reset), `t` (ganti target),
atau `q` (selesai & simpan). Ada preset dzikir setelah shalat dan riwayat
harian yang disimpan lokal dalam berkas JSON. Hanya memakai standard library
Python 3.8+.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import tempfile
from dataclasses import dataclass
from datetime import date, timedelta
from typing import Dict, List, Optional, Tuple

VERSI = "1.0.0"
BERKAS_DEFAULT = os.path.join("~", ".tasbih_online_riwayat.json")
TARGET_MAKS = 1_000_000
BANTUAN = "Enter = +1 | u = undo | r = reset | t = ganti target | q = selesai & simpan"

Riwayat = Dict[str, Dict[str, int]]  # {"2026-10-21": {"tasbih": 33, ...}}


@dataclass(frozen=True)
class Dzikir:
    kunci: str
    nama: str
    arab: str
    latin: str
    arti: str


_DZIKIR = (
    Dzikir("tasbih", "Tasbih", "سُبْحَانَ اللَّهِ", "Subḥānallāh", "Mahasuci Allah"),
    Dzikir("tahmid", "Tahmid", "الْحَمْدُ لِلَّهِ", "Alḥamdulillāh", "Segala puji bagi Allah"),
    Dzikir("takbir", "Takbir", "اللَّهُ أَكْبَرُ", "Allāhu akbar", "Allah Mahabesar"),
    Dzikir("tahlil", "Tahlil", "لَا إِلَهَ إِلَّا اللَّهُ", "Lā ilāha illallāh",
           "Tiada tuhan (yang berhak disembah) selain Allah"),
    Dzikir("istighfar", "Istighfar", "أَسْتَغْفِرُ اللَّهَ", "Astagfirullāh",
           "Aku memohon ampun kepada Allah"),
    Dzikir("shalawat", "Shalawat", "اللَّهُمَّ صَلِّ عَلَى مُحَمَّدٍ",
           "Allāhumma ṣalli ‘alā Muḥammad", "Ya Allah, limpahkanlah shalawat kepada Muhammad"),
    Dzikir("tahlil-penutup", "Tahlil penutup",
           "لَا إِلَهَ إِلَّا اللَّهُ وَحْدَهُ لَا شَرِيكَ لَهُ، لَهُ الْمُلْكُ وَلَهُ الْحَمْدُ، "
           "وَهُوَ عَلَى كُلِّ شَيْءٍ قَدِيرٌ",
           "Lā ilāha illallāhu waḥdahu lā syarīka lah, lahul-mulku wa lahul-ḥamdu, "
           "wa huwa ‘alā kulli syai’in qadīr",
           "Tiada tuhan (yang berhak disembah) selain Allah semata, tiada sekutu bagi-Nya. "
           "Milik-Nya kerajaan dan milik-Nya segala puji, dan Dia Mahakuasa atas segala sesuatu."),
)
DAFTAR_DZIKIR: Dict[str, Dzikir] = {d.kunci: d for d in _DZIKIR}

# HR. Muslim no. 597 (Abu Hurairah): 33 tasbih, 33 tahmid, 33 takbir, genap 100 dengan tahlil.
URUTAN_SETELAH_SHALAT: List[Tuple[str, int]] = [
    ("tasbih", 33), ("tahmid", 33), ("takbir", 33), ("tahlil-penutup", 1)]
# HR. Muslim no. 596 (Ka'b bin 'Ujrah): 33 tasbih, 33 tahmid, 34 takbir.
URUTAN_TAKBIR_34: List[Tuple[str, int]] = [("tasbih", 33), ("tahmid", 33), ("takbir", 34)]


# ---------------------------------------------------------------- logika murni
def format_angka(n: int) -> str:
    """Format bilangan bulat gaya Indonesia: 1234 -> '1.234'."""
    return f"{n:,}".replace(",", ".")


def validasi_target(target: int) -> int:
    if isinstance(target, bool) or not isinstance(target, int):
        raise ValueError("Target harus berupa bilangan bulat.")
    if not 1 <= target <= TARGET_MAKS:
        raise ValueError(f"Target harus antara 1 dan {format_angka(TARGET_MAKS)}.")
    return target


def parse_target(teks: str) -> int:
    """Ubah teks seperti '33' menjadi target yang valid (ValueError bila salah)."""
    teks = teks.strip().replace(".", "")
    if not re.fullmatch(r"[0-9]+", teks):
        raise ValueError("Target harus berupa angka bulat positif, misalnya 33, 99, atau 100.")
    return validasi_target(int(teks))


def tafsir_perintah(teks: str) -> str:
    """Terjemahkan ketikan pengguna menjadi nama perintah."""
    t = teks.strip().lower()
    peta = {"": "tambah", "+": "tambah", "u": "undo", "r": "reset",
            "t": "target", "q": "selesai", "x": "selesai"}
    return peta.get(t, "tidak_dikenal")


class Penghitung:
    """Penghitung dzikir bebas dengan target dan putaran (tanpa I/O)."""

    def __init__(self, target: int = 33) -> None:
        self.target = validasi_target(target)
        self.hitungan = 0

    @property
    def putaran(self) -> int:
        """Berapa kali target sudah tercapai (mis. berapa kali 33)."""
        return self.hitungan // self.target

    @property
    def posisi(self) -> int:
        """Posisi di putaran berjalan; tampil penuh (33/33) tepat saat target tercapai."""
        sisa = self.hitungan % self.target
        return self.target if sisa == 0 and self.hitungan > 0 else sisa

    def tambah(self) -> bool:
        """+1. Kembalikan True bila hitungan tepat mencapai kelipatan target."""
        self.hitungan += 1
        return self.hitungan % self.target == 0

    def undo(self) -> bool:
        if self.hitungan == 0:
            return False
        self.hitungan -= 1
        return True

    def reset(self) -> None:
        self.hitungan = 0

    def ganti_target(self, target: int) -> None:
        self.target = validasi_target(target)

    def status(self) -> str:
        return (f"{format_angka(self.posisi)}/{format_angka(self.target)} | "
                f"putaran {format_angka(self.putaran)} | total {format_angka(self.hitungan)}")


class SesiBerurutan:
    """Rangkaian dzikir berurutan, mis. dzikir setelah shalat (tanpa I/O)."""

    def __init__(self, langkah: List[Tuple[str, int]]) -> None:
        if not langkah:
            raise ValueError("Rangkaian dzikir tidak boleh kosong.")
        for kunci, jumlah in langkah:
            if kunci not in DAFTAR_DZIKIR:
                raise ValueError(f"Dzikir '{kunci}' tidak dikenal.")
            validasi_target(jumlah)
        self.langkah = list(langkah)
        self.indeks = 0
        self.hitungan = 0  # hitungan di langkah berjalan

    @property
    def selesai(self) -> bool:
        return self.indeks >= len(self.langkah)

    @property
    def dzikir_sekarang(self) -> Optional[Dzikir]:
        return None if self.selesai else DAFTAR_DZIKIR[self.langkah[self.indeks][0]]

    @property
    def target_sekarang(self) -> int:
        return 0 if self.selesai else self.langkah[self.indeks][1]

    @property
    def total_target(self) -> int:
        return sum(j for _, j in self.langkah)

    @property
    def total_hitungan(self) -> int:
        return sum(j for _, j in self.langkah[:self.indeks]) + self.hitungan

    def tambah(self) -> str:
        """+1. Hasil: 'lanjut', 'langkah_selesai', atau 'selesai'."""
        if self.selesai:
            return "selesai"
        self.hitungan += 1
        if self.hitungan >= self.target_sekarang:
            self.indeks += 1
            self.hitungan = 0
            return "selesai" if self.selesai else "langkah_selesai"
        return "lanjut"

    def undo(self) -> bool:
        if self.hitungan > 0:
            self.hitungan -= 1
            return True
        if self.indeks > 0:
            self.indeks -= 1
            self.hitungan = self.langkah[self.indeks][1] - 1
            return True
        return False

    def reset(self) -> None:
        self.indeks = 0
        self.hitungan = 0

    def rekap(self) -> Dict[str, int]:
        """Jumlah per dzikir yang sudah dibaca dalam sesi ini."""
        hasil: Dict[str, int] = {}
        for i, (kunci, jumlah) in enumerate(self.langkah):
            n = jumlah if i < self.indeks else (self.hitungan if i == self.indeks else 0)
            if n:
                hasil[kunci] = hasil.get(kunci, 0) + n
        return hasil

    def status(self) -> str:
        if self.selesai:
            return f"selesai | total {self.total_hitungan}/{self.total_target}"
        return (f"[{self.indeks + 1}/{len(self.langkah)}] {self.dzikir_sekarang.latin} | "
                f"{self.hitungan}/{self.target_sekarang} | "
                f"total {self.total_hitungan}/{self.total_target}")


# ---------------------------------------------------------------- riwayat
def catat(harian: Riwayat, tanggal: date, rekap: Dict[str, int]) -> Riwayat:
    """Kembalikan riwayat baru yang sudah ditambah rekap sesi (data lama tidak diubah)."""
    baru = {tgl: dict(isi) for tgl, isi in harian.items()}
    hari = baru.setdefault(tanggal.isoformat(), {})
    for kunci, n in rekap.items():
        if n > 0:
            hari[kunci] = hari.get(kunci, 0) + n
    if not hari:
        del baru[tanggal.isoformat()]
    return baru


def ringkas(harian: Riwayat, hari_ini: date) -> Dict[str, Dict[str, int]]:
    """Ringkasan per dzikir: hari ini, 7 hari terakhir (termasuk hari ini), dan total."""
    hasil: Dict[str, Dict[str, int]] = {"hari_ini": {}, "tujuh_hari": {}, "total": {}}
    awal_7 = hari_ini - timedelta(days=6)
    for tgl_str, isi in harian.items():
        tgl = date.fromisoformat(tgl_str)
        for kunci, n in isi.items():
            hasil["total"][kunci] = hasil["total"].get(kunci, 0) + n
            if awal_7 <= tgl <= hari_ini:
                hasil["tujuh_hari"][kunci] = hasil["tujuh_hari"].get(kunci, 0) + n
            if tgl == hari_ini:
                hasil["hari_ini"][kunci] = hasil["hari_ini"].get(kunci, 0) + n
    return hasil


def muat_riwayat(path: str) -> Riwayat:
    """Baca riwayat JSON. Berkas belum ada -> riwayat kosong. Rusak -> ValueError."""
    if not os.path.exists(path):
        return {}
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        harian = data["harian"]
        bersih: Riwayat = {}
        for tgl, isi in harian.items():
            date.fromisoformat(tgl)
            bersih[tgl] = {str(k): int(v) for k, v in isi.items()}
        return bersih
    except (ValueError, KeyError, TypeError, AttributeError) as e:
        raise ValueError(f"Berkas riwayat '{path}' rusak atau bukan format tasbih-online ({e}).")


def simpan_riwayat(path: str, harian: Riwayat) -> None:
    """Tulis riwayat secara atomik (berkas sementara lalu os.replace)."""
    folder = os.path.dirname(os.path.abspath(path))
    os.makedirs(folder, exist_ok=True)
    data = {"aplikasi": "tasbih-online", "versi": 1,
            "harian": {k: harian[k] for k in sorted(harian)}}
    fd, tmp = tempfile.mkstemp(prefix=".tasbih-", suffix=".tmp", dir=folder)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        os.replace(tmp, path)
    except BaseException:
        if os.path.exists(tmp):
            os.remove(tmp)
        raise


def nama_dzikir(kunci: str) -> str:
    return DAFTAR_DZIKIR[kunci].nama if kunci in DAFTAR_DZIKIR else kunci


def format_ringkasan(ringkasan: Dict[str, Dict[str, int]], hari_ini: date) -> str:
    judul = {"hari_ini": f"Hari ini ({hari_ini.strftime('%d-%m-%Y')})",
             "tujuh_hari": "7 hari terakhir", "total": "Total sepanjang waktu"}
    baris: List[str] = []
    for bagian in ("hari_ini", "tujuh_hari", "total"):
        isi = ringkasan[bagian]
        baris.append(f"{judul[bagian]}: {format_angka(sum(isi.values()))} kali")
        for kunci in sorted(isi, key=lambda k: (-isi[k], k)):
            baris.append(f"  - {nama_dzikir(kunci):<28} {format_angka(isi[kunci]):>8}")
    return "\n".join(baris)


# ---------------------------------------------------------------- I/O terminal
def tampilkan_dzikir(d: Dzikir) -> None:
    print(f"  {d.arab}\n  {d.latin}\n  Artinya: \"{d.arti}\"")


def baca(prompt: str) -> str:
    try:
        return input(prompt)
    except EOFError:  # stdin habis (mis. lewat pipe) dianggap selesai
        return "q"


def bunyi(bel: bool) -> None:
    print("\a" if bel else "", end="", flush=True)


def jalankan_hitung(dzikir: Dzikir, target: int, bel: bool = True) -> Dict[str, int]:
    p = Penghitung(target)
    print(f"\n== {dzikir.nama} | target {format_angka(target)} ==")
    tampilkan_dzikir(dzikir)
    print(BANTUAN)
    try:
        while True:
            perintah = tafsir_perintah(baca("> "))
            if perintah == "tambah":
                if p.tambah():
                    bunyi(bel)
                    print(f"  ** Target {format_angka(p.target)} tercapai — putaran ke-"
                          f"{format_angka(p.putaran)}. Lanjutkan (Enter) atau q untuk selesai.")
                print("  " + p.status())
            elif perintah == "undo":
                print("  " + (p.status() if p.undo() else "Hitungan sudah 0."))
            elif perintah == "reset":
                if baca(f"  Reset hitungan {format_angka(p.hitungan)} ke 0? (y/n) ").strip().lower() == "y":
                    p.reset()
                    print("  Hitungan direset ke 0.")
            elif perintah == "target":
                try:
                    p.ganti_target(parse_target(baca("  Target baru (33/99/100/angka lain): ")))
                    print("  " + p.status())
                except ValueError as e:
                    print(f"  {e}")
            elif perintah == "selesai":
                break
            else:
                print("  Perintah tidak dikenal. " + BANTUAN)
    except KeyboardInterrupt:
        print("\n  Dihentikan (Ctrl+C).")
    print(f"Selesai: {dzikir.nama} {format_angka(p.hitungan)} kali.")
    return {dzikir.kunci: p.hitungan} if p.hitungan else {}


def jalankan_berurutan(langkah: List[Tuple[str, int]], bel: bool = True) -> Dict[str, int]:
    s = SesiBerurutan(langkah)
    print(f"\n== Dzikir setelah shalat | total {s.total_target} ==")
    print(" -> ".join(f"{DAFTAR_DZIKIR[k].nama} {j}x" for k, j in langkah))
    print(BANTUAN.replace(" | t = ganti target", ""))
    print(f"\n[1/{len(langkah)}] {s.dzikir_sekarang.nama} {s.target_sekarang}x")
    tampilkan_dzikir(s.dzikir_sekarang)
    try:
        while not s.selesai:
            perintah = tafsir_perintah(baca("> "))
            if perintah == "tambah":
                sebelum, target = s.dzikir_sekarang, s.target_sekarang
                hasil = s.tambah()
                if hasil == "lanjut":
                    print("  " + s.status())
                    continue
                bunyi(bel)
                print(f"  ** {sebelum.nama} {target}x selesai "
                      f"(total {s.total_hitungan}/{s.total_target}).")
                if hasil == "langkah_selesai":
                    print(f"\n[{s.indeks + 1}/{len(langkah)}] Berikutnya: "
                          f"{s.dzikir_sekarang.nama} {s.target_sekarang}x")
                    tampilkan_dzikir(s.dzikir_sekarang)
            elif perintah == "undo":
                print("  " + (s.status() if s.undo() else "Hitungan sudah 0."))
            elif perintah == "reset":
                if baca("  Ulang rangkaian dari awal? (y/n) ").strip().lower() == "y":
                    s.reset()
                    print("  " + s.status())
            elif perintah == "target":
                print("  Target tidak bisa diubah pada mode dzikir setelah shalat.")
            elif perintah == "selesai":
                break
            else:
                print("  Perintah tidak dikenal. " + BANTUAN)
    except KeyboardInterrupt:
        print("\n  Dihentikan (Ctrl+C).")
    if s.selesai:
        print(f"Alhamdulillah, rangkaian selesai: {s.total_hitungan} dzikir.")
    else:
        print(f"Rangkaian belum selesai: {s.total_hitungan}/{s.total_target}.")
    return s.rekap()


def simpan_sesi(path: str, rekap: Dict[str, int], hari_ini: date) -> None:
    if not rekap:
        print("Tidak ada hitungan untuk disimpan.")
        return
    harian = catat(muat_riwayat(path), hari_ini, rekap)
    simpan_riwayat(path, harian)
    isi = ", ".join(f"{nama_dzikir(k)} +{format_angka(n)}" for k, n in rekap.items())
    print(f"Tersimpan ke {path}: {isi}")


def tampilkan_daftar() -> None:
    print("Daftar dzikir singkat (kunci untuk --dzikir):")
    for d in _DZIKIR:
        print(f"\n[{d.kunci}] {d.nama}")
        tampilkan_dzikir(d)


def tampilkan_riwayat(path: str, hari_ini: date) -> None:
    harian = muat_riwayat(path)
    print(f"Riwayat dzikir — berkas: {path}")
    if not harian:
        print("Belum ada riwayat. Mulai berdzikir lalu ketik q untuk menyimpan.")
        return
    print(format_ringkasan(ringkas(harian, hari_ini), hari_ini))


def menu_interaktif(path: str, bel: bool, simpan: bool) -> None:
    print(f"=== Tasbih Online v{VERSI} — penghitung dzikir di terminal ===\n"
          "1. Hitung dzikir bebas (pilih dzikir & target)\n"
          "2. Dzikir setelah shalat: 33 tasbih, 33 tahmid, 33 takbir + tahlil = 100\n"
          "3. Dzikir setelah shalat varian 34 takbir (33 + 33 + 34)\n"
          "4. Daftar dzikir singkat\n5. Lihat riwayat\n0. Keluar")
    pilihan = baca("Pilih [1]: ").strip() or "1"
    rekap: Dict[str, int] = {}
    if pilihan == "1":
        kunci = [d.kunci for d in _DZIKIR if d.kunci != "tahlil-penutup"]
        for i, k in enumerate(kunci, 1):
            print(f"  {i}. {DAFTAR_DZIKIR[k].nama} — {DAFTAR_DZIKIR[k].latin}")
        p = baca("Pilih dzikir [1]: ").strip() or "1"
        if not (re.fullmatch(r"[0-9]+", p) and 1 <= int(p) <= len(kunci)):
            raise ValueError(f"Pilihan dzikir harus 1 sampai {len(kunci)}.")
        target = parse_target(baca("Target (33/99/100/angka lain) [33]: ") or "33")
        rekap = jalankan_hitung(DAFTAR_DZIKIR[kunci[int(p) - 1]], target, bel)
    elif pilihan in ("2", "3"):
        rekap = jalankan_berurutan(URUTAN_SETELAH_SHALAT if pilihan == "2" else URUTAN_TAKBIR_34, bel)
    elif pilihan == "4":
        tampilkan_daftar()
    elif pilihan == "5":
        tampilkan_riwayat(path, date.today())
    elif pilihan in ("0", "q"):
        print("Sampai jumpa.")
    else:
        raise ValueError("Pilihan menu harus 0 sampai 5.")
    if rekap and simpan:
        simpan_sesi(path, rekap, date.today())


def _target_arg(teks: str) -> int:
    try:
        return parse_target(teks)
    except ValueError as e:
        raise argparse.ArgumentTypeError(str(e))


def _dzikir_arg(teks: str) -> str:
    kunci = teks.strip().lower()
    if kunci not in DAFTAR_DZIKIR:
        raise argparse.ArgumentTypeError(
            f"'{teks}' tidak dikenal. Pilihan: {', '.join(sorted(DAFTAR_DZIKIR))}.")
    return kunci


class _Formatter(argparse.HelpFormatter):
    def add_usage(self, usage, actions, groups, prefix=None):  # type: ignore[override]
        return super().add_usage(usage, actions, groups, prefix or "Pemakaian: ")


class _Parser(argparse.ArgumentParser):
    def error(self, message: str) -> None:  # type: ignore[override]
        for en, idn in (("unrecognized arguments", "argumen tidak dikenal"),
                        ("expected one argument", "butuh satu nilai"), ("argument ", "opsi ")):
            message = message.replace(en, idn)
        self.print_usage(sys.stderr)
        self.exit(2, f"Error: {message}\nKetik `python3 {self.prog} -h` untuk bantuan.\n")


def buat_parser() -> argparse.ArgumentParser:
    ap = _Parser(
        prog="tasbih.py", add_help=False, formatter_class=_Formatter,
        description="Tasbih Online: penghitung dzikir (tasbih digital) di terminal. "
                    "Tanpa argumen akan membuka menu interaktif.")
    ap._optionals.title = "Opsi"
    ap.add_argument("-h", "--help", action="help", help="tampilkan bantuan ini lalu keluar")
    ap.add_argument("--dzikir", type=_dzikir_arg, metavar="KUNCI",
                    help="dzikir yang dihitung: " + ", ".join(sorted(DAFTAR_DZIKIR)) + " (default: tasbih)")
    ap.add_argument("--target", type=_target_arg, metavar="N",
                    help="target per putaran: 33, 99, 100, atau angka lain")
    ap.add_argument("--shalat", action="store_true",
                    help="preset dzikir setelah shalat (33 tasbih, 33 tahmid, 33 takbir, tahlil = 100)")
    ap.add_argument("--takbir-34", action="store_true",
                    help="preset varian 33 tasbih, 33 tahmid, 34 takbir")
    ap.add_argument("--daftar", action="store_true", help="tampilkan daftar dzikir singkat (Arab, latin, arti)")
    ap.add_argument("--riwayat", action="store_true", help="tampilkan ringkasan riwayat (hari ini, 7 hari, total)")
    ap.add_argument("--file", default=BERKAS_DEFAULT, metavar="BERKAS",
                    help="lokasi berkas riwayat JSON (default: %(default)s)")
    ap.add_argument("--tanpa-simpan", action="store_true", help="jangan simpan hasil ke riwayat")
    ap.add_argument("--tanpa-bel", action="store_true", help="matikan bunyi bel saat target tercapai")
    ap.add_argument("--versi", action="version", version=f"%(prog)s {VERSI}",
                    help="tampilkan versi lalu keluar")
    return ap


def main(argv: Optional[List[str]] = None) -> int:
    args = buat_parser().parse_args(argv)
    path = os.path.expanduser(args.file)
    bel = not args.tanpa_bel
    try:
        if args.riwayat:
            tampilkan_riwayat(path, date.today())
        elif args.daftar:
            tampilkan_daftar()
        elif args.shalat or args.takbir_34:
            rekap = jalankan_berurutan(URUTAN_TAKBIR_34 if args.takbir_34 else URUTAN_SETELAH_SHALAT, bel)
            if not args.tanpa_simpan:
                simpan_sesi(path, rekap, date.today())
        elif args.dzikir or args.target:
            rekap = jalankan_hitung(DAFTAR_DZIKIR[args.dzikir or "tasbih"], args.target or 33, bel)
            if not args.tanpa_simpan:
                simpan_sesi(path, rekap, date.today())
        else:
            menu_interaktif(path, bel, not args.tanpa_simpan)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except OSError as e:
        print(f"Error: gagal membaca/menulis berkas riwayat ({e}).", file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        print("\nDibatalkan.", file=sys.stderr)
        return 130
    return 0


if __name__ == "__main__":
    sys.exit(main())
