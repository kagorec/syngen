"""
Script to recursively search text files in specified directories,
extract and count n-grams (phrases of N words), and save results to CSV.
Uses multiprocessing for improved performance.
UPDATED: 2025-05-02
By KaGorec
"""

import os
import re
import csv
import logging
import multiprocessing
from collections import Counter
from functools import partial
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor, as_completed


# Configuration
# Number of words in each phrase (2 for bigrams, 3 for trigrams, etc.)
NGRAM_SIZE = 2

# Minimum number of symbols in a phrase
MINSYMBOLS = 4

RESULT = r"D:\content\result.csv"
SOURCE_DIRS = [
    r"C:\content\syn\folder-with-txt-articles",
    r"C:\content\sample2\clear-articles-without-html-tags", 
    r"C:\any\folder\conyent-txt", "", "", ""  # Additional empty paths
]
BLACKLIST = [
# Games platforms and Services
"Amazon Prime Gaming", "Battle.net", "Bethesda.net", "Big Fish Games", "Blox Fruits", "Direct2Drive", "Dotemu", "EA Play", "Epic Games", "GamersGate", "GeForce Now", "GOG", "GOG.com", "Google Stadia", "Green Man Gaming", "Humble Bundle", "itch.io", "Kongregate", "Metaboli", "Microsoft Store", "Newgrounds", "Nvidia GeForce Now", "Origin", "RAWG.io", "Riot Games", "Rockstar Games", "Steam", "Ubisoft Connect", "Xbox Game Pass",

# ...

# PC Hardware Manufacturers and Components
"ADATA", "Altera", "AMD", "AOC", "Arm Ltd.", "ASRock", "AsRock", "ASUS", "Asus", "Audio-Technica", "be quiet!", "Belkin International, Inc.", "BenQ", "BIOS", "Celeron", "Cooler Master", "Core", "Corsair", "CPU", "Crucial", "eDRAM", "EPYC", "EVGA", "Fellowes, Inc.", "Foxconn", "Fractal Design", "G.Skill", "G Skill", "GeForce", "Gigabyte", "GPU", "GTX", "HDD", "HP", "HyperX", "Intel", "Kingston", "LG", "Lian Li", "Logitech", "Machina Labs", "Microchip", "Motherboard", "MSI", "Noctua", "NVMe", "Nvidia", "NZXT", "PC", "Pentium", "PSU", "Radeon", "RAM", "Razer", "Razor Inc.", "Roccat", "RTX", "RX", "Ryzen", "Samsung", "SanDisk", "Seagate", "Seasonic", "Sennheiser", "SK Hynix Inc.", "SRAM", "SSD", "SteelSeries", "Thermaltake", "Threadripper", "UEFI", "WD", "Western Digital",

# Automotive Brands
"Acura", "Audi", "Beetle", "BMW", "BYD", "Cadillac", "Chevrolet", "Chevy", "Chrysler", "Chrysler Minivans", "Citroën", "Dodge", "Farizon", "Ferrari", "Fiat", "Ford", "Geely", "GMC", "Honda", "Hyundai", "Hyundai Mobis", "Hyundai Rotem", "Infiniti", "Jaguar", "Jeep", "Kia", "Lamborghini", "Land Rover", "Lexus", "London Electric Vehicle Company", "Mazda", "Mercedes", "Mercedes-Benz", "Mini", "Mitsubishi", "Nissan", "Peugeot", "Porsche", "Ram", "Renault", "Rolls-Royce", "Subaru", "Suzuki", "Tesla", "Toyota", "Volkswagen", "Volvo", "VW", "Zhejiang Geely Holding Group",

# Motorcycle Brands
"Benelli", "BMW", "BMW Motorrad", "Ducati", "Harley Davidson", "Harley-Davidson", "Honda", "Husqvarna", "Indian Motorcycle", "Indian Motorcycles", "Kawasaki", "KTM", "Piaggio", "Qianjiang Motorcycle", "Royal Enfield", "Suzuki", "Triumph", "Vespa", "Yamaha",

# Electronics and Appliance Brands
"Acer", "Amana", "Amazon", "Apple", "Bissell", "Bosch", "Cafe", "Canon", "Dyson", "Electrolux", "Frigidaire", "GE", "GE Appliances", "Google", "Haier", "IKEA", "Kitchen Aid", "KitchenAid", "Lenovo", "LG Energy Solution, Ltd.", "Maytag", "Microsoft", "Midea Group", "Miele", "Nikon", "Panasonic", "Philips", "Piaggio Fast Forward", "Samsung Electronics", "Sharp", "Siemens", "Smeg", "Sony", "Sub-Zero", "Toshiba", "Whirlpool",


    # Articles
    "a", "an", "the", "ll", 

    # Prepositions
    "as", "by", "for", "in", "of", "off", "on", "out", "per", "plus", "so", "than", 
    "to", "unto", "up", "upon", "via", "while", "yet",

    # Coordinating Conjunctions
    "and", "but", "for", "nor", "or", "so", "yet",

    # Subordinating Conjunctions
    "as", "if", "than", "that", "though", "unless", "until", "when", "where", "while",

    # Auxiliary Verbs
    "am", "are", "be", "been", "being", "can", "could", "dare",
    "did", "do", "does", "had", "has", "have", "having", "may",
    "might", "must", "need", "ought", "shall", "should", "used", "will",
    "would",

    # Personal Pronouns
    "I", "i", "he", "her", "him", "it", "me", "she",
    "them", "they", "us", "we", "you",

    # Possessive Pronouns
    "her", "hers", "his", "its", "mine", "my", "our", "ours",
    "their", "theirs", "your", "yours",

    # Reflexive Pronouns
    "herself", "himself", "itself", "myself", "ourselves", "themselves",
    "yourself", "yourselves",

    # Demonstrative Pronouns
    "that", "these", "this", "those",

    # Interrogative & Relative Pronouns
    "what", "whatever", "which", "whichever", "who", "whoever", "whom",
    "whomever", "whose",

    # Indefinite Pronouns
    "any", "anybody", "anyone", "anything", "each",
    "either", "everybody", "everyone", "everything", "much", "neither", 
    "no one", "nobody", "none", "noone", "nothing",
    "one", "other", "others", "several", "some", "somebody", "someone",
    "something",

    # Miscellaneous
    "here", "indeed", "just", "merely", "nearly", "never", "now", "often",
    "only", "really", "scarcely", "seldom",
    "simply", "sometimes", "somewhat", "still", "then", "there", "too",
    "usually", "very"
]


