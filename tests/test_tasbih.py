"""Unit test untuk tasbih.py — jalankan: python3 -m unittest discover -s tests -v"""
import io
import json
import os
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from datetime import date
from unittest import mock

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

import tasbih  # noqa: E402
from tasbih import (  # noqa: E402
    DAFTAR_DZIKIR, URUTAN_SETELAH_SHALAT, URUTAN_TAKBIR_34, Penghitung, SesiBerurutan,
    catat, format_angka, muat_riwayat, parse_target, ringkas, simpan_riwayat, tafsir_perintah,
)


class TestPenghitung(unittest.TestCase):
    def test_tambah_dan_target_33(self):
        p = Penghitung(33)
        hasil = [p.tambah() for _ in range(33)]
        self.assertEqual(hasil.count(True), 1)          # hanya ketukan ke-33 yang mencapai target
        self.assertTrue(hasil[-1])
        self.assertEqual((p.hitungan, p.putaran, p.posisi), (33, 1, 33))

    def test_putaran_berapa_kali_33(self):
        p = Penghitung(33)
        for _ in range(100):
            p.tambah()
        self.assertEqual(p.putaran, 3)                  # 100 = 3 x 33 + 1
        self.assertEqual(p.posisi, 1)
        self.assertEqual(p.status(), "1/33 | putaran 3 | total 100")

    def test_undo_tidak_negatif(self):
        p = Penghitung(33)
        self.assertFalse(p.undo())
        p.tambah()
        p.tambah()
        self.assertTrue(p.undo())
        self.assertEqual(p.hitungan, 1)

    def test_reset_dan_ganti_target(self):
        p = Penghitung(99)
        for _ in range(10):
            p.tambah()
        p.ganti_target(5)
        self.assertEqual((p.putaran, p.posisi), (2, 5))  # 10 = 2 x 5
        p.reset()
        self.assertEqual((p.hitungan, p.putaran, p.posisi), (0, 0, 0))

    def test_target_tidak_valid(self):
        for salah in (0, -1, tasbih.TARGET_MAKS + 1):
            with self.assertRaises(ValueError):
                Penghitung(salah)
        with self.assertRaises(ValueError):
            Penghitung(True)


class TestParsing(unittest.TestCase):
    def test_parse_target(self):
        self.assertEqual(parse_target("33"), 33)
        self.assertEqual(parse_target(" 100 "), 100)
        self.assertEqual(parse_target("1.000"), 1000)
        for salah in ("", "abc", "-5", "0", "3,5"):
            with self.assertRaises(ValueError):
                parse_target(salah)

    def test_tafsir_perintah(self):
        self.assertEqual(tafsir_perintah(""), "tambah")
        self.assertEqual(tafsir_perintah("  U "), "undo")
        self.assertEqual(tafsir_perintah("r"), "reset")
        self.assertEqual(tafsir_perintah("t"), "target")
        self.assertEqual(tafsir_perintah("q"), "selesai")
        self.assertEqual(tafsir_perintah("zzz"), "tidak_dikenal")

    def test_format_angka_indonesia(self):
        self.assertEqual(format_angka(0), "0")
        self.assertEqual(format_angka(1234567), "1.234.567")


class TestSesiSetelahShalat(unittest.TestCase):
    def test_preset_genap_100_dan_urutan(self):
        s = SesiBerurutan(URUTAN_SETELAH_SHALAT)
        self.assertEqual(s.total_target, 100)
        urutan, kejadian = [], []
        while not s.selesai:
            urutan.append(s.dzikir_sekarang.kunci)
            kejadian.append(s.tambah())
        self.assertEqual(sorted(set(urutan), key=urutan.index),
                         ["tasbih", "tahmid", "takbir", "tahlil-penutup"])
        self.assertEqual(kejadian.count("langkah_selesai"), 3)
        self.assertEqual(kejadian[-1], "selesai")
        self.assertEqual(s.rekap(), {"tasbih": 33, "tahmid": 33, "takbir": 33, "tahlil-penutup": 1})

    def test_varian_34_takbir(self):
        s = SesiBerurutan(URUTAN_TAKBIR_34)
        for _ in range(100):
            s.tambah()
        self.assertTrue(s.selesai)
        self.assertEqual(s.rekap(), {"tasbih": 33, "tahmid": 33, "takbir": 34})

    def test_undo_mundur_ke_langkah_sebelumnya(self):
        s = SesiBerurutan(URUTAN_SETELAH_SHALAT)
        for _ in range(33):
            s.tambah()
        self.assertEqual(s.dzikir_sekarang.kunci, "tahmid")
        self.assertTrue(s.undo())
        self.assertEqual((s.dzikir_sekarang.kunci, s.hitungan, s.total_hitungan), ("tasbih", 32, 32))
        s.reset()
        self.assertEqual(s.total_hitungan, 0)
        self.assertFalse(s.undo())

    def test_rekap_sebagian(self):
        s = SesiBerurutan(URUTAN_SETELAH_SHALAT)
        for _ in range(40):
            s.tambah()
        self.assertEqual(s.rekap(), {"tasbih": 33, "tahmid": 7})

    def test_dzikir_tidak_dikenal(self):
        with self.assertRaises(ValueError):
            SesiBerurutan([("tidak-ada", 33)])


