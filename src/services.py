from datetime import datetime, timedelta

from fastapi import Depends, HTTPException
from sqlalchemy import select, insert, Integer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.functions import func

from src.schemas import EventIn
from src.database.connection import get_session
from src.database.models import EventModel


async def get_event_service(session: AsyncSession = Depends(get_session)):
    return EventService(session)


class EventService:
    def __init__(self, session: AsyncSession):
        self.session = session


    @staticmethod
    async def parse_date(date):
        try:
            return datetime.strptime(date, '%Y-%m-%d')
        except ValueError:
            raise HTTPException(
                status_code=500,
                detail="Invalid date format. Use YYYY-MM-DD"
            )


    async def ingest(self, events: list[EventIn]):
        if not events:
            return {"inserted": 0}

        rows = [
            {
                "event_id": event.event_id,
                "occurred_at": event.occurred_at,
                "user_id": event.user_id,
                "event_type": event.event_type,
                "properties": event.properties,
            }
            for event in events
        ]

        stmt = (
            insert(EventModel)
            .values(rows)
            .on_conflict_do_nothing(
                index_elements=["event_id"]
            )
        )

        result = await self.session.execute(stmt)
        await self.session.commit()

        return {
            "received": len(events),
            "inserted": result.rowcount or 0,
        }


    async def get_uniq_users_by_date(self, from_date: str, to_date: str):
        from_dt = await self.parse_date(from_date)
        to_dt = await self.parse_date(to_date) + timedelta(days=1)

        day = func.date(EventModel.occurred_at) # only date

        stmt = (
            select(
                day.label("day"),
                func.count(func.distinct(EventModel.user_id)).label("dau"),
            )
            .where(EventModel.occurred_at >= from_dt, EventModel.occurred_at < to_dt)
            .group_by(day)
            .order_by(day)
        )

        res = await self.session.execute(stmt)
        data = [{"date": str(day), "dau": dau} for day, dau in res.all()]
        return {"from": from_date, "to": to_date, "dau": data}


    async def get_top_events(self, from_date: str, to_date: str, limit: int):
        from_date = await self.parse_date(from_date)
        to_date = await self.parse_date(to_date) + timedelta(days=1)

        res = await self.session.execute(
            select(
                EventModel.event_type,
                func.count().label("count")
            )
            .filter(EventModel.occurred_at >= from_date,
                    EventModel.occurred_at < to_date)
            .group_by(EventModel.event_type)
            .order_by(func.count().desc())
            .limit(limit)
        )

        top = [{"event_type": et, "count": c} for et, c in res.all()]
        return {"top_events": top}


    async def get_retention(self, start_date: str, windows: int):
        start_date = await self.parse_date(start_date)

        first_seen_cte = (
            select(
                EventModel.user_id.label("user_id"),
                func.min(EventModel.occurred_at).label("first_seen"),
            )
            .where(EventModel.occurred_at >= start_date)
            .group_by(EventModel.user_id)
            .cte("first_seen") # temporary table
        )

        # cohort_week: first week
        cohort_cte = (
            select(
                first_seen_cte.c.user_id,
                func.date_trunc("week", first_seen_cte.c.first_seen).label("cohort_week"), # округление до week
            ).cte("cohort")
        )

        # week_index: difference between occurred_at и cohort_week
        # just вычисление
        week_index_expr = (
                func.extract(  # to seconds
                    # epoch это представление времени в секундах с 1970 года (UNIX-время).
                    "epoch",
                    func.date_trunc("week", EventModel.occurred_at) - cohort_cte.c.cohort_week
                ) / (7 * 24 * 60 * 60)
        ).cast(Integer) # to int

        stmt = (
            select(
                cohort_cte.c.cohort_week.label("cohort_week"),
                week_index_expr.label("week_index"),
                func.count(func.distinct(EventModel.user_id)).label("users"),
            )
            .join(cohort_cte, cohort_cte.c.user_id == EventModel.user_id)
            .where(EventModel.occurred_at >= start_date)
            .where(week_index_expr.between(0, windows)) # windows is count
            .group_by("cohort_week", "week_index")
            .order_by("cohort_week", "week_index")
        )

        res = await self.session.execute(stmt)
        rows = res.all()  # (cohort_week, week_index, users)

        # cohort_size = users в week_index=0
        cohort_size = {cw: u for cw, wi, u in rows if wi == 0}

        retention = {}
        for cw, wi, users in rows:
            base = cohort_size.get(cw, 0)
            pct = round(users / base * 100, 2) if base else 0.0
            retention.setdefault(
                str(cw.date()), {}
            )[int(wi)] = {
                "users": users, "pct": pct
            }

        return {"start_date": start_date, "windows": windows, "retention": retention}

