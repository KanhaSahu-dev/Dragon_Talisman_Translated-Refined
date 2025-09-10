# Missing Chapter Extractor for Dragon Talisman

This folder contains **2 simple scripts** to extract missing chapters that failed during the initial bulk extraction process.

## Problem Solved

During the initial extraction process, some chapters were missed due to:
- Network timeouts
- Different HTML structures on certain pages
- Server-side rendering issues
- Content loading delays

## 📝 Scripts Available (Only 2!)

### 1. `single_chapter_missing_extract.py` - Single Chapter Extractor
**For extracting one specific missing chapter at a time.**

Features:
- Simple single chapter extraction
- Multiple extraction methods for different HTML structures
- Enhanced content parsing for `<sent>` tags
- Automatic ad and script removal
- Detailed progress reporting

**Usage:**
```bash
python single_chapter_missing_extract.py
# Then enter the chapter number when prompted (e.g., 13)
```

### 2. `bulk_chapter_missing_extract.py` - Bulk Missing Chapter Extractor
**Automatically finds and extracts ALL missing chapters.**

Features:
- Automatically scans for missing chapters
- Batch extraction of all missing chapters
- Command-line support for automation
- Grouped display of missing chapters
- Progress tracking

**Usage:**
```bash
# Interactive mode (asks for range)
python bulk_chapter_missing_extract.py

# Command line mode (automatic)
python bulk_chapter_missing_extract.py 1 1200
python bulk_chapter_missing_extract.py 1 100
```

## Technical Details

### Content Extraction Method

The scripts use a multi-layered approach to extract content:

1. **Primary Method**: Extract from `<div id="showReading">` with `<sent>` tags
2. **Secondary Method**: Extract from `<div class="readBox">` with `<sent>` tags  
3. **Fallback Method**: Extract from `<div id="readcontent">`
4. **Last Resort**: Extract from `<div class="textbox">`

### Content Processing

- **Paragraph Formation**: Intelligently groups `<sent>` elements into paragraphs
- **Dialogue Detection**: Starts new paragraphs for dialogue
- **Ad Removal**: Removes Google AdSense and other advertising content
- **Script Cleaning**: Removes JavaScript and other non-content elements
- **Formatting**: Proper spacing and line breaks

### Quality Assurance

- Minimum content length validation (100+ characters)
- Content source tracking for debugging
- Character count reporting
- Error logging and reporting

## 📋 Quick Start Guide

**Need to extract a specific missing chapter?**
```bash
python single_chapter_missing_extract.py
# Enter: 13 (for Chapter 13)
```

**Want to find and extract ALL missing chapters automatically?**
```bash
python bulk_chapter_missing_extract.py
# Enter: 1 (start range)
# Enter: 1200 (end range)
```

## Example Output

**Single Chapter Extraction:**
```
🔍 Extracting Chapter 13 from: https://novelhi.com/s/Dragon-Talisman/13
📖 Title: Chapter 13
✅ Successfully extracted Chapter 13
📊 Content length: 16549 characters
🔧 Extraction method: showReading div with <sent> tags
💾 Saved to: Extracted_Chapters_Fixed/Chapter_013.txt
```

**Batch Missing Chapter Finder:**
```
🔍 Scanning for missing chapters in range 1-100...
📋 Found 3 missing chapters:
   📄 Chapter 13
   📄 Chapters 45-47 (3 chapters)
🚀 Extract all 4 missing chapters? (y/n): y
✅ Successfully extracted: 4 chapters
```

## File Structure

```
Extracted_Chapters_Fixed/
├── Chapter_001.txt
├── Chapter_002.txt
├── ...
├── Chapter_013.txt  ← Newly extracted
├── ...
└── Chapter_XXX.txt
```

## Success Rate

The enhanced extraction method has a very high success rate because:
- Multiple fallback methods
- Better HTML parsing
- Improved content detection
- Robust error handling

## Troubleshooting

### If extraction fails:
1. Check your internet connection
2. Verify the chapter number exists on the website
3. Try running the script again (temporary server issues)
4. Check the error message for specific issues

### If content seems incomplete:
1. The script validates minimum content length
2. Check the extraction method used (shown in output)
3. Compare with the website manually if needed

## Dependencies

- `requests`: HTTP requests
- `beautifulsoup4`: HTML parsing
- `urllib3`: HTTP utilities
- `re`: Regular expressions
- `os`, `time`, `sys`: Standard library

Install with:
```bash
pip install requests beautifulsoup4 urllib3
```

## 🎯 Summary

**Just 2 scripts to remember:**

1. **`single_chapter_missing_extract.py`** - Extract ONE specific missing chapter
2. **`bulk_chapter_missing_extract.py`** - Find and extract ALL missing chapters

**Plus 1 optimized bulk extractor:**
- **`fixed_extractor.py`** - High-performance parallel extraction (most advanced)

That's it! Simple and effective.

## Notes

- The scripts are respectful to the server with built-in delays
- Content is saved in UTF-8 encoding
- All scripts output to the `Extracted_Chapters_Fixed` folder
- Progress is shown in real-time for batch operations
- Chapter 13 has already been successfully extracted! 