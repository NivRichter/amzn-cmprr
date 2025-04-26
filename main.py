from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from amazon_price_comparison import AmazonPriceComparer
from pydantic import BaseModel
import os

app = FastAPI()

# Enable CORS for all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static directory
app.mount("/static", StaticFiles(directory="static"), name="static")


# Serve index.html at root
@app.get("/")
def read_index():
    return FileResponse(os.path.join("templates", "index.html"))


comparer = AmazonPriceComparer()


class SearchRequest(BaseModel):
    type: str
    query: str


@app.post("/api/search")
async def search(request: SearchRequest):
    if not request.query:
        return {"error": "Query is required"}
    try:
        if request.type == "product_id":
            results = await comparer.search_by_product_id(request.query)
        else:
            results = await comparer.search_product(request.query)
        return results
    except Exception as e:
        return {"error": str(e)}
