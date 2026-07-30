import re
import requests

DOWNLOAD_PAGE = "https://www.microsoft.com/en-us/download/details.aspx?id=56519"
OUTPUT_FILE = "azure-cloud-ips.txt"


def get_json_download_url():
    resp = requests.get(DOWNLOAD_PAGE, timeout=30, headers={"User-Agent": "Mozilla/5.0"})
    match = re.search(
        r'https://download\.microsoft\.com/download/[^"]+ServiceTags_Public_[^"]+\.json',
        resp.text,
    )
    if not match:
        raise Exception("No se encontró el link del JSON en la página de descarga")
    return match.group(0)


def main():
    url = get_json_download_url()
    print(f"Descargando: {url}")
    data = requests.get(url, timeout=60).json()

    for value in data["values"]:
        if value["name"] == "AzureCloud":
            prefixes = sorted(p for p in value["properties"]["addressPrefixes"] if ":" not in p)
            with open(OUTPUT_FILE, "w") as f:
                f.write("\n".join(prefixes) + "\n")
            print(f"Escrito {len(prefixes)} rangos en {OUTPUT_FILE}")
            return

    raise Exception("No se encontró el tag AzureCloud en el JSON")


if __name__ == "__main__":
    main()
