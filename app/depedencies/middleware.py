from fastapi.middleware.cors import CORSMiddleware

origins = ["http://localhost:3000", "https://getelmo.vercel.app"]


def init(app):
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
