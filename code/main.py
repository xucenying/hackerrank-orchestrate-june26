"""
main.py — Entry point for the damage claim verification system.

Reads dataset/claims.csv, processes each claim concurrently via
asyncio.gather, and writes results to output.csv.
"""
