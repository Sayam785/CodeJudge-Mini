"""Oracle connection factory used by the database layer.

python-oracledb uses thin mode by default, so no Oracle Client installation
is needed.  The defaults match the local Oracle 21c XE XEPDB1 setup and can
be overridden with environment variables for another development machine.
"""

import os

import oracledb


def get_connection():
    """Open one short-lived application connection in python-oracledb thin mode."""
    return oracledb.connect(
        user=os.getenv("ORACLE_USER", "SAYAM_PBL"),
        password=os.getenv("ORACLE_PASSWORD", "123"),
        dsn=os.getenv("ORACLE_DSN", "localhost:1521/XEPDB1"),
    )
