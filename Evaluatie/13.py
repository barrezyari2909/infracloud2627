import json
import requests

URL = "https://api.country.is"


def main():
    try:
        response = requests.get(URL, timeout=30)
        response.raise_for_status()
    except requests.exceptions.Timeout:
        print("Fout: de server antwoordde niet op tijd.")
        return
    except requests.exceptions.ConnectionError:
        print("Fout: geen verbinding.")
        return
    except requests.exceptions.HTTPError as e:
        print(f"HTTP-fout: {e}")
        return

    data = response.json()

    print("=" * 50)
    print("HTTP-informatie")
    print("=" * 50)
    print(f"URL:          {response.url}")
    print(f"Statuscode:   {response.status_code}")
    print(f"Content-Type: {response.headers.get('Content-Type')}")

    print("\n" + "=" * 50)
    print("Ruwe JSON-respons")
    print("=" * 50)
    print(json.dumps(data, indent=4))

    print("\n" + "=" * 50)
    print("Verwerkte informatie")
    print("=" * 50)
    print(f"Publiek IP-adres: {data['ip']}")
    print(f"Landcode:         {data['country']}")


if __name__ == "__main__":
    main()