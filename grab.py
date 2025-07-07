import requests
import json
import datetime
import time
import sys
import math

ACCESS_TOKEN = '[put your API key here]'  # Replace with your GitHub token or set to None

usage = """Retrieves a list of follower usernames of a GitHub user using the GitHub API.

Usage: python grab.py [target_username] [output filename] [max_pages|optional]

Example:
    grab.py jfullstackdev followers.txt 5
"""

def main():
    if len(sys.argv) < 3:
        print(usage)
        sys.exit(-1)

    target_username = sys.argv[1]
    output_filename = sys.argv[2]
    max_pages = int(sys.argv[3]) if len(sys.argv) >= 4 else 10  # default max 10 pages
    per_page = 30  # GitHub default per page

    headers = {
        'Accept': 'application/vnd.github.v3+json'
    }
    if ACCESS_TOKEN and ACCESS_TOKEN != '[put your API key here]':
        headers['Authorization'] = f'token {ACCESS_TOKEN}'

    params = {
        'per_page': per_page,
        'page': 1
    }

    try:
        with open(output_filename, "a", encoding="utf-8") as output_file:
            while params['page'] <= max_pages:
                url = f'https://api.github.com/users/{target_username}/followers'
                r = requests.get(url, headers=headers, params=params)

                # Rate limit handling
                remaining_requests = int(r.headers.get('X-RateLimit-Remaining', 0))
                reset_time = datetime.datetime.fromtimestamp(int(r.headers.get('X-RateLimit-Reset', 0)))
                waiting_time = (reset_time - datetime.datetime.now()).total_seconds()
                print(f"Page {params['page']} - {remaining_requests} requests remaining, reset in {math.ceil(waiting_time / 60.0)} minutes...")

                if remaining_requests == 0:
                    print(f"Rate limit reached. Waiting {math.ceil(waiting_time)} seconds...")
                    time.sleep(waiting_time + 1)
                    continue

                if r.status_code != 200:
                    print(f"Error: Received status code {r.status_code}, retrying in 10 seconds...")
                    time.sleep(10)
                    continue

                followers = r.json()
                if not followers:
                    print("No more followers found, stopping.")
                    break

                # Write usernames to file
                for user in followers:
                    username = user.get('login')
                    if username:
                        output_file.write(username + "\n")

                print(f"Added {len(followers)} followers from page {params['page']}.")

                params['page'] += 1
                time.sleep(1)  # Be polite, avoid hitting rate limits too fast

    except KeyboardInterrupt:
        print("\nInterrupted by user, exiting.")
        sys.exit(0)
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
