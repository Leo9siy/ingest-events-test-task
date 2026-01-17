# LEARNED: Token Bucket Rate Limiting

## New tool/topic
**Token Bucket rate limiting** (in-memory) and integration testing FastAPI using **httpx + ASGITransport**.

## What I learned
- Token bucket is a simple algorithm to limit request rate:
  - a bucket has a maximum capacity
  - tokens refill over time at a fixed rate
  - each request consumes a token; if there are no tokens left, we return HTTP 429
- In-memory rate limiting is easy to implement but has limitations:
  - works per-process (multiple replicas need shared state like Redis)
  - best suited for a take-home MVP and basic protection

## Why configured this way
- Token bucket provides basic stability requirements without adding external dependencies.
- httpx + ASGITransport provides deterministic integration tests with minimal infrastructure.

## Next improvements
- Replace in-memory limiter with Redis-based limiter for multi-instance deployments.
- Add metrics for rate-limited responses and per-endpoint latency histograms.
