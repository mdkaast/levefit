from fastapi import FastAPI

app = FastAPI(title="PFO API")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
