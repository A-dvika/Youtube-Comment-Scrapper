from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import csv
import sys
import re
from langdetect import detect, DetectorFactory
from langdetect.lang_detect_exception import LangDetectException

# Ensure consistent language detection
DetectorFactory.seed = 0

if len(sys.argv) != 3:
    print("Add a video ID and output file name after the script name")
    sys.exit(1)

vid_id = sys.argv[1]
output_file = sys.argv[2]
yt_client = build(
    "youtube", "v3", developerKey="AeIzaSyCt21TFlMPQ1MSjB0tfB0Z_3AT6KkbGKRk"
)

# Regular expression to detect emojis
emoji_pattern = re.compile("[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF"
                           "\U0001F680-\U0001F6FF\U0001F1E0-\U0001F1FF"
                           "\U00002700-\U000027BF]+", flags=re.UNICODE)


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
        print(e.resp.status)
        return None
    except Exception as e:
        print(e)
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


comments = []
next = None
english_count = 0
hindi_count = 0

# Open CSV files for writing
with open("hindi.csv", "w", newline="", encoding="utf-8") as hindi_file, \
     open("english.csv", "w", newline="", encoding="utf-8") as english_file:

    hindi_writer = csv.writer(hindi_file)
    english_writer = csv.writer(english_file)

    # Write header row in both files
    hindi_writer.writerow(["comments", "emoji"])
    english_writer.writerow(["comments", "emoji"])

    while True:
        resp = get_comments(yt_client, vid_id, next)

        if not resp:
            break

        comments += resp["items"]
        next = resp.get("nextPageToken")
        if not next:
            break

        for i in resp["items"]:
            comment_text = i["snippet"]["topLevelComment"]["snippet"]["textDisplay"]

            # Extract emojis and clean comment
            cleaned_comment, emojis = extract_emojis_and_clean(comment_text)

            # Check if the cleaned comment contains any emoji
            if emojis:
                lang = detect_language(cleaned_comment)

                if lang == 'english':
                    english_writer.writerow([cleaned_comment, emojis])
                    english_count += 1
                elif lang == 'hindi':
                    hindi_writer.writerow([cleaned_comment, emojis])
                    hindi_count += 1

print(f"Total comments fetched: {len(comments)}")
print(f"Total English comments with emojis: {english_count}")
print(f"Total Hindi comments with emojis: {hindi_count}")
