"""
aggregator.py — Merges outputs from all agents into the final output row.

Takes results from context_builder, image_analyst, claim_verifier, and
risk_scorer and produces a dict matching the 14-column output schema.
"""
