"""
Pulls the most reccently played song from LASTFM'S SCROBBLER, and logs it to stats.json.
Json can then be used to created a sheilds.io badge.
The Following environment variables must be set for this script to work:
LASTFM_USERNAME, LASTFM_API_KEY, LASTFM_LIMIT, TRAKT_USERNAME, and TRAKT_API_KEY.
By default for this script, LASTFM_LIMIT is 1.
Created by github.com/vault108
"""

import json
import os
import sys
import requests


def lastfm_stats():
    """Fetches the most recently played song from Last.fm
    Then attempts to update stats.json if there's a new song."""
    username = os.getenv("LASTFM_USERNAME")
    api_key = os.getenv("LASTFM_API_KEY")
    limit = os.getenv("LASTFM_LIMIT")
    scrobbler_url = f"http://ws.audioscrobbler.com/2.0/?method=user.getrecenttracks&user={username}&api_key={api_key}&limit={str(limit)}&format=json"
    response = requests.get(scrobbler_url, timeout=10)
    if response.status_code != 200:
        print("Error: Unable to fetch data from Last.fm API")
        print(f"Status Code: {response.status_code} URL: {scrobbler_url}")
        sys.exit(1)
    if username is None or api_key is None:
        print("Error: LASTFM_USERNAME or LASTFM_API_KEY environment variable not set.")
        sys.exit(1)
    if limit is None:
        limit = "1"
    data = response.json()
    track = data["recenttracks"]["track"]
    artist = track[0]["artist"]["#text"]
    song = track[0]["name"]
    together = f"{artist} - {song}"
    try:
        try:
            with open("assets/stats.json", "r", encoding="utf-8") as file:
                existing_data = json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            existing_data = {}

        output = {"song": together}

        if existing_data.get("song") == output["song"]:
            print("No New Song Detected.")
        else:
            existing_data.update(output)
            with open("assets/stats.json", "w", encoding="utf-8") as f:
                json.dump(existing_data, f, indent=2)
            print("New Song Detected. Updated stats.json")
    except (IOError, KeyError, requests.exceptions.JSONDecodeError) as e:
        print(f"An error occurred in generate_stats_json: {e}")
        sys.exit(1)


def traktv_stats():
    """Fetches stats from Trakt.tv and updates stats.json if there are new stats."""
    trakt_api_key = os.getenv("TRAKT_API_KEY")
    trakt_username = os.getenv("TRAKT_USERNAME")
    traktv_url = f"https://api.trakt.tv/users/{trakt_username}/stats"
    headers = {
        "Content-Type": "application/json",
        "trakt-api-version": "2",
        "trakt-api-key": trakt_api_key,
    }
    response = requests.get(traktv_url, headers=headers, timeout=10)
    if trakt_api_key is None or trakt_username is None:
        print(
            "Error: TRAKT_API_KEY or TRAKT_USERNAME environment variable not set. Now Exiting."
        )
        sys.exit(1)
    if response.status_code != 200:
        print("Error: Unable to fetch data from Trakt.tv API")
        print(f"Status Code: {response.status_code} URL: {traktv_url}")
        sys.exit(1)
    try:
        data = response.json()
        movie_days = round(data["movies"]["minutes"] / 60 / 24)
        movies_watched = data["movies"]["watched"]
        show_days = round(data["episodes"]["minutes"] / 60 / 24)
        shows_watched = data["shows"]["watched"]
        episodes_watched = data["episodes"]["watched"]

        try:
            with open("assets/stats.json", "r", encoding="utf-8") as file:
                existing_data = json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            existing_data = {}

        output = {
            "movie_days": movie_days,
            "movies_watched": movies_watched,
            "show_days": show_days,
            "shows_watched": shows_watched,
            "episodes_watched": episodes_watched,
        }

        # Check if stats have changed
        if all(existing_data.get(key) == value for key, value in output.items()):
            print("No New Stats Detected.")
        else:
            existing_data.update(output)
            with open("assets/stats.json", "w", encoding="utf-8") as file:
                json.dump(existing_data, file, indent=2)
            print("New Stats Detected. Updated stats.json")

    except (IOError, KeyError, requests.exceptions.JSONDecodeError) as e:
        print(f"An error occurred in traktv_stats: {e}")
        sys.exit(1)


if __name__ == "__main__":
    lastfm_stats()
    traktv_stats()
