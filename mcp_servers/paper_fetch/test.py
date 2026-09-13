from server import fetch_paper

result = fetch_paper("2509.14559", title="test")
print(result["title"])
print(len(result["text"]))
print(result["text"][:300])