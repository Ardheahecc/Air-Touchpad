# 🛸 Air Touchpad

Air Touchpad Pro adalah aplikasi utilitas berbasis *Computer Vision* yang menyulap webcam Anda menjadi sensor gerak cerdas. Kendalikan kursor mouse, lakukan klik, gulir halaman, hingga mengontrol musik hanya dengan gestur tangan di udara!

## ✨ Fitur Utama
* **Two-Hand Control Architecture:** Pembagian tugas yang natural (Tangan Kiri untuk navigasi kursor, Tangan Kanan untuk eksekusi aksi).
* **Adaptive Pointer Precision:** Kecepatan kursor dinamis (cepat saat mengayun, presisi/lambat saat membidik target kecil).
* **Smart Media Control:** Atur volume dan ganti lagu (*Next/Prev*) menggunakan ayunan jari dari jarak jauh.
* **On-Screen Keyboard & Multitasking:** Panggil keyboard virtual dan buka *Task View* (App Switcher) murni menggunakan gestur jari.
* **Picture-in-Picture (PiP) Transparan:** Jendela kamera tidak akan menutupi pekerjaan Anda dan selalu *stay-on-top*.

## 🛠️ Teknologi yang Digunakan
* **Python 3.x**
* **OpenCV** (Pengolahan gambar & UI)
* **MediaPipe** (Pelacakan sendi tangan/Biometrik)
* **PyAutoGUI** (Automasi sistem operasi)

## 🚀 Cara Instalasi

1. *Clone* repositori ini:
   ```bash
   git clone [https://github.com/Ardheahecc/Air-Touchpad.git](https://github.com/Ardheahecc/Air-Touchpad.git)

2. Masuk ke direktori proyek:
   ```bash
   cd Air-Touchpad-Pro

3. Buat dan aktifkan Virtual Environment (Direkomendasikan):
   ```bash
   python -m venv venv
   # Windows:
   .\venv\Scripts\activate

4. Instal semua pustaka yang dibutuhkan:
   ```bash
   pip install -r requirements.txt

5. Jalankan aplikasi:
   ```bash
   python main.py
