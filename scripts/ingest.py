"""Create or refresh the local policy embedding index."""

import argparse

from src.config import Settings
from src.database import Database
from src.provider import GeminiProvider, ProviderUnavailable
from src.retrieval import Retriever


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()
    settings = Settings()
    provider = GeminiProvider(settings)
    try:
        retriever = Retriever(Database(settings.database_path), provider, settings)
        version = retriever.ensure_index(force=args.force)
        print(f"Indexed {retriever.status()['indexed_chunks']} chunks. Policy version: {version[:12]}")
    except ProviderUnavailable as exc:
        raise SystemExit(str(exc)) from None
    finally:
        provider.close()


if __name__ == "__main__":
    main()
