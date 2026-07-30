import re
import requests

DOWNLOAD_PAGE = "https://www.microsoft.com/en-us/download/confirmation.aspx?id=56519"
LINES_PER_CHUNK = 3000  # ~45KB por archivo, seguro bajo el límite de 63KB


def get_json_download_url():
    resp = requests.get(
        DOWNLOAD_PAGE, timeout=30,
        headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"},
    )
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

    prefixes = None
    for value in data["values"]:
        if value["name"] == "AzureCloud":
            prefixes = sorted(p for p in value["properties"]["addressPrefixes"] if ":" not in p)
            break

    if not prefixes:
        raise Exception("No se encontró el tag AzureCloud en el JSON")

    chunks = [prefixes[i:i + LINES_PER_CHUNK] for i in range(0, len(prefixes), LINES_PER_CHUNK)]

    for idx, chunk in enumerate(chunks, start=1):
        filename = f"azure-cloud-ips-part{idx}.txt"
        with open(filename, "w") as f:
            f.write("\n".join(chunk) + "\n")
        print(f"Escrito {len(chunk)} rangos en {filename}")

    with open("azure-cloud-ips-manifest.txt", "w") as f:
        f.write(str(len(chunks)))
    print(f"Total de partes: {len(chunks)}")


if __name__ == "__main__":
    main()
