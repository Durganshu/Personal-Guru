#!/usr/bin/env python3
"""
Migration script to add book_generation_progress table.
"""

from app import create_app
from app.core.extensions import db
from app.core.models import BookGenerationProgress
import sys

def add_book_generation_progress_table():
    """Add the book_generation_progress table to the database."""
    app = create_app()

    with app.app_context():
        try:
            # Create the table
            print("Creating book_generation_progress table...")
            BookGenerationProgress.__table__.create(db.engine, checkfirst=True)
            print("✓ book_generation_progress table created successfully!")
            return True
        except Exception as e:
            print(f"✗ Error creating table: {e}")
            return False

if __name__ == "__main__":
    success = add_book_generation_progress_table()
    sys.exit(0 if success else 1)
