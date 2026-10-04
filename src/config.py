import os
from typing import Optional

from dotenv import load_dotenv

load_dotenv()


def get_secret(name: str) -> Optional[str]:
    """Read a setting from the environment or Streamlit Cloud secrets."""
    value = os.getenv(name)
    if value:
        return value

    try:
        import streamlit as st

        value = st.secrets.get(name)
    except (FileNotFoundError, KeyError, ImportError):
        value = None

    return str(value) if value else None
