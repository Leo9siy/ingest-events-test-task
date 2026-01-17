We use PostgreSQL with a UNIQUE constraint on event_id 
and INSERT … ON CONFLICT DO NOTHING to guarantee idempotent ingestion 
at the database level. This approach avoids race conditions, 
reduces database round-trips, and ensures correctness under concurrent ingestion.



