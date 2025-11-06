# Pollinations CLI

A command-line interface to interact with Pollinations API.

## Cara Penggunaan

```cmd
polli-cli.exe "a little asian girl smile face big eye" -o my_image.jpeg

polli-cli.exe "a futuristic city" -m flux -S 768x768 --seed 12345

polli-cli.exe -c 3 "a cat astronaut" --output images/cats/

polli-cli.exe -t 2 -c 2 "a dog in a park" --log-file generation_log.jsonl
```

## Parameter Lengkap

| Argumen Panjang | Argumen Pendek | Tipe | Default | Deskripsi |
| :-------------- | :------------- | :--- | :------ | :---------- |
| `prompt`        |                | `str`|         | Prompt utama untuk pembuatan gambar. Bisa berupa string, path ke file teks, atau `-` untuk membaca dari stdin. |
| `--model`       | `-m`           | `str`| `flux`  | Model yang akan digunakan untuk generasi. |
| `--size`        | `-S`           | `WxH`| `1024x1024`| Ukuran gambar yang dihasilkan dalam format WxH (misalnya, 512x512). |
| `--seed`        | `-s`           | `int`| Random  | Seed untuk randomisasi. Seed acak akan digunakan jika tidak disediakan. |
| `--logo`        |                | `bool`| `True`  | Tambahkan logo ke gambar. Gunakan `--no-logo` untuk menghapus logo. |
| `--private`     |                | `bool`| `False` | Jadikan gambar pribadi (default adalah publik). |
| `--safe`        |                | `bool`| `False` | Aktifkan mode aman. |
| `--referrer`    |                | `str`| `pollinations-cli-requests` | Atur referrer. |
| `--enhance`     |                | `bool`| `True`  | Aktifkan peningkatan gambar. |
| `--negative`    | `-n`           | `str`| `""`    | Prompt negatif. |
| `--output`      | `-o`           | `str`| Random  | Nama file output. Jika tidak disediakan, nama acak akan dibuat. Untuk multi-generasi, ini harus berupa direktori. |
| `--no-save`     |                | `bool`| `False` | Jangan simpan gambar ke file. |
| `--count`       | `-c`           | `int`| `1`     | Jumlah gambar yang akan dihasilkan per prompt. |
| `--retries`     | `-r`           | `int`| `3`     | Jumlah percobaan ulang untuk generasi jika gagal. |
| `--retry-delay` |                | `int`| `5`     | Penundaan dalam detik antara percobaan ulang. |
| `--threads`     | `-t`           | `int`| `1`     | Jumlah thread bersamaan yang akan digunakan untuk generasi batch. (Maksimum yang direkomendasikan adalah 2). |
| `--log-file`    |                | `str`|         | Path ke file untuk mencatat detail generasi (dalam format JSON Lines). |
| `--timeout`     |                | `int`| `60`    | Batas waktu untuk permintaan API dalam detik. |

## Kompilasi Executable

ikuti intruksi ini untuk mengkompilasinya menjadi executable:

- install uv `powershell -c "irm https://astral.sh/uv/install.ps1 | more"`
- jalankan uv: `uv sync`
- jalankan program: `uv run build/build_binary.py`

*Executable* yang dihasilkan akan berada di direktori `dist/`.

## ⬇️ Unduh Executable

Anda dapat mengunduh executable: [mediafire](https://www.mediafire.com/file/ukkhar7uyiohk4n/polli-cli.zip/file).

## Beri Dukungan

[![Buka Halaman Donasi](https://irfanykywz.github.io/donate/donate.png)](https://irfanykywz.github.io/donate/)