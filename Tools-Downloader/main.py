#!/usr/bin/env python3
"""
SlideShare Scraper - Auto ChromeDriver (Windows & Linux Compatible)
Menggunakan webdriver-manager untuk otomatis download chromedriver
Install: pip install webdriver-manager
"""

import json
import logging
import requests
import time
import os
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from webdriver_manager.chrome import ChromeDriverManager
import re
from urllib.parse import urlparse
from PIL import Image
from io import BytesIO
import img2pdf

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class SlideShareScraper:
    def __init__(self, url, output_file='image_data.json'):
        self.url = url
        self.output_file = output_file
        self.image_urls = []
        self.image_data = []
        self.driver = None
        self.file_name = None
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })

    def setup_driver(self):
        """Setup Chrome driver dengan webdriver-manager (cross-platform)"""
        chrome_options = Options()
        
        chrome_options.add_argument('--disable-notifications')
        chrome_options.add_argument('--disable-popup-blocking')
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-gpu')  # Prevent GPU issues
        chrome_options.add_argument('--log-level=3')  # Suppress SSL warnings
        chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])  # Suppress DevTools
        
        # Set page load strategy untuk faster loading
        chrome_options.page_load_strategy = 'eager'
        
        logger.info("Starting Chrome driver...")
        print("⚙️  Initializing Chrome driver...\n")
        
        try:
            # Webdriver-manager otomatis download dan setup chromedriver
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            self.driver.set_page_load_timeout(60)  # 60 second timeout
            self.driver.implicitly_wait(10)  # Implicit wait
            self.driver.maximize_window()
            print("✅ Chrome driver started\n")
        except Exception as e:
            print(f"❌ Error: {e}")
            print("\n💡 Please install webdriver-manager:")
            print("   pip install webdriver-manager")
            raise

    def open_slideshare(self):
        """Buka SlideShare link di browser"""
        max_retries = 3
        for attempt in range(max_retries):
            try:
                print(f"🌐 Opening SlideShare link...\n")
                print(f"   URL: {self.url}\n")
                
                self.driver.get(self.url)
                
                # Tunggu halaman load
                wait = WebDriverWait(self.driver, 30)
                wait.until(EC.presence_of_all_elements_located((By.TAG_NAME, "body")))
                
                print("⏳ Waiting for page to load...\n")
                time.sleep(3)  # Reduced from 5 to 3
                
                print("✅ Page loaded successfully\n")
                
                # Extract nama file dari H1 element
                self.extract_file_name()
                return
                
            except Exception as e:
                if attempt < max_retries - 1:
                    print(f"⚠️  Attempt {attempt + 1} failed: {e}")
                    print(f"   Retrying in 3 seconds...\n")
                    time.sleep(3)
                else:
                    raise
    
    def extract_file_name(self):
        """Extract nama file dari H1 element dengan class Metadata_title"""
        try:
            js_script = """
            var h1 = document.querySelector('h1.Metadata_title__aM3nZ');
            if (h1) {
                return h1.innerText;
            }
            var allH1 = document.querySelectorAll('h1');
            for (var i = 0; i < allH1.length; i++) {
                var text = allH1[i].innerText.trim();
                if (text && text.length > 0 && !text.toLowerCase().includes('share') && !text.toLowerCase().includes('slideshare')) {
                    return text;
                }
            }
            return null;
            """
            
            file_name = self.driver.execute_script(js_script)
            
            if file_name:
                self.file_name = file_name.strip()
                print(f"📄 File name extracted: {self.file_name}\n")
            else:
                self.file_name = "slides"
                print(f"⚠️  Could not extract file name, using default: {self.file_name}\n")
                
        except Exception as e:
            print(f"⚠️  Error extracting file name: {e}")
            self.file_name = "slides"

    def extract_image_urls(self):
        """Extract high-res slide image URLs dengan scroll optimized dan incremental extraction"""
        try:
            print("🔍 Extracting image URLs via optimized scroll...\n")
            
            # Set untuk tracking URLs unik (high-res slides only)
            found_urls = set()
            
            # Scroll parameters (lebih cepat untuk prevent timeout)
            scroll_pause_time = 2  # Dikurangi dari 5 ke 2 detik
            scroll_increment = 400  # Diperbesar dari 200 ke 400px
            current_position = 0
            scroll_count = 0
            same_count = 0
            max_same = 3  # Stop jika URL tidak bertambah 3x berturut-turut
            
            print(f"   Scroll strategy: {scroll_increment}px every {scroll_pause_time}s\n")
            
            # Reset scroll position
            try:
                self.driver.execute_script("window.scrollTo(0, 0);")
                time.sleep(1)
            except:
                pass
            
            # Scroll loop dengan incremental extraction
            while True:
                try:
                    # Get current scroll info
                    scroll_info = self.driver.execute_script("""
                        return {
                            scrollY: window.scrollY,
                            scrollHeight: Math.max(
                                document.body.scrollHeight,
                                document.documentElement.scrollHeight
                            )
                        };
                    """)
                    
                    current_y = scroll_info['scrollY']
                    total_height = scroll_info['scrollHeight']
                    
                    # Extract URLs setiap scroll (incremental)
                    js_extract = """
                    var urls = [];
                    var imgs = document.querySelectorAll('img');
                    for (var i = 0; i < imgs.length; i++) {
                        var src = imgs[i].src;
                        // Filter untuk high-res slides: image.slidesharecdn.com + -2048.jpg
                        if (src && src.includes('image.slidesharecdn.com') && src.includes('-2048.jpg')) {
                            urls.push(src);
                        }
                    }
                    return urls;
                    """
                    
                    new_urls = self.driver.execute_script(js_extract)
                    old_count = len(found_urls)
                    found_urls.update(new_urls)
                    new_count = len(found_urls)
                    
                    if new_count > old_count:
                        print(f"   📸 Found {new_count} high-res slides (+{new_count - old_count})")
                        same_count = 0  # Reset counter
                    else:
                        same_count += 1
                    
                    # Progress info
                    print(f"   Scroll: {current_y}px / {total_height}px (iteration: {scroll_count})", end='\r')
                    
                    # Check stopping conditions
                    if same_count >= max_same:
                        print(f"\n   ⚠️  No new images found for {max_same} iterations, stopping...")
                        break
                    
                    if current_y + 1000 >= total_height:
                        print(f"\n   ✅ Reached end of page")
                        break
                    
                    # Scroll down
                    current_position = current_y + scroll_increment
                    self.driver.execute_script(f"window.scrollTo(0, {current_position});")
                    scroll_count += 1
                    
                    # Prevent infinite loop
                    if scroll_count > 200:
                        print(f"\n   ⚠️  Max scroll iterations reached (200)")
                        break
                    
                    time.sleep(scroll_pause_time)
                    
                except Exception as e:
                    print(f"\n   ⚠️  Scroll error: {e}")
                    # Try to continue despite error
                    break
            
            # Final extraction pass
            print(f"\n\n   🔍 Final extraction pass...")
            try:
                final_urls = self.driver.execute_script("""
                    var urls = [];
                    var imgs = document.querySelectorAll('img');
                    for (var i = 0; i < imgs.length; i++) {
                        var src = imgs[i].src;
                        if (src && src.includes('image.slidesharecdn.com') && src.includes('-2048.jpg')) {
                            urls.push(src);
                        }
                    }
                    return urls;
                """)
                found_urls.update(final_urls)
            except Exception as e:
                print(f"   ⚠️  Final extraction warning: {e}")
            
            # Sort URLs by slide number
            def get_slide_num(url):
                import re
                match = re.search(r'-(\d+)-2048\.jpg', url)
                return int(match.group(1)) if match else 999999
            
            self.image_urls = sorted(list(found_urls), key=get_slide_num)
            
            print(f"\n   Total scroll iterations: {scroll_count}")
            print(f"   Total high-res slide images: {len(self.image_urls)}\n")
            
            if len(self.image_urls) > 0:
                print(f"✅ Image URLs extracted: {len(self.image_urls)} slides\n")
                for idx, url in enumerate(self.image_urls[:5], 1):
                    slide_num = get_slide_num(url)
                    print(f"   [{idx}] Slide {slide_num}: {url.split('/')[-1]}")
                if len(self.image_urls) > 5:
                    print(f"   ... and {len(self.image_urls) - 5} more slides\n")
                else:
                    print()
            else:
                print("⚠️  No high-res slide images found!\n")
            
            return len(self.image_urls) > 0
            
        except Exception as e:
            print(f"❌ Error extracting image URLs: {e}")
            import traceback
            traceback.print_exc()
            return False

    def get_image_data(self):
        """Fetch image data menggunakan GET request dengan cookies/session dari browser"""
        try:
            print("=" * 100)
            print("📥 FETCHING IMAGE DATA")
            print("=" * 100 + "\n")
            
            if not self.image_urls:
                print("⚠️  No image URLs found!")
                return False
            
            print(f"Fetching {len(self.image_urls)} images...\n")
            
            cookies = self.driver.get_cookies()
            cookie_dict = {cookie['name']: cookie['value'] for cookie in cookies}
            
            for idx, url in enumerate(self.image_urls, 1):
                try:
                    print(f"[{idx}/{len(self.image_urls)}] Fetching: {url[:80]}...")
                    
                    response = self.session.get(
                        url, 
                        timeout=10,
                        cookies=cookie_dict,
                        allow_redirects=True
                    )
                    
                    data = {
                        'index': idx,
                        'url': url,
                        'status_code': response.status_code,
                        'content_length': len(response.content),
                        'content_type': response.headers.get('Content-Type', 'Unknown'),
                        'timestamp': datetime.now().isoformat(),
                        'accessible': response.status_code == 200
                    }
                    
                    if response.status_code == 200:
                        print(f"   ✅ Success | Size: {len(response.content)} bytes | Type: {data['content_type']}")
                        self.image_data.append(data)
                    else:
                        print(f"   ⚠️  Status: {response.status_code}")
                        self.image_data.append(data)
                    
                except requests.Timeout:
                    print(f"   ❌ Timeout")
                    data = {
                        'index': idx,
                        'url': url,
                        'status_code': 'TIMEOUT',
                        'error': 'Request timeout',
                        'timestamp': datetime.now().isoformat(),
                        'accessible': False
                    }
                    self.image_data.append(data)
                    
                except Exception as e:
                    print(f"   ❌ Error: {str(e)}")
                    data = {
                        'index': idx,
                        'url': url,
                        'error': str(e),
                        'timestamp': datetime.now().isoformat(),
                        'accessible': False
                    }
                    self.image_data.append(data)
                
                time.sleep(0.5)
            
            return len(self.image_data) > 0
            
        except Exception as e:
            print(f"❌ Error getting image data: {e}")
            return False

    def display_results(self):
        """Tampilkan hasil di terminal"""
        print("\n" + "=" * 100)
        print("📊 HASIL SCRAPING")
        print("=" * 100 + "\n")
        
        print(f"Total URLs extracted: {len(self.image_urls)}")
        print(f"Total data fetched: {len(self.image_data)}\n")
        
        success_count = sum(1 for d in self.image_data if d.get('status_code') == 200)
        print(f"✅ Successful requests: {success_count}")
        print(f"❌ Failed requests: {len(self.image_data) - success_count}\n")
        
        print("=" * 100)
        print("📋 IMAGE DATA DETAILS")
        print("=" * 100 + "\n")
        
        for data in self.image_data:
            print(f"[{data.get('index')}] URL: {data.get('url')}")
            print(f"    Status: {data.get('status_code')}")
            print(f"    Content-Type: {data.get('content_type', 'N/A')}")
            print(f"    Size: {data.get('content_length', 'N/A')} bytes")
            if 'error' in data:
                print(f"    Error: {data.get('error')}")
            print()
        
        print("\n" + "=" * 100)
        print("📈 SUMMARY")
        print("=" * 100 + "\n")
        
        total_size = sum(d.get('content_length', 0) for d in self.image_data if isinstance(d.get('content_length'), int))
        print(f"Total data size: {total_size / (1024*1024):.2f} MB")
        print(f"Average size per image: {total_size / len(self.image_data) if self.image_data else 0 / (1024):.2f} KB\n")

    def save_results(self):
        """Simpan hasil ke JSON file"""
        try:
            output = {
                'url': self.url,
                'timestamp': datetime.now().isoformat(),
                'total_urls_extracted': len(self.image_urls),
                'total_fetched': len(self.image_data),
                'image_data': self.image_data
            }
            
            with open(self.output_file, 'w', encoding='utf-8') as f:
                json.dump(output, f, indent=2, ensure_ascii=False)
            
            print(f"✅ Results saved to {self.output_file}\n")
            
        except Exception as e:
            print(f"❌ Error saving results: {e}")

    def close_driver(self):
        """Close browser"""
        try:
            if self.driver:
                self.driver.quit()
                print("🔒 Browser closed\n")
        except Exception as e:
            print(f"⚠️  Error closing browser: {e}\n")
    
    def convert_to_pdf(self, image_files, output_dir=None):
        """Convert semua images ke 1 file PDF"""
        try:
            if not image_files:
                print("⚠️  No images to convert to PDF!")
                return None
            
            if output_dir is None:
                output_dir = os.path.join('download', self.file_name or 'slides')
            
            # Nama file PDF berdasarkan nama slides
            pdf_filename = f"{self.file_name or 'slides'}.pdf"
            pdf_path = os.path.join(output_dir, pdf_filename)
            
            print("=" * 100)
            print("📄 CONVERTING TO PDF")
            print("=" * 100 + "\n")
            
            print(f"Converting {len(image_files)} images to PDF...\n")
            print(f"Output: {pdf_path}\n")
            
            # Convert ke PDF menggunakan img2pdf
            with open(pdf_path, "wb") as pdf_file:
                pdf_file.write(img2pdf.convert(image_files))
            
            pdf_size = os.path.getsize(pdf_path)
            print(f"✅ PDF created successfully!")
            print(f"   File: {pdf_filename}")
            print(f"   Size: {pdf_size / (1024*1024):.2f} MB")
            print(f"   Pages: {len(image_files)}\n")
            
            return pdf_path
            
        except Exception as e:
            print(f"❌ Error converting to PDF: {e}")
            import traceback
            traceback.print_exc()
            return None

    def download_images(self, output_dir=None):
        """Download langsung image URLs yang sudah di-extract secara urut"""
        try:
            if output_dir is None:
                output_dir = os.path.join('download', self.file_name or 'slides')
            
            print("=" * 100)
            print("💾 DOWNLOADING HIGH-RES IMAGES (Direct Download)")
            print("=" * 100 + "\n")
            
            if not self.image_urls:
                print("⚠️  No image URLs to download!")
                return []
            
            print(f"📁 Output directory: {output_dir}\n")
            print(f"Total images to download: {len(self.image_urls)}\n")
            
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)
                print(f"✅ Created directory: {output_dir}\n")
            
            # Get cookies dari browser untuk authentikasi
            cookies = self.driver.get_cookies()
            cookie_dict = {cookie['name']: cookie['value'] for cookie in cookies}
            
            downloaded_files = []
            
            for idx, url in enumerate(self.image_urls, 1):
                try:
                    filename = f"slide_{idx:03d}.jpg"
                    filepath = os.path.join(output_dir, filename)
                    
                    print(f"[{idx}/{len(self.image_urls)}] Downloading: {filename}...", end=' ')
                    
                    # Download image
                    response = self.session.get(
                        url,
                        timeout=15,
                        cookies=cookie_dict,
                        allow_redirects=True,
                        stream=True
                    )
                    
                    if response.status_code == 200:
                        # Convert ke RGB JPG untuk konsistensi
                        img = Image.open(BytesIO(response.content))
                        
                        # Convert semua mode ke RGB
                        if img.mode in ('RGBA', 'LA', 'P'):
                            background = Image.new('RGB', img.size, (255, 255, 255))
                            if img.mode == 'P':
                                img = img.convert('RGBA')
                            if img.mode == 'RGBA':
                                background.paste(img, mask=img.split()[-1])
                                img = background
                            else:
                                img = img.convert('RGB')
                        elif img.mode != 'RGB':
                            img = img.convert('RGB')
                        
                        # Save sebagai JPG quality tinggi
                        img.save(filepath, 'JPEG', quality=95, optimize=True)
                        file_size = os.path.getsize(filepath)
                        
                        print(f"✅ {file_size:,} bytes")
                        downloaded_files.append(filepath)
                        
                    else:
                        print(f"❌ HTTP {response.status_code}")
                    
                except Exception as e:
                    print(f"❌ Error: {str(e)}")
                    continue
                
                # Rate limiting
                time.sleep(0.3)
            
            print(f"\n✅ Successfully downloaded {len(downloaded_files)}/{len(self.image_urls)} images\n")
            return downloaded_files
            
        except Exception as e:
            print(f"❌ Error downloading images: {e}")
            import traceback
            traceback.print_exc()
            return []

    def run(self):
        """Main execution - Extract URLs → Download → Convert to PDF"""
        try:
            print("\n" + "=" * 100)
            print("🚀 SLIDESHARE SCRAPER (Direct Download + PDF Conversion)")
            print("=" * 100 + "\n")
            
            # Step 1: Setup driver
            self.setup_driver()
            
            # Step 2: Open page
            self.open_slideshare()
            
            # Step 3: Extract image URLs
            if not self.extract_image_urls():
                print("⚠️  No images found on page")
                return False
            
            # Step 4: Download images langsung (skip get_image_data karena tidak perlu)
            downloaded_files = self.download_images()
            
            if not downloaded_files:
                print("⚠️  No images downloaded")
                return False
            
            # Step 5: Convert to PDF
            pdf_path = self.convert_to_pdf(downloaded_files)
            
            if pdf_path:
                print("=" * 100)
                print("✅ SCRAPING COMPLETED SUCCESSFULLY!")
                print("=" * 100)
                print(f"\n📊 Summary:")
                print(f"   • Slides extracted: {len(self.image_urls)}")
                print(f"   • Images downloaded: {len(downloaded_files)}")
                print(f"   • PDF file: {os.path.basename(pdf_path)}")
                print(f"   • Location: {os.path.dirname(pdf_path)}\n")
                print("=" * 100 + "\n")
                return True
            else:
                print("⚠️  PDF conversion failed")
                return False
            
        except Exception as e:
            print(f"❌ Error during scraping: {e}")
            import traceback
            traceback.print_exc()
            return False
        finally:
            try:
                self.close_driver()
            except:
                pass


