import argparse
import base64
import sys
import json
from http.client import HTTPException
from urllib import request as urllib_request

NOIP_BASE_URL = "https://dynupdate.no-ip.com/nic/update"
PUBLICIP_BASE_URL = "https://api.ipify.org/?format=json"


class NoIpError(Exception):
    ...


def _get_public_ip() -> str:
    with urllib_request.urlopen(PUBLICIP_BASE_URL) as r:
        body = r.read()

    body_json = json.loads(body)
    return body_json["ip"]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("username")
    parser.add_argument("password")
    parser.add_argument("hostname")
    parser.add_argument("--verbose", action="store_true", default=False)

    args = parser.parse_args()

    output = sys.stdout.write
    verbose = args.verbose

    output(f"{'NO-IP-PUBLIC-IP-UPDATE':=^76}\n")
    if verbose:
        output("Getting public ip address...\n")

    public_ip = _get_public_ip()

    url = f"{NOIP_BASE_URL}?hostname={args.hostname}&myip={public_ip}"

    if verbose:
        output(f"Public ip address: {public_ip}\n")
        output(f"Building request...\n")
        output(f"URL: {url!r}\n")

    request = urllib_request.Request(url)
    auth_b64 = base64.b64encode(f"{args.username}:{args.password}".encode("ascii"))
    request.add_header("Authorization", f"Basic {auth_b64.decode('ascii')}")

    if verbose:
        output("Request built\n")
        output("Sending request to no-ip...\n")

    with urllib_request.urlopen(request) as r:
        body = r.read().decode("utf-8")

    if verbose:
        output(f"Response body: {body!r}\n")

    if body.startswith("good"):
        output("Request successful. IP updated!\n")
    elif body.startswith("nochg"):
        output("Request successful. No change.\n")
    else:
        raise HTTPException(f"Unknown error.\n\tStatus: {r.status}\n\tBody: {body!r}")

    output(("=" * 76) + "\n")


if __name__ == "__main__":
    raise SystemExit(main())
