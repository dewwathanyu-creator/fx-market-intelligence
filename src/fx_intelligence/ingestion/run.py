"""Run one bounded provider fetch into the local raw layer."""

import argparse
import os
from pathlib import Path

import httpx
from dotenv import load_dotenv

from fx_intelligence.registry import load_registry

from .bot import BotClient
from .fred import FredClient
from .storage import store_raw


def main() -> None:
    parser = argparse.ArgumentParser(description="Fetch one official-source data window")
    parser.add_argument("source_id")
    parser.add_argument("--start", required=True, help="YYYY-MM-DD")
    parser.add_argument("--end", required=True, help="YYYY-MM-DD")
    args = parser.parse_args()
    root = Path.cwd()
    load_dotenv(root / ".env")
    registry = load_registry(root / "config" / "sources" / "registry.yaml")
    source = next((item for item in registry if item["id"] == args.source_id), None)
    if source is None:
        parser.error(f"unknown source_id: {args.source_id}")
    if args.start > args.end:
        parser.error("start must not follow end")
    with httpx.Client() as http:
        if source["provider"] == "FRED":
            rows = FredClient(os.getenv("FRED_API_KEY", ""), http=http).fetch(
                source["series_id"], args.start, args.end
            )
            payload = {"observations": rows}
        elif source["provider"] == "BOT":
            params = {"start_period": args.start, "end_period": args.end}
            if ":" in source["series_id"]:
                params["currency"] = source["series_id"].split(":", 1)[1]
            payload = BotClient(os.getenv("BOT_API_KEY", ""), http=http).fetch(
                source["url"], params
            )
        else:
            parser.error(f"unsupported provider: {source['provider']}")
    output = store_raw(root / "data" / "raw", source["id"], f"{args.start}_{args.end}", payload)
    print(output)


if __name__ == "__main__":
    main()
