import re
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import csv
from langdetect import detect, DetectorFactory
from langdetect.lang_detect_exception import LangDetectException
import os
# Ensure consistent language detection
DetectorFactory.seed = 0

yt_client = build(
    "youtube", "v3", developerKey=""
)

# Regular expression to detect emojis and Hindi script
emoji_pattern = re.compile("[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF"
                           "\U0001F680-\U0001F6FF\U0001F1E0-\U0001F1FF"
                           "\U00002700-\U000027BF]+", flags=re.UNICODE)
hindi_script_pattern = re.compile("[\u0900-\u097F]+")

# Hinglish dictionary
hinglish_dict = {
                        'a' : [
                            "aaya", "apna", "arre", "arey", "aisa", "aik", "aaiye", "aaye", "aaiyiye", 
                            "aaja", "abhi", "aap", "aapse", "aapko", "aapke", "aata", "ajeeb", "ajib", 
                            "aankhon", "aankhein", "aankh", "aaj", "ajj", "aasmaan", "asman", "aasman", 
                            "aur", "aawashyakta", "awashyakta", "adhik", "aaraam", "aram", "aaram", 
                            "araam", "accha", "acha", "achha", "acchi", "achhi", "achi", "achanak", 
                            "aasaan", "asaan", "asan", "aasan", "aapki", "ab", "adbhut"
                            ],
                        'b': [
                            "bahut", "beta", "bina", "bhai", "bolo", "bolna", "bohot", "baatein", 
                            "bharosa", "buniyaad", "buniyad", "behtar", "behtareen", "bewkoof", 
                            "bewkoofi", "bewakoof", "bewakoofi", "bewajah", "baaton", "baato", 
                            "bhi", "barbaad", "barbad", "baarish", "baarishein", "barish", 
                            "barishein", "barishon", "bhaag", "bhaago", "bhaagna", "badi", "bhim", "bheem", 
                            "badal", "baadal", "badlaav", "badlav", "badla", "behta", "bemisaal", "besharam"
                            "beshumar", "beshumaar"
                            ],
                        'c': [
                            "chal", "chalo", "chand", "chaand", "chandni", "chandi", "chori", 
                            "chhod", "chod", "chodo", "chhodo", "chalte", "chalti", "chalta", "chalna",
                            "chupa", "chhupa"
                            ],
                        'd': [
                            "dekha", "din", "dhoop", "dost", "dil", "dino", "dopahar", "dopaher", 
                            "dhyaan", "dhyan", "dilli", "dafa", "dekhi", "dikhi", "dikhayi", "dikhai", 
                            "dekho", "dekhna", "dastan", "daastan", "daastaan", "darmiyaan", "darr", 
                            "dastak", "diya", "doobe", "doobna", "doob", "dhoop", "dosti", "dikkat", "der"
                            ],
                        'e': ['ek'],
                        'f': ['farz', 'fikr', 'fikar', 'faltu', 'farsh'],
                        'g': [
                            "gaya", "gayi", "gadha", "gaadi", "ghadi", "ghum", "gehra", "gehraiyaan", 
                            "ghaata", "ghoomne", "ghumna", "ghumo", "ghoomo", "ghar", "gumnaam", 
                            "gawar", "gawaar", "gulab", "gulaabi", "gulabi", "gulaab", "gunguna", 
                            "gungunati", "garmi", "galti", "gumnaam"
                        ],
                        'h': [
                            "haan", "han", "hai", "hum", "humein", "hume", "humko", "hoti", "hota", 
                            "hona", "humesha", "humaara", "humara", "humaari", "humari", "humse", 
                            "humne", "haar", "husn", "hua", "hun", "hoon", "h", "hain", "haari", 
                            "hi", "hasna", "has", "hans", "hansi", "hasi", "har", "hari"
                        ],
                        'i': ["ishq", "idhar", "izzat", "ijjat", "ijazat", "ijaazat"],
                        'j': [
                            "jisse", "jawab", "jaise", "jidhar", "jeet", "janwar", "jaanwar", 
                            "janvar", "jaanvar", "jaan", "janam", "jaisa", "judayi", "judaayi", 
                            "judai", "judaai", "jaadu", "jagah", "jaane", "jaana", "jo", "jal", 
                            "jalana", "jalaana", "jab", "jawan", "jawaan", "jaon", "jao", "jaun", 
                            "jispe", "jispar", "jaisi", "jagah", "jodi", "jaake", "jai", "jay"
                            "jaag", "jaga", "jaldi", "jalti", "jag", "jaahir", "jaahil", "janaab", "janab", 
                            "jinke", "jahan", "jahaan"
                        ],
                        'k': [
                            "kabhi", "kaise", "kidhar", "khud", "khayal", "khayalon", "khwab", "khwaab", 
                            "kya", "kyun", "kyu", "kab", "kaash", "kash", "kagaz", "kabhie", "kis", 
                            "kahani", "kahaani", "kissa", "kisse", "khushi", "kinaare", "kinare", 
                            "khaali", "khali", "kahin", "kahi", "kahan", "kaha", "kaho", "khushbu", 
                            "khushboo", "khatam", "kinare", "kinaare", "kasam", "keh", "kehna", 
                            "khidki", "kapde", "kapdon", "ki", "kam", "kaam", "koi", "koyi", "kuch", 
                            "kuchh", "karo", "kar", "karna", "kr", "ka", "khuda"
                        ],
                        'l': [
                            "lagta", "liye", "laaye", "laana", "lelo", "lafzon", "laut", "lega", 
                            "legi", "lena", "lao", "log"
                        ],
                        'm': [
                            "magar", "mai", "main", "matlab", "mujhe", "mujhse", "mohabbat", "mohabat", 
                            "mein", "maze", "mazze", "maje", "mauj", "masti", "mahaul", "maahaul", 
                            "mera", "mere", "merre", "maine", "mene", "meine", "meri", "milan", 
                            "mehek", "mehak", "madhur", "maafi", "maaf", "maan", "mana", "meherbaan", 
                            "meherbaani", "meherbani", "maalum", "malum", "mushkil", "musafir", 
                            "mahila", "mitron", "masoom", "masum", "mausam", "mahadev", "mar", "maar",
                            "marke", "maarke", "maarna", "marna", "museebat", "musibat"
                        ],
                        'n': ["nahi", "nahana", "nahaana", "namak", "na", "naseeb", "nazar", "nazariya", "naam", 
                              "namah", "nazrein"
                              ],
                        'p': [
                            "pati", "patni", "pata", "pawan", "paisa", "paise", "pyar", "pyaar", 
                            "prayas", "puraani", "purani", "pukaare", "pukaar", "pukar", "pukare", 
                            "pakore", "phool", "pehle", "pehli", "pehla", "phir", "prem", "par", 
                            "pe", "parvat", "paani"
                        ],
                        'o': ["om"],
                        'r': [
                            "raat", "raha", "raah", "rehna", "rehne", "rahogi", "rahoge", "ruko", 
                            "rukna", "raasta", "rasta", "rabba", "rehti", "roko", "rona", "ro", 
                            "rakh", "rakhi", "rakhna", "ram"
                        ],
                        's': [
                            "sab", "sabhi", "sapna", "samajh", "shayad", "shakal", "shaam", "sham", 
                            "savera", "shuddh", "sawali", "silsila", "sawal", "sawaal", "suno", 
                            "suna", "soona", "safar", "subah", "subha", "saathi", "sathi", "saath", 
                            "shukr", "shukriya", "shukrana", "shukraana", "shukar", "shakkar", 
                            "saari", "surile", "sureele", "swapna", "sagar", "sajna", "shuru", 
                            "samne", "saamne", "soch", "socha", "sochna", "sakhi", "shayar", 
                            "shaayar", "shayari", "shaayari", "sardi", "se", "sahi", "shree", "shri", "shivaay", 
                            "shivay", "sampurana", "sampurna", "shyam", "shyaam", "socho", "suhana", "suhaana", 
                            "sawaalon", "sabr"
                        ],
                        't': [
                            "thoda", "thodi", "tujhe", "tum", "tumhein", "tumhe", "tumko", "tarah", 
                            "tere", "tera", "terre", "tanhayi", "tanhaayi", "tanhayee", "toofan", 
                            "toofani", "tumhari", "tumhaari", "tumse", "tumhare", "tumhaari", 
                            "teri", "tayyar", "tayyaar", "tayyari", "tayyaari", "tamasha", 
                            "tamaasha", "todo", "todna", "tabhi", "tadap", "tha", "thi", 
                            "tasveer", "tujh", "tujhpe", "tujhko", "tabah"
                        ],
                        'v': ["vaayu", "varna", "vaise", "vo"],
                        'w': ["waqt", "waise", "waisa", "waisi", "warna", "wahi", "wohi", "wo", "wahan", "waha", "wah"],
                        'y': ["yr", "yar", "yaar", "yaraana", "yarana", "yaad", "yaadein", "yaadon", 
                              "yaari", "yaariyan", "yaado", "yeh", "yahi", "yahin", "ya", "yun"
                              ],
                        'z': ["zindagi", "zeher", "zara", "zarra", "zanjeer", "zehnaseeb", "zarurat", "zaroorat", 
                              "zariya", "zyada", "zyaada", "zid", "zidd"
                              ],
                    }


