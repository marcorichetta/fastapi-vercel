# FastAPI on Vercel Example

This is a [FastAPI](https://fastapi.tiangolo.com/) example app deployed on [Vercel](https://vercel.com/).

### Requirements

-   Vercel account
-   Vercel CLI

### Setup

1. `git clone && cd fastapi-vercel`
1. _(Recommended)_ Create a virtual environment and activate it

```bash
python -m venv env

source env/bin/activate
```

1. Install dependencies

```bash
pip install -r requirements.txt
```

1. Run it!

```bash
uvicorn main:app --reload
```

1. Deploy to Vercel

```bash
vercel
# or
git push # on main
```
