"""HTTP client for PokéAPI including endpoints, retry policy, and concurrency limit."""

import asyncio
import logging
from collections.abc import AsyncIterator

import httpx

from app.config import settings

logger = logging.getLogger(__name__)

# Only 18 base types are in scope
TYPE_COUNT = 18

CONCURRENCY = 10
ATTEMPTS = 3


def id_from_url(url: str) -> int:
    """PokéAPI identifies related resources by URL, so ids arrive as the last segment."""
    return int(url.rstrip("/").rsplit("/", 1)[-1])


class PokeAPIClient(httpx.AsyncClient):
    def __init__(self, **kwargs) -> None:
        super().__init__(
            base_url=settings.pokeapi_base_url,
            # httpx defaults to 5s, which drops dozens of the 1351 under concurrency.
            timeout=httpx.Timeout(30.0, connect=10.0),
            headers={"User-Agent": "pokemon-team-builder"},
            **kwargs,
        )

    async def get_json(self, path: str) -> dict:
        for attempt in range(1, ATTEMPTS + 1):
            try:
                response = await self.get(path)
                response.raise_for_status()
                return response.json()
            except httpx.HTTPStatusError as exc:
                # Only 5xx is worth a retry; a 404 answers the question.
                if exc.response.status_code < 500 or attempt == ATTEMPTS:
                    raise
            except httpx.TransportError:  # TimeoutException is a subclass
                if attempt == ATTEMPTS:
                    raise
            await asyncio.sleep(0.5 * 2 ** (attempt - 1))
        raise AssertionError("unreachable")

    async def get_all_pokemon_ids(self) -> list[int]:
        listing = await self.get_json("/pokemon?limit=5000")
        return [id_from_url(r["url"]) for r in listing["results"]]

    async def get_type_damage_relations(self) -> dict[str, dict]:
        """{type name: its damage_relations}, for the 18 chart types."""
        listing = await self.get_json(f"/type?limit={TYPE_COUNT}")
        names = [r["name"] for r in listing["results"]]
        details = await asyncio.gather(
            *(self.get_json(f"/type/{name}") for name in names)
        )
        return {
            name: detail["damage_relations"]
            for name, detail in zip(names, details, strict=True)
        }

    async def iter_pokemon(
        self, pokemon_ids: list[int]
    ) -> AsyncIterator[tuple[int, dict | None]]:
        """(id, payload) as each request finishes, `CONCURRENCY` at a time.

        Yields so the caller can drop each payload once it has processed it.
        """
        semaphore = asyncio.Semaphore(CONCURRENCY)

        async def fetch(pokemon_id: int) -> tuple[int, dict | None]:
            async with semaphore:
                try:
                    return pokemon_id, await self.get_json(f"/pokemon/{pokemon_id}/")
                except httpx.HTTPError as exc:
                    # None means "fetch failed", not "deleted upstream": the caller
                    # leaves the existing row alone.
                    logger.warning("pokemon %d failed: %r", pokemon_id, exc)
                    return pokemon_id, None

        tasks = [fetch(pokemon_id) for pokemon_id in pokemon_ids]
        for done, completed in enumerate(asyncio.as_completed(tasks), start=1):
            if done % 200 == 0:
                logger.info("fetched %d/%d", done, len(pokemon_ids))
            yield await completed