# Setup logging with a lock for multiprocessing
log_lock = multiprocessing.Lock()
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(processName)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('search_words.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def load_config():
    """Load configuration from variables defined at the top of the script."""
    with log_lock:
        config = {
            'source_dirs': [path for path in SOURCE_DIRS if path.strip()],
            'blacklist': [word.lower() for word in BLACKLIST],
            'result_path': RESULT
        }
        logger.info(f"Loaded configuration: {len(config['source_dirs'])} directories, "
                    f"{len(config['blacklist'])} blacklisted words")
    return config


def safe_log(level, message):
    """Thread-safe logging function."""
    with log_lock:
        if level == 'info':
            logger.info(message)
        elif level == 'warning':
            logger.warning(message)
        elif level == 'error':
            logger.error(message)
        else:
            logger.debug(message)


def is_blacklisted(text, blacklist):
    """Check if any word from blacklist is in the text."""
    text_lower = text.lower()
    return any(blackword in text_lower for blackword in blacklist)


def clean_text(text):
    """Clean text by converting to lowercase and removing punctuation."""
    # Convert to lowercase
    text = text.lower()
    # Replace punctuation with spaces
    text = re.sub(r'[^\w\s]', ' ', text)
    # Replace multiple spaces with a single space
    text = re.sub(r'\s+', ' ', text)
    return text.strip()


def has_digits(text):
    """Check if text contains any digits."""
    return any(char.isdigit() for char in text)


def has_single_letters(text):
    """Check if text contains any single letters separated by spaces."""
    # Match single letters that are surrounded by spaces or at the beginning/end of the string
    return bool(re.search(r'(^| )[a-zA-Z]( |$)', text))


def is_too_short(text):
    """Check if text has fewer than MINSYMBOLS characters."""
    return len(text) < MINSYMBOLS


def read_file_with_fallback_encodings(file_path):
    """Try to read file with different encodings."""
    encodings = ['utf-8', 'cp1251', 'latin-1', 'iso-8859-1']
    
    for encoding in encodings:
        try:
            with open(file_path, 'r', encoding=encoding) as f:
                return f.read()
        except UnicodeDecodeError:
            continue
    
    # If all encodings fail, raise an exception
    raise UnicodeError(f"Failed to decode file {file_path} with any encoding")


def count_ngrams(text, blacklist):
    """
    Extract and count n-grams (phrases of N words) from text.
    Filters out phrases containing blacklisted words, digits, single letters,
    or phrases shorter than MINSYMBOLS characters.
    """
    cleaned_text = clean_text(text)
    words = cleaned_text.split()
    
    if len(words) < NGRAM_SIZE:
        return Counter()
    
    ngrams = []
    
    # Simple n-gram extraction
    for i in range(len(words) - NGRAM_SIZE + 1):
        phrase = " ".join(words[i:i+NGRAM_SIZE])
        
        # Skip phrases that:
        # 1. Contain blacklisted words
        # 2. Contain digits
        # 3. Contain single letters
        # 4. Are shorter than MINSYMBOLS characters
        if (is_blacklisted(phrase, blacklist) or 
            has_digits(phrase) or 
            has_single_letters(phrase) or 
            is_too_short(phrase)):
            continue
            
        ngrams.append(phrase)
    
    return Counter(ngrams)


def process_file(file_path, blacklist):
    """Process a single text file and extract n-grams."""
    try:
        safe_log('info', f"Processing file: {file_path}")
        text = read_file_with_fallback_encodings(file_path)
        return count_ngrams(text, blacklist)
    except (IOError, UnicodeError) as e:
        safe_log('error', f"Error processing file {file_path}: {str(e)}")
        return Counter()


def find_txt_files(directory):
    """Recursively find all .txt files in the given directory."""
    txt_files = []
    try:
        for root, _, files in os.walk(directory):
            for file in files:
                if file.lower().endswith('.txt'):
                    txt_files.append(os.path.join(root, file))
    except Exception as e:
        safe_log('error', f"Error finding txt files in {directory}: {str(e)}")
    
    return txt_files


def save_results(ngram_counter, output_path):
    """Save n-gram counts to CSV file."""
    try:
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Sort n-grams by count (descending)
        sorted_ngrams = ngram_counter.most_common()
        
        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            # Write header
            writer.writerow(['phrase', 'words_count', 'total_count'])
            
            # Write data
            for phrase, count in sorted_ngrams:
                words_count = len(phrase.split())
                writer.writerow([phrase, words_count, count])
        
        safe_log('info', f"Results saved to {output_path}, {len(sorted_ngrams)} phrases found")
    except Exception as e:
        safe_log('error', f"Error saving results to {output_path}: {str(e)}")


def process_directory(directory, blacklist):
    """Process all text files in a directory."""
    if not os.path.isdir(directory):
        safe_log('warning', f"Directory does not exist: {directory}")
        return Counter()
    
    safe_log('info', f"Searching in directory: {directory}")
    txt_files = find_txt_files(directory)
    safe_log('info', f"Found {len(txt_files)} text files in {directory}")
    
    directory_ngrams = Counter()
    
    # Create a partial function for multiprocessing
    process_func = partial(process_file, blacklist=blacklist)
    
    # Use ProcessPoolExecutor for parallel processing
    max_workers = min(multiprocessing.cpu_count(), 8)  # Limit to 8 processes
    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        future_to_file = {executor.submit(process_func, file_path): file_path 
                          for file_path in txt_files}
        
        for future in as_completed(future_to_file):
            file_path = future_to_file[future]
            try:
                ngrams = future.result()
                directory_ngrams.update(ngrams)
            except Exception as e:
                safe_log('error', f"Error processing {file_path}: {str(e)}")
    
    return directory_ngrams


def main():
    """Main function to orchestrate the process."""
    safe_log('info', "Starting search words")
    
    # Load configuration
    config = load_config()
    
    # Initialize counter for all n-grams
    all_ngrams = Counter()
    
    # Process each source directory with multiprocessing
    with ProcessPoolExecutor(max_workers=len(config['source_dirs'])) as executor:
        future_to_dir = {
            executor.submit(process_directory, directory, config['blacklist']): directory
            for directory in config['source_dirs']
        }
        
        for future in as_completed(future_to_dir):
            directory = future_to_dir[future]
            try:
                directory_ngrams = future.result()
                all_ngrams.update(directory_ngrams)
                safe_log('info', f"Completed processing directory: {directory}")
            except Exception as e:
                safe_log('error', f"Error processing directory {directory}: {str(e)}")
    
    # Save results
    save_results(all_ngrams, config['result_path'])
    safe_log('info', "Processing completed")


if __name__ == "__main__":
    # This guards against spawning multiple processes on Windows
    multiprocessing.freeze_support()
    try:
        main()
    except Exception as e:
        safe_log('error', f"Unhandled exception: {str(e)}")
		
		
