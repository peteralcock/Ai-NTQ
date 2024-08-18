import craigslistscraper as cs
import json

# Define the search. Everything is done lazily, and so the html is not 
# fetched at this step.
search = cs.Search(
    query = "bmw e46",
    city = "minneapolis",
    category = "cto"
)

# Fetch the html from the server. Don't forget to check the status. 
status = search.fetch()
if status != 200:
    raise Exception(f"Unable to fetch search with status <{status}>.")

print(f"{len(search.ads)} ads found!")
for ad in search.ads:
    # Fetch additional information about each ad. Check the status again.
    status = ad.fetch()
    if status != 200:
        print(f"Unable to fetch ad '{ad.title}' with status <{status}>.")
        continue

    # There is a to_dict() method for convenience. 
    data = ad.to_dict()

    # json.dumps is merely for pretty printing. 
    print(json.dumps(data, indent = 4))