# Define file paths
hindi_file_path = "hindi.csv"
english_file_path = "english.csv"
hinglish_file_path = "hinglish.csv"

# Function to open file in append mode and write header if needed
def open_csv_with_header(file_path, header):
    new_file = not os.path.exists(file_path)  # Check if file exists
    file = open(file_path, "a", newline="", encoding="utf-8")
    writer = csv.writer(file)
    
    if new_file:  # If it's a new file, write the header
        writer.writerow(header)
    
    return file, writer

# Open CSV files in append mode
hindi_file, hindi_writer = open_csv_with_header(hindi_file_path, ["comments", "emoji"])
english_file, english_writer = open_csv_with_header(english_file_path, ["comments", "emoji"])
hinglish_file, hinglish_writer = open_csv_with_header(hinglish_file_path, ["comments", "emoji"])

# Counters for statistics
total_comments = 0
english_count = 0
hindi_count = 0
hinglish_count = 0

# Function to get comments from YouTube API
def get_comments(client, video_id, token=None):
    """Fetch comments from YouTube API."""
    try:
        response = (
            client.commentThreads()
            .list(
                part="snippet",
                videoId=video_id,
                textFormat="plainText",
                maxResults=100,
                pageToken=token,
            )
            .execute()
        )
        return response
    except HttpError as e:
        print(f"HTTP Error {e.resp.status} for video ID: {video_id}")
        return None
    except Exception as e:
        print(f"Error: {e}")
        return None

