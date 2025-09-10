#!/usr/bin/env python3
"""
Batch script to automatically find and extract all missing chapters.
This script scans for missing chapters and extracts them automatically.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from single_chapter_missing_extract import MissingChapterExtractor

def main():
    print("🐉 Dragon Talisman - Find & Extract Missing Chapters")
    print("=" * 60)
    
    # Get range from command line or use defaults
    if len(sys.argv) >= 3:
        try:
            start_range = int(sys.argv[1])
            end_range = int(sys.argv[2])
            print(f"📊 Using command line range: {start_range}-{end_range}")
        except ValueError:
            print("❌ Invalid arguments. Usage: python find_and_extract_missing.py [start] [end]")
            return
    else:
        # Ask user for range
        try:
            start_range = int(input("Enter start chapter number (default: 1): ") or "1")
            end_range = int(input("Enter end chapter number (default: 1200): ") or "1200")
        except ValueError:
            print("❌ Invalid input. Using defaults: 1-1200")
            start_range, end_range = 1, 1200
    
    print(f"🔍 Scanning for missing chapters in range {start_range}-{end_range}...")
    
    # Initialize extractor
    extractor = MissingChapterExtractor()
    
    # Find missing chapters
    missing_chapters = extractor.find_missing_chapters(start_range, end_range)
    
    if not missing_chapters:
        print("✅ Great! No missing chapters found in the specified range.")
        return
    
    print(f"\n📋 Found {len(missing_chapters)} missing chapters:")
    
    # Group consecutive chapters for better display
    groups = []
    if missing_chapters:
        current_group = [missing_chapters[0]]
        
        for i in range(1, len(missing_chapters)):
            if missing_chapters[i] == missing_chapters[i-1] + 1:
                current_group.append(missing_chapters[i])
            else:
                groups.append(current_group)
                current_group = [missing_chapters[i]]
        groups.append(current_group)
        
        # Display missing chapters in groups
        for group in groups:
            if len(group) == 1:
                print(f"   📄 Chapter {group[0]}")
            else:
                print(f"   📄 Chapters {group[0]}-{group[-1]} ({len(group)} chapters)")
    
    # Confirm extraction
    if len(sys.argv) >= 3:
        # Auto-proceed if command line arguments provided
        proceed = True
    else:
        confirm = input(f"\n🚀 Extract all {len(missing_chapters)} missing chapters? (y/n): ").lower()
        proceed = confirm == 'y'
    
    if not proceed:
        print("❌ Extraction cancelled.")
        return
    
    print(f"\n🚀 Starting extraction of {len(missing_chapters)} missing chapters...")
    print("⏱️  This may take a few minutes depending on the number of chapters.")
    
    # Extract missing chapters
    results = extractor.extract_missing_chapters(missing_chapters)
    
    # Summary
    successful = sum(1 for r in results.values() if r['success'])
    failed = len(results) - successful
    
    print("\n" + "=" * 60)
    print("📊 EXTRACTION SUMMARY")
    print("=" * 60)
    print(f"✅ Successfully extracted: {successful} chapters")
    print(f"❌ Failed extractions: {failed} chapters")
    print(f"📁 Files saved in: {os.path.abspath(extractor.output_folder)}")
    
    if failed > 0:
        print(f"\n❌ Failed chapters (you can retry these with the single extractor):")
        for chapter_num, result in results.items():
            if not result['success']:
                print(f"   Chapter {chapter_num}: {result['message']}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n🛑 Extraction interrupted by user")
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1) 