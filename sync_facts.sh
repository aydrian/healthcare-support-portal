#!/bin/bash

# Healthcare Support Portal - OSO Facts Synchronization
# Convenience script to sync authorization facts with OSO Cloud

echo "🔐 Healthcare Support Portal - OSO Fact Synchronization"
echo "======================================================"

# Run the fact synchronization script
uv run python -m packages.common.src.common.sync_oso_facts