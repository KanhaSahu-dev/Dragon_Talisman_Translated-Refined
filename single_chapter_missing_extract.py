import requests
import urllib3
from bs4 import BeautifulSoup
import os
import time
import re
from typing import List, Tuple, Optional

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class MissingChapterExtractor:
    def __init__(self, base_url='https://novelhi.com/s/Dragon-Talisman', output_folder='Extracted_Chapters_Fixed'):
        self.base_url = base_url
        self.output_folder = output_folder
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
        
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)
    
    def extract_content_from_sent_tags(self, content_div) -> str:
        """Extract content from <sent> tags and format properly"""
        sent_elements = content_div.find_all('sent')
        
        if not sent_elements:
            return ""
        
        content_parts = []
        current_paragraph = []
        
        for sent in sent_elements:
            sent_text = sent.get_text().strip()
            if not sent_text:
                continue
            
            # Check if this should start a new paragraph
            should_start_new_paragraph = (
                # Dialogue often starts new paragraphs
                (sent_text.startswith('"') and current_paragraph and 
                 not current_paragraph[-1].endswith('"')) or
                # Long descriptive sentences
                (len(sent_text) > 120 and current_paragraph) or
                # Sentences that end with periods and next starts with capital
                (current_paragraph and current_paragraph[-1].endswith('.') and
                 sent_text[0].isupper() and len(sent_text) > 80)
            )
            
            if should_start_new_paragraph:
                if current_paragraph:
                    content_parts.append(' '.join(current_paragraph))
                current_paragraph = [sent_text]
            else:
                current_paragraph.append(sent_text)
        
        # Add the last paragraph
        if current_paragraph:
            content_parts.append(' '.join(current_paragraph))
        
        return '\n\n'.join(content_parts)
    
    def clean_content(self, content: str) -> str:
        """Clean up extracted content"""
        # Remove script tags and ads
        content = re.sub(r'<script[^>]*>.*?</script>', '', content, flags=re.DOTALL | re.IGNORECASE)
        content = re.sub(r'<ins[^>]*>.*?</ins>', '', content, flags=re.DOTALL | re.IGNORECASE)
        
        # Remove ad-related content
        unwanted_patterns = [
            r'adsbygoogle.*?push\(\{\}\);',
            r'pagead2\.googlesyndication\.com.*',
            r'data-ad-[^=]*="[^"]*"',
            r'crossorigin="anonymous"',
            r'async=""',
            r'Report.*?bad translation',
            r'Select text and click.*Report.*',
            r'Words:\d+.*?Update:\d+/\d+/\d+.*?\d+:\d+:\d+',
        ]
        
        for pattern in unwanted_patterns:
            content = re.sub(pattern, '', content, flags=re.DOTALL | re.IGNORECASE)
        
        # Clean up extra whitespace
        content = re.sub(r'\n\s*\n\s*\n+', '\n\n', content)
        content = re.sub(r'[ \t]+', ' ', content)
        content = content.strip()
        
        return content
    
    def extract_single_chapter(self, chapter_num: int) -> Tuple[bool, str]:
        """Extract a single chapter with enhanced content extraction"""
        url = f'{self.base_url}/{chapter_num}'
        print(f'🔍 Extracting Chapter {chapter_num} from: {url}')
        
        try:
            response = self.session.get(url, verify=False, timeout=20)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract title
            title = soup.find('h1')
            title_text = title.get_text().strip() if title else f'Chapter {chapter_num}'
            print(f'📖 Title: {title_text}')
            
            # Look for content in order of preference
            content = ""
            content_source = ""
            
            # Method 1: Look for showReading div with sent tags (most reliable)
            show_reading_div = soup.find('div', {'id': 'showReading'})
            if show_reading_div:
                content = self.extract_content_from_sent_tags(show_reading_div)
                content_source = "showReading div with <sent> tags"
            
            # Method 2: Look for readBox class
            if not content:
                read_box_div = soup.find('div', class_='readBox')
                if read_box_div:
                    content = self.extract_content_from_sent_tags(read_box_div)
                    content_source = "readBox div with <sent> tags"
            
            # Method 3: Look for readcontent div
            if not content:
                readcontent_div = soup.find('div', {'id': 'readcontent'})
                if readcontent_div:
                    # Try to find sent tags within
                    content = self.extract_content_from_sent_tags(readcontent_div)
                    if not content:
                        # Fallback to text extraction
                        content = readcontent_div.get_text()
                    content_source = "readcontent div"
            
            # Method 4: Look for textbox class (fallback)
            if not content:
                textbox_div = soup.find('div', class_='textbox')
                if textbox_div:
                    content = textbox_div.get_text()
                    content_source = "textbox div"
            
            if not content:
                return False, "No content found in any known container"
            
            # Clean the content
            content = self.clean_content(content)
            
            if len(content) < 100:
                return False, f"Content too short: {len(content)} characters"
            
            # Save the chapter
            filename = f'{self.output_folder}/Chapter_{chapter_num:03d}.txt'
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(f'{title_text}\n')
                f.write('=' * len(title_text) + '\n\n')
                f.write(content)
            
            print(f'✅ Successfully extracted Chapter {chapter_num}')
            print(f'📊 Content length: {len(content)} characters')
            print(f'🔧 Extraction method: {content_source}')
            print(f'💾 Saved to: {filename}')
            
            return True, f"Success: {len(content)} chars from {content_source}"
            
        except Exception as e:
            error_msg = f"Error extracting Chapter {chapter_num}: {str(e)}"
            print(f'❌ {error_msg}')
            return False, error_msg
    
    def extract_missing_chapters(self, chapter_list: List[int]) -> dict:
        """Extract multiple missing chapters"""
        print(f'🚀 Missing Chapter Extractor Started!')
        print(f'📋 Chapters to extract: {chapter_list}')
        print(f'📁 Output folder: {os.path.abspath(self.output_folder)}')
        print('=' * 60)
        
        results = {}
        successful = 0
        failed = 0
        
        for chapter_num in chapter_list:
            print(f'\n[{chapter_num}/{len(chapter_list)}] Processing Chapter {chapter_num}...')
            
            success, message = self.extract_single_chapter(chapter_num)
            results[chapter_num] = {'success': success, 'message': message}
            
            if success:
                successful += 1
            else:
                failed += 1
            
            # Small delay to be respectful to the server
            time.sleep(1)
        
        print('\n' + '=' * 60)
        print(f'🎉 Extraction Complete!')
        print(f'✅ Successfully extracted: {successful} chapters')
        print(f'❌ Failed extractions: {failed} chapters')
        
        if failed > 0:
            print('\n❌ Failed chapters:')
            for chapter_num, result in results.items():
                if not result['success']:
                    print(f'   Chapter {chapter_num}: {result["message"]}')
        
        return results
    
    def find_missing_chapters(self, start: int = 1, end: int = 100) -> List[int]:
        """Find missing chapters in the specified range"""
        missing = []
        for i in range(start, end + 1):
            filename = f'{self.output_folder}/Chapter_{i:03d}.txt'
            if not os.path.exists(filename):
                missing.append(i)
        return missing

def main():
    print('🐉 Dragon Talisman Single Chapter Extractor')
    print('=' * 50)
    
    try:
        extractor = MissingChapterExtractor()
        
        # Simple single chapter extraction
        chapter_input = input('Enter chapter number to extract: ').strip()
        
        try:
            chapter_num = int(chapter_input)
            print(f'\n🚀 Extracting Chapter {chapter_num}...')
            success, message = extractor.extract_single_chapter(chapter_num)
            
            if success:
                print(f'\n✅ Success! {message}')
            else:
                print(f'\n❌ Failed: {message}')
                
        except ValueError:
            print('❌ Invalid input. Please enter a valid chapter number.')
            
    except KeyboardInterrupt:
        print('\n🛑 Extraction interrupted by user')
    except Exception as e:
        print(f'❌ Error: {e}')

if __name__ == '__main__':
    main() 