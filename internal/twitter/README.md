# Twitter User Stats Checker

Script untuk mengecek jumlah tweet dan reply dari user Twitter lain menggunakan API web Twitter.

## Fitur

- ✅ Cek jumlah followers
- ✅ Cek jumlah tweets (post asli)
- ✅ Cek jumlah replies (balasan ke tweet lain)
- ✅ Cek total posts
- ✅ Lihat 10 tweet terbaru
- ✅ Support multiple users sekaligus
- ✅ Interface dalam Bahasa Indonesia

## Cara Menggunakan

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Dapatkan Auth Token dari Browser

1. Buka Twitter.com di browser
2. Login ke akun Twitter kamu
3. Tekan F12 untuk buka Developer Tools
4. Buka tab "Application" atau "Storage"
5. Cari "Cookies" → "https://twitter.com"
6. Copy nilai dari cookie `auth_token`
7. Copy nilai dari cookie `ct0` (optional)

### 3. Jalankan Script

```bash
python check_user_stats.py
```

### 4. Masukkan Informasi

- **Auth Token**: Paste auth_token yang sudah di-copy
- **CT0 Token**: Paste ct0 token (bisa dikosongkan)
- **Proxy URL**: URL proxy jika diperlukan (bisa dikosongkan)

### 5. Pilih Menu

- **Menu 1**: Cek statistik satu user
- **Menu 2**: Cek statistik multiple users (pisahkan username dengan koma)
- **Menu 3**: Keluar

## Contoh Output

```
📊 Statistik @username:
   👥 Followers: 1,234
   🐦 Tweets: 45
   💬 Replies: 23
   📝 Total Posts: 68

🕒 10 Tweet Terbaru:
   1. 🐦 Ini adalah tweet asli...
      🔗 https://x.com/username/status/123456
   2. 💬 Ini adalah reply ke tweet lain...
      🔗 https://x.com/username/status/123457
```

## Catatan Penting

- Script ini menggunakan API web Twitter, bukan API v2
- Pastikan akun Twitter kamu tidak dalam status suspended/restricted
- Jangan terlalu sering request untuk menghindari rate limiting
- Script hanya bisa mengakses data public user
- Untuk user private, data tidak akan bisa diakses

## Troubleshooting

### Error "Failed to get ct0"
- Pastikan auth_token valid dan belum expired
- Coba refresh halaman Twitter dan ambil auth_token baru

### Error "User not found"
- Username mungkin salah atau akun private
- Pastikan username tanpa @ di awal

### Error "Rate limit exceeded"
- Tunggu beberapa menit sebelum request lagi
- Gunakan proxy jika diperlukan

## Disclaimer

Script ini dibuat untuk tujuan edukasi dan analisis data. Gunakan dengan bijak dan sesuai dengan Terms of Service Twitter. 