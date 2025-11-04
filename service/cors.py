from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


def init_cors(app: FastAPI, allowed_domains: list[str] = None):
    if allowed_domains is None:
        allowed_domains = []


    origins = [
        *allowed_domains
    ]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
