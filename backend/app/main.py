from fastapi import FastAPI


app = FastAPI()

@app.get("/")


async def health_check():
    return {"message": "Hello from Zolitron2"}