def extract_emojis_and_clean(text):
    """Extract emojis and return cleaned text and emojis."""
    emojis = ''.join(emoji_pattern.findall(text))
    cleaned_text = emoji_pattern.sub('', text).strip()
    return cleaned_text, emojis

def detect_language(text):
    """Detect language of the comment."""
    try:
        lang = detect(text)
        return 'hindi' if lang == 'hi' else 'english'
    except LangDetectException:
        return 'unknown'

def is_hinglish(text):
    """Check if the text is Hinglish by looking for common Hinglish words."""
    words = text.lower().split()
    for word in words:
        first_char = word[0]
        if first_char in hinglish_dict and word in hinglish_dict[first_char]:
            return True
    return False

def is_pure_english(text):
    """Check if the text is pure English by ensuring it contains no Hindi script or common Hindi words."""
    if hindi_script_pattern.search(text):
        return False
    words = text.lower().split()
    return not any(word in hinglish_dict.get(word[0], []) for word in words)

# Read video IDs from id.csv
video_ids = []
with open("id.csv", "r", encoding="utf-8") as id_file:
    reader = csv.reader(id_file)
    for row in reader:
        video_ids.append(row[0])  # Assuming each row has one video ID

print(f"Total video IDs to scrape: {len(video_ids)}")

# Scrape comments for each video ID
for vid_id in video_ids:
    print(f"Scraping comments for video ID: {vid_id}")
    next_token = None

    while True:
        resp = get_comments(yt_client, vid_id, next_token)

        if not resp:
            break

        total_comments += len(resp["items"])
        next_token = resp.get("nextPageToken")
        if not next_token:
            break

        for i in resp["items"]:
            comment_text = i["snippet"]["topLevelComment"]["snippet"]["textDisplay"]

            # Extract emojis and clean comment
            cleaned_comment, emojis = extract_emojis_and_clean(comment_text)

            # Check if the cleaned comment contains any emoji
            if emojis:
                lang = detect_language(cleaned_comment)

                if lang == 'hindi':
                    hindi_writer.writerow([cleaned_comment, emojis])
                    hindi_count += 1
                elif is_hinglish(cleaned_comment):
                    hinglish_writer.writerow([cleaned_comment, emojis])
                    hinglish_count += 1
                elif lang == 'english' and is_pure_english(cleaned_comment):
                    english_writer.writerow([cleaned_comment, emojis])
                    english_count += 1

# Print final counts
print(f"Total comments processed: {total_comments}")
print(f"Hindi comments: {hindi_count}")
print(f"Hinglish comments: {hinglish_count}")
print(f"English comments: {english_count}")

# Close the CSV files
hindi_file.close()
english_file.close()
hinglish_file.close()