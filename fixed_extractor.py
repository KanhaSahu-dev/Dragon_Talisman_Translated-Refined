import requests
import urllib3
from bs4 import BeautifulSoup
import os
import time
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
import re

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class FixedChapterExtractor:
    def __init__(self, base_url='https://novelhi.com/s/Dragon-Talisman', output_folder='Extracted_Chapters_Fixed', max_workers=8):
        self.base_url = base_url
        self.output_folder = output_folder
        self.max_workers = max_workers
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)
        
        self.success_count = 0
        self.error_count = 0
        self.lock = threading.Lock()
    
    def extract_single_chapter(self, chapter_num):
        url = f'{self.base_url}/{chapter_num}'
        
        try:
            response = self.session.get(url, verify=False, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Get title
            title = soup.find('h1')
            title_text = title.get_text().strip() if title else f'Chapter {chapter_num}'
            
            # CRITICAL FIX: Look for the correct content container
            content_div = soup.find('div', {'id': 'showReading'})
            if not content_div:
                content_div = soup.find('div', class_='readBox')
            
            if content_div:
                # Extract all <sent> elements which contain the actual content
                sent_elements = content_div.find_all('sent')
                
                if sent_elements:
                    # Combine all sentences into paragraphs
                    content_parts = []
                    current_paragraph = []
                    
                    for sent in sent_elements:
                        sent_text = sent.get_text().strip()
                        if sent_text:
                            # Check if this should start a new paragraph
                            if (sent_text.startswith('"') and current_paragraph and 
                                not current_paragraph[-1].endswith('"')):
                                # Start new paragraph for dialogue
                                if current_paragraph:
                                    content_parts.append(' '.join(current_paragraph))
                                    current_paragraph = [sent_text]
                                else:
                                    current_paragraph.append(sent_text)
                            elif len(sent_text) > 100 and current_paragraph:
                                # Long sentences often start new paragraphs
                                content_parts.append(' '.join(current_paragraph))
                                current_paragraph = [sent_text]
                            else:
                                current_paragraph.append(sent_text)
                    
                    # Add the last paragraph
                    if current_paragraph:
                        content_parts.append(' '.join(current_paragraph))
                    
                    # Join paragraphs with double newlines
                    content = '\n\n'.join(content_parts)
                else:
                    # Fallback: get all text from the div
                    content = content_div.get_text().strip()
                    # Remove script tags and ads
                    content = re.sub(r'<script.*?</script>', '', content, flags=re.DOTALL)
                    content = re.sub(r'<ins.*?</ins>', '', content, flags=re.DOTALL)
                
                # Clean up the content
                content = self.clean_content(content)
                
                if len(content) > 100:  # Only save if we have substantial content
                    filename = f'{self.output_folder}/Chapter_{chapter_num:03d}.txt'
                    with open(filename, 'w', encoding='utf-8') as f:
                        f.write(f'{title_text}\n')
                        f.write('=' * len(title_text) + '\n\n')
                        f.write(content)
                    
                    with self.lock:
                        self.success_count += 1
                        if self.success_count % 10 == 0:
                            print(f' Fixed extraction: {self.success_count} chapters... (Latest: Chapter {chapter_num}, {len(content)} chars)')
                    
                    return True, chapter_num, None
                else:
                    with self.lock:
                        self.error_count += 1
                    return False, chapter_num, f'Insufficient content: {len(content)} chars'
            else:
                with self.lock:
                    self.error_count += 1
                return False, chapter_num, 'No content container found'
                
        except Exception as e:
            with self.lock:
                self.error_count += 1
            return False, chapter_num, str(e)
    
    def clean_content(self, content):
        # Remove unwanted elements but preserve the story content
        unwanted_patterns = [
            r'Remember the mobile version:.*',
            r'<script.*?</script>',
            r'<ins.*?</ins>',
            r'adsbygoogle',
            r'googlesyndication',
            r'data-ad-.*?=".*?"',
            r'crossorigin="anonymous"',
        ]
        
        for pattern in unwanted_patterns:
            content = re.sub(pattern, '', content, flags=re.DOTALL | re.IGNORECASE)
        
        # Clean up extra spaces and line breaks
        content = re.sub(r'\n\s*\n\s*\n+', '\n\n', content)
        content = re.sub(r'[ \t]+', ' ', content)
        content = content.strip()
        
        return content
    
    def extract_chapters_parallel(self, start_chapter, end_chapter):
        print(f' FIXED Chapter Extractor - Complete Content Extraction!')
        print(f' Extracting chapters {start_chapter} to {end_chapter}')
        print(f' Using {self.max_workers} parallel workers')
        print(f' Total chapters to extract: {end_chapter - start_chapter + 1}')
        print(' This will extract the COMPLETE chapter content (not the truncated version)')
        print('=' * 70)
        
        start_time = time.time()
        
        chapter_range = list(range(start_chapter, end_chapter + 1))
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_chapter = {
                executor.submit(self.extract_single_chapter, chapter_num): chapter_num 
                for chapter_num in chapter_range
            }
            
            completed = 0
            total = len(chapter_range)
            
            for future in as_completed(future_to_chapter):
                completed += 1
                success, chapter_num, error = future.result()
                
                if completed % 50 == 0 or completed == total:
                    elapsed = time.time() - start_time
                    rate = completed / elapsed if elapsed > 0 else 0
                    eta = (total - completed) / rate if rate > 0 else 0
                    
                    print(f' Progress: {completed}/{total} ({completed/total*100:.1f}%) | '
                          f'Rate: {rate:.1f} ch/sec | ETA: {eta/60:.1f} min')
        
        end_time = time.time()
        total_time = end_time - start_time
        
        print('\\n' + '=' * 70)
        print(f' FIXED Extraction Complete!')
        print(f' Successfully extracted: {self.success_count} chapters (COMPLETE CONTENT)')
        print(f' Failed extractions: {self.error_count} chapters')
        print(f'  Total time: {total_time/60:.2f} minutes')
        print(f' Average speed: {(self.success_count)/total_time:.2f} chapters/second')
        print(f' Files saved in: {os.path.abspath(self.output_folder)}')
        print(f' This extraction includes ALL content from <sent> tags!')
        
        if self.error_count > 0:
            print(f'\\n  Note: {self.error_count} chapters failed to extract. You may want to retry those manually.')

def main():
    print(' Dragon Talisman FIXED Chapter Extractor')
    print(' Complete Content Extraction (Fixes Missing Content Issue)')
    print('=' * 70)
    
    try:
        start = int(input('Enter starting chapter number: '))
        end = int(input('Enter ending chapter number: '))
        
        if end < start:
            print(' End chapter must be greater than start chapter!')
            return
        
        workers = input('Enter number of parallel workers (default: 8, max recommended: 12): ')
        workers = int(workers) if workers else 8
        workers = min(workers, 12)
        
        print(f'\\n Starting FIXED extraction with {workers} workers...')
        print(' This will extract the COMPLETE chapter content!')
        time.sleep(2)
        
        extractor = FixedChapterExtractor(max_workers=workers)
        extractor.extract_chapters_parallel(start, end)
        
    except KeyboardInterrupt:
        print('\\n  Extraction interrupted by user')
    except ValueError:
        print(' Invalid input. Please enter valid numbers.')
    except Exception as e:
        print(f' Error: {e}')

if __name__ == '__main__':
    main()
