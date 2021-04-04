from fastapi import FastAPI


app = FastAPI()


@app.get("/")
async def root():
    return {"pi": "3.1415926535897932384626433"}
