import csv
import json
from datetime import datetime
from pathlib import Path
from typing import Any

import requests
import typer
from dateutil import parser
from rich.progress import track
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.connection import get_context_session
from src.database.models import EventModel


app = typer.Typer(help="Usage: import_events [OPTIONS] CSV_PATH")


def parse_dt(value: str) -> datetime:
    return parser.parse(value)


def parse_properties(value: str) -> dict[str, Any]:
    if value is None or value.strip() == "" or value.strip().lower() == "null":
        return {}
    try:
        return json.loads(value)
    except json.JSONDecodeError:
        # якщо в CSV кривуватий JSON — краще явно падати
        raise ValueError(f"Invalid properties_json: {value[:200]}")


async def bulk_insert_events(session: AsyncSession, rows: list[dict[str, Any]]) -> int:
    """
    Packet insert with ON CONFLICT DO NOTHING (Postgres).
    Return rowcount (apx: rowcount).
    """
    if not rows:
        return 0

    stmt = insert(EventModel).values(rows)

    stmt = stmt.on_conflict_do_nothing(index_elements=[EventModel.event_id])

    result = await session.execute(stmt)
    await session.commit()

    return result.rowcount or 0


@app.command("import_events")
def import_events(
    csv_path: Path = typer.Argument(..., exists=True, file_okay=True, dir_okay=False),
    batch_size: int = typer.Option(2000, help="Packets size to DataBase"),
):
    """
    CSV colums:
      event_id, occurred_at, user_id, event_type, properties_json
    """
    typer.echo(f"Reading CSV: {csv_path}")

    required = {"event_id", "occurred_at", "user_id", "event_type", "properties_json"}

    import asyncio

    async def run():
        inserted_total = 0
        processed_total = 0

        with csv_path.open("r", encoding="utf-8", newline="") as f:
            reader = csv.DictReader(f)
            if not reader.fieldnames:
                raise typer.BadParameter("CSV has no header row.")

            missing = required - set(reader.fieldnames)
            if missing:
                raise typer.BadParameter(f"Missing columns: {', '.join(sorted(missing))}")

            batch: list[dict[str, Any]] = []

            async with get_context_session() as session:
                for row in track(reader, description="Importing..."):
                    processed_total += 1

                    payload = {
                        "event_id": row["event_id"],
                        "occurred_at": parse_dt(row["occurred_at"]),
                        "user_id": row["user_id"],
                        "event_type": row["event_type"],
                        "properties": parse_properties(row["properties_json"]),
                    }
                    batch.append(payload)

                    if len(batch) >= batch_size:
                        inserted = await bulk_insert_events(session, batch)
                        inserted_total += inserted
                        batch.clear()

                if batch:
                    inserted = await bulk_insert_events(session, batch)
                    inserted_total += inserted

        typer.echo(f"Processed: {processed_total}")
        typer.echo(f"Inserted (approx): {inserted_total}")
        typer.echo("Done ✅")

    asyncio.run(run())


def main():
    app()