class TestDataDzikir(unittest.TestCase):
    def test_daftar_lengkap_dan_berisi_huruf_arab(self):
        for kunci in ("tasbih", "tahmid", "takbir", "tahlil", "istighfar", "shalawat", "tahlil-penutup"):
            d = DAFTAR_DZIKIR[kunci]
            self.assertTrue(any("\u0600" <= c <= "\u06ff" for c in d.arab), kunci)
            self.assertTrue(d.latin and d.arti)

    def test_lafaz_kunci(self):
        self.assertEqual(DAFTAR_DZIKIR["tasbih"].arab, "سُبْحَانَ اللَّهِ")
        self.assertEqual(DAFTAR_DZIKIR["takbir"].arab, "اللَّهُ أَكْبَرُ")
        self.assertTrue(DAFTAR_DZIKIR["tahlil-penutup"].arab.endswith("قَدِيرٌ"))


class TestRiwayat(unittest.TestCase):
    def test_catat_murni_dan_menjumlah(self):
        awal = {}
        h1 = catat(awal, date(2026, 10, 21), {"tasbih": 33})
        h2 = catat(h1, date(2026, 10, 21), {"tasbih": 33, "tahmid": 33})
        self.assertEqual(awal, {})                      # data lama tidak diubah
        self.assertEqual(h2, {"2026-10-21": {"tasbih": 66, "tahmid": 33}})
        self.assertEqual(catat({}, date(2026, 10, 21), {}), {})

    def test_ringkasan_hari_ini_7_hari_total(self):
        harian = {
            "2026-10-21": {"tasbih": 33},
            "2026-10-15": {"tasbih": 10},   # tepat 6 hari lalu -> masih 7 hari
            "2026-10-14": {"tahmid": 5},    # 7 hari lalu -> di luar 7 hari
        }
        r = ringkas(harian, date(2026, 10, 21))
        self.assertEqual(r["hari_ini"], {"tasbih": 33})
        self.assertEqual(r["tujuh_hari"], {"tasbih": 43})
        self.assertEqual(r["total"], {"tasbih": 43, "tahmid": 5})

    def test_simpan_dan_muat_tempfile(self):
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, "sub", "riwayat.json")
            self.assertEqual(muat_riwayat(path), {})    # belum ada -> kosong
            data = {"2026-10-21": {"tasbih": 33, "shalawat": 100}}
            simpan_riwayat(path, data)
            self.assertEqual(muat_riwayat(path), data)
            with open(path, encoding="utf-8") as f:
                self.assertEqual(json.load(f)["aplikasi"], "tasbih-online")
            self.assertEqual([n for n in os.listdir(os.path.dirname(path)) if n.endswith(".tmp")], [])

    def test_berkas_rusak(self):
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, "rusak.json")
            with open(path, "w", encoding="utf-8") as f:
                f.write("{bukan json")
            with self.assertRaises(ValueError):
                muat_riwayat(path)


class TestCLI(unittest.TestCase):
    def test_hitung_lalu_simpan(self):
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, "r.json")
            masukan = ["", "", "", "u", "", "q"]          # 3x tambah, undo, tambah -> 3
            with mock.patch("builtins.input", side_effect=masukan), redirect_stdout(io.StringIO()) as out:
                kode = tasbih.main(["--target", "3", "--file", path, "--tanpa-bel"])
            self.assertEqual(kode, 0)
            self.assertIn("Target 3 tercapai", out.getvalue())
            self.assertEqual(muat_riwayat(path)[date.today().isoformat()], {"tasbih": 3})

    def test_eof_dianggap_selesai(self):
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, "r.json")
            with mock.patch("builtins.input", side_effect=["", EOFError()]), redirect_stdout(io.StringIO()):
                kode = tasbih.main(["--dzikir", "istighfar", "--file", path, "--tanpa-bel"])
            self.assertEqual(kode, 0)
            self.assertEqual(muat_riwayat(path)[date.today().isoformat()], {"istighfar": 1})

    def test_riwayat_rusak_exit_code_bukan_nol(self):
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, "r.json")
            with open(path, "w", encoding="utf-8") as f:
                f.write("[]")
            with redirect_stdout(io.StringIO()), mock.patch("sys.stderr", new=io.StringIO()) as err:
                kode = tasbih.main(["--riwayat", "--file", path])
            self.assertEqual(kode, 1)
            self.assertIn("rusak", err.getvalue())


if __name__ == "__main__":
    unittest.main()
