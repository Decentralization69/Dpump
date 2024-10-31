import re

def parse_command(text, image_url):
    pattern = r"@(\w+)\s/([lL][aA][uU][nN][cC][hH])\s\"([^\"]+)\"\s\"([^\"]+)\"\s\"([^\"]+)\""
    match = re.match(pattern, text)

    if not match:
        raise ValueError("Unable to parse text. Please check the format.")

    username, command, token_name, ticker, description = match.groups()

    return {
        "username": username,
        "command": command,
        "token_name": token_name,
        "ticker": ticker,
        "description": description,
        "image_url": image_url,
    }