def main():
    slideshare_url = [
        "https://www.slideshare.net/slideshow/materi-ppt-bentuk-aljabar-kelas-7-kurikulum-merdeka/267115139",
        "https://www.slideshare.net/slideshow/ppt-materi-spldvpptx/251499584#14",
        "https://www.slideshare.net/slideshow/ppt-spldv-kelas-viii/249256255"
    ]
    
    print("\n" + "=" * 100)
    print("🚀 BATCH SLIDESHARE SCRAPER (Optimized + Auto PDF)")
    print("=" * 100)
    print(f"\nTotal URLs to process: {len(slideshare_url)}")
    print(f"Features:")
    print(f"  • Fast scroll (400px/2s) with incremental extraction")
    print(f"  • High-res images only (-2048.jpg quality)")
    print(f"  • Direct download with sequential naming (slide_001.jpg, slide_002.jpg, ...)")
    print(f"  • Auto-convert to single PDF file after download")
    print(f"  • Smart stopping (no new images for 3 iterations)\n")
    
    success_count = 0
    failed_count = 0
    failed_urls = []
    
    for i, url in enumerate(slideshare_url, 1):
        print(f"\n{'='*100}")
        print(f"[{i}/{len(slideshare_url)}] Processing URL...")
        print(f"{'='*100}")
        
        try:
            scraper = SlideShareScraper(url)
            result = scraper.run()
            
            if result:
                success_count += 1
            else:
                failed_count += 1
                failed_urls.append(url)
            
        except KeyboardInterrupt:
            print("\n\n⚠️  Process interrupted by user (Ctrl+C)")
            failed_count += 1
            failed_urls.append(url)
            break
            
        except Exception as e:
            print(f"\n❌ Error processing URL {i}: {str(e)}")
            print(f"   URL: {url}")
            failed_count += 1
            failed_urls.append(url)
            
            # Ask user if they want to continue
            try:
                response = input("\nContinue to next URL? (Y/n): ").strip().lower()
                if response == 'n':
                    break
            except:
                # If input fails, continue anyway
                pass
    
    print("\n" + "=" * 100)
    print("📊 BATCH PROCESSING SUMMARY")
    print("=" * 100)
    print(f"\nTotal URLs: {len(slideshare_url)}")
    print(f"✅ Successful: {success_count}")
    print(f"❌ Failed: {failed_count}")
    
    if failed_urls:
        print(f"\nFailed URLs:")
        for url in failed_urls:
            print(f"  - {url}")
    
    print(f"\n{'='*100}\n")


if __name__ == "__main__":
    main()
