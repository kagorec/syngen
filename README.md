# SynGen — A Tool for Finding and Analyzing n-grams in Text Files

## Description
SynGen is a professional text analysis tool that recursively processes files in specified directories, extracts and counts the occurrence statistics of phrases (n-grams). Thanks to its use of multiprocessing and advanced filtering system, the script is ideal for processing large volumes of text data and will be useful for linguists, content analysts, SEO specialists, and researchers in the field of NLP.

## Practical Applications
- **SEO Competitor Analysis** — identifying popular key phrases
- **Linguistic Research** — analyzing the frequency of word combinations
- **Content Preparation** — determining the most relevant phrases for inclusion in texts
- **Text Corpus Processing** — preparing data for machine learning
- **Copywriter Workflow Automation** — identifying frequently used phrases and clichés

## Installation and Setup

### Requirements
- Python 3.6 or higher
- Standard Python libraries (no additional package installation required)

### Launch Procedure
1. Download and save as `syngen.py` or clone the repository:
```bash
git clone https://github.com/yourusername/syngen.git
cd syngen
```

2. If necessary, configure (use notepad or other) the parameters at the top of the script:
   - `NGRAM_SIZE` — size of n-grams (default: 2 words)
   - `MINSYMBOLS` — minimum phrase length in characters
   - `RESULT` — path for saving results
   - `SOURCE_DIRS` — directories to search for text files
   - `BLACKLIST` — words to exclude from analysis

3. Run the script:
```bash
python syngen.py
```

# More About SynGen

## Technical Features

### 🔥 Performance and Optimization
- **Multiprocessing Architecture** — the script uses available processor resources most efficiently:
  ```python
  # Dynamic determination of the optimal number of processes
  max_workers = min(multiprocessing.cpu_count(), 8)
  with ProcessPoolExecutor(max_workers=max_workers) as executor:
      # Parallel file processing
  ```
- **Two-level Parallelization** — simultaneous processing of both directories and files within them:
  ```python
  # First level — parallel directory processing
  with ProcessPoolExecutor(max_workers=len(config['source_dirs'])) as executor:
      future_to_dir = {
          executor.submit(process_directory, directory, config['blacklist']): directory
          for directory in config['source_dirs']
      }
  ```
- **Thread-safe Logging** — using mutexes for safe logging from different processes:
  ```python
  log_lock = multiprocessing.Lock()
  # ...
  def safe_log(level, message):
      """Thread-safe logging function."""
      with log_lock:
          # Logging with protection through locking
  ```

### 📊 Intelligent Text Processing
- **Multi-level Filtering System** — comprehensive checking of each phrase:
  ```python
  # Phrases go through multiple filters
  if (is_blacklisted(phrase, blacklist) or 
      has_digits(phrase) or 
      has_single_letters(phrase) or 
      is_too_short(phrase)):
      continue
  ```
- **Smart File Decoding** — automatic detection of text file encoding:
  ```python
  def read_file_with_fallback_encodings(file_path):
      """Try to read file with different encodings."""
      encodings = ['utf-8', 'cp1251', 'latin-1', 'iso-8859-1']
      
      for encoding in encodings:
          try:
              with open(file_path, 'r', encoding=encoding) as f:
                  return f.read()
          except UnicodeDecodeError:
              continue
  ```
- **Extended Blacklist** — a preset list of words to exclude, including:
  - Brand names (more than 100 popular brands from different areas)
  - Function words (prepositions, conjunctions, pronouns, etc.)
  - Auxiliary verbs and frequently used words

### 🛡️ Reliability and Stability
- **Error Handling at All Levels** — the system continues to work even when individual components fail:
  ```python
  try:
      # Operations with files and text
  except (IOError, UnicodeError) as e:
      safe_log('error', f"Error processing file {file_path}: {str(e)}")
      return Counter()
  ```
- **Automatic Creation of Result Directories**:
  ```python
  # Create directory if it doesn't exist
  os.makedirs(os.path.dirname(output_path), exist_ok=True)
  ```
- **Protection Against Parasitic Processes on Windows**:
  ```python
  if __name__ == "__main__":
      # Preventing the creation of multiple processes on Windows
      multiprocessing.freeze_support()
  ```

## Results Format
Results are saved in a CSV file with columns:
- `phrase` — extracted phrase
- `words_count` — number of words in the phrase
- `total_count` — total number of occurrences of this phrase in the processed texts

Phrases are sorted by frequency in descending order, which immediately highlights the most important n-grams.
