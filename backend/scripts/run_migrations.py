#!/usr/bin/env python3
"""
Database migration runner for Constellation Hub.

Usage:
    python run_migrations.py                  # Upgrade to latest
    python run_migrations.py upgrade head     # Upgrade to latest
    python run_migrations.py downgrade -1     # Downgrade one step
    python run_migrations.py history          # Show migration history
    python run_migrations.py current          # Show current revision
"""
import os
import sys
import argparse

# Ensure backend directory is in path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from alembic.config import Config
from alembic import command


def get_alembic_config():
    """Get Alembic configuration."""
    config_path = os.path.join(os.path.dirname(__file__), 'alembic.ini')
    return Config(config_path)


def upgrade(revision='head'):
    """Upgrade database to specified revision."""
    config = get_alembic_config()
    command.upgrade(config, revision)
    print(f"✅ Database upgraded to {revision}")


def downgrade(revision='-1'):
    """Downgrade database by specified steps."""
    config = get_alembic_config()
    command.downgrade(config, revision)
    print(f"✅ Database downgraded by {revision}")


def history():
    """Show migration history."""
    config = get_alembic_config()
    command.history(config)


def current():
    """Show current database revision."""
    config = get_alembic_config()
    command.current(config)


def heads():
    """Show available migration heads."""
    config = get_alembic_config()
    command.heads(config)


def revision(message=None, autogenerate=False):
    """Create a new migration revision."""
    config = get_alembic_config()
    command.revision(
        config,
        message=message,
        autogenerate=autogenerate
    )


def main():
    parser = argparse.ArgumentParser(description='Constellation Hub Database Migrations')
    subparsers = parser.add_subparsers(dest='command', help='Migration command')

    # Upgrade command
    upgrade_parser = subparsers.add_parser('upgrade', help='Upgrade database')
    upgrade_parser.add_argument('revision', nargs='?', default='head', help='Target revision')

    # Downgrade command
    downgrade_parser = subparsers.add_parser('downgrade', help='Downgrade database')
    downgrade_parser.add_argument('revision', nargs='?', default='-1', help='Steps to downgrade')

    # History command
    subparsers.add_parser('history', help='Show migration history')

    # Current command
    subparsers.add_parser('current', help='Show current revision')

    # Heads command
    subparsers.add_parser('heads', help='Show available heads')

    # Revision command
    revision_parser = subparsers.add_parser('revision', help='Create new migration')
    revision_parser.add_argument('-m', '--message', required=True, help='Migration message')
    revision_parser.add_argument('--autogenerate', action='store_true', help='Auto-generate from models')

    args = parser.parse_args()

    if args.command == 'upgrade':
        upgrade(args.revision)
    elif args.command == 'downgrade':
        downgrade(args.revision)
    elif args.command == 'history':
        history()
    elif args.command == 'current':
        current()
    elif args.command == 'heads':
        heads()
    elif args.command == 'revision':
        revision(args.message, args.autogenerate)
    else:
        # Default: upgrade to head
        print("Running database migrations...")
        upgrade('head')


if __name__ == '__main__':
    main()
