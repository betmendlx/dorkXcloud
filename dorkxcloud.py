import argparse
import requests
import bs4
import urllib.parse
import re
import sys
from time import sleep
import pyfiglet
from fake_useragent import UserAgent

# Membuat banner DorkXcloud dengan figlet
banner = pyfiglet.figlet_format("DorkXcloud", font="slant")
print('\033[92m' + banner + '\033[00m')

# Membuat parser argumen
parser = argparse.ArgumentParser(description='Google Dork Script by dorkXcloud')

# Menambahkan argumen input
parser.add_argument('-d', '--dork', type=str, help='Tentukan dork pencarian.')
parser.add_argument('-p', '--pages', type=int, default=3, help='Jumlah halaman hasil pencarian yang akan diambil (default: 3).')
parser.add_argument('-o', '--output', type=str, help='Simpan hasil ke file teks.')
parser.add_argument('-t', '--timeout', type=int, default=5, help='Timeout untuk setiap request (default: 5 detik).')
parser.add_argument('-v', '--verbose', action='store_true', help='Tampilkan informasi tambahan selama proses.')
parser.add_argument('-u', '--user-agent', type=str, help='User-Agent kustom untuk request (opsional).')

# Parsing argumen dari command line
args = parser.parse_args()

# Memeriksa apakah argumen dork diberikan
if not args.dork:
    parser.error('Query pencarian (-d/--dork) diperlukan.')

# Mengambil query pencarian dari argumen command line
dork = args.dork

# Mengkonversi query pencarian ke format URL-encoded
encoded_query = urllib.parse.quote(dork)
print("Dork : " '\033[93m' + dork + '\033[00m\n')

# Mendefinisikan parameter yang akan dihapus dari URL
params_to_remove = ['sa', 'ved', 'usg']

# Inisialisasi list untuk menyimpan hasil
results = []

# Membuat objek UserAgent untuk menghasilkan random User-Agent
ua = UserAgent()

# Fungsi untuk mendapatkan User-Agent
def get_user_agent():
    if args.user_agent:  # Jika User-Agent kustom diberikan
        return args.user_agent
    else:  # Gunakan random User-Agent
        return ua.random

# Iterasi melalui halaman hasil pencarian
for page in range(args.pages):
    if args.verbose:
        print(f"Mengambil halaman {page + 1} dari {args.pages}...")

    # Menghitung indeks awal untuk halaman saat ini
    start = page * 10

    # Membangun URL pencarian Google untuk halaman saat ini
    url = f'https://google.com/search?q={encoded_query}&start={start}'

    try:
        # Mengirim GET request ke URL dengan random User-Agent
        headers = {'User-Agent': get_user_agent()}
        if args.verbose:
            print(f"Menggunakan User-Agent: {headers['User-Agent']}")
        request_result = requests.get(url, headers=headers, timeout=args.timeout)

        # Membuat objek BeautifulSoup dari HTML response
        soup = bs4.BeautifulSoup(request_result.text, "html.parser")

        # Mencari semua tag anchor (link) dalam hasil pencarian
        link_tags = soup.find_all('a')

        # Iterasi melalui tag link dan mengekstrak URL
        for link_tag in link_tags:
            href = link_tag.get('href')
            if href and href.startswith('/url?q='):  # Mengekstrak URL dari atribut href
                url = href[7:]  # Menghapus prefix '/url?q='
                url = urllib.parse.unquote(url)  # Mendekode karakter URL-encoded

                # Mengecualikan URL tertentu
                if not (url.startswith('https://www.google.com') or
                        url.startswith('https://support.google.com') or
                        url.startswith('https://github.com') or
                        url.startswith('https://stackoverflow.com') or
                        url.startswith('https://accounts.google.com')):
                    # Menghapus parameter yang tidak diinginkan
                    cleaned_url = re.sub(r'&?(?:{})=.*?(?=&|$)'.format('|'.join(params_to_remove)), '', url)
                    results.append(cleaned_url)
                    print(cleaned_url)

        # Jeda untuk menghindari blokir oleh Google
        sleep(2)

    except requests.exceptions.RequestException as e:
        print(f"Error: {e}", file=sys.stderr)
        continue

# Menyimpan hasil ke file jika argumen output diberikan
if args.output:
    with open(args.output, 'w') as file:
        for result in results:
            file.write(result + '\n')
    print(f"\nHasil disimpan ke {args.output}")

print("\nPencarian selesai!")
