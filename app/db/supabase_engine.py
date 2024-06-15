from dotenv import load_dotenv

load_dotenv()

import os

from supabase import create_client
from supabase.client import ClientOptions


class SupabaseSingleton:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = SupabaseSingleton._init_supabase()
        return cls._instance

    @classmethod
    def _init_supabase(cls):
        # Initialize Supabase here
        url = os.environ["SUPABASE_URL"]
        key = os.environ["SUPABASE_KEY"]

        supabase = create_client(
            url, key,
            options=ClientOptions(
                postgrest_client_timeout=10,
                storage_client_timeout=10,
                schema="public",
            ))

        return supabase
