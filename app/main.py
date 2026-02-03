from fastapi import FastAPI

app = FastAPI(title="Dynamic Version-Controlled RAG")

@app.get("/")
def health():
    return {"status": "ok"}
