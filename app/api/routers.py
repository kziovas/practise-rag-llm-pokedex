from fastapi import APIRouter, Body, HTTPException, Query
from app.services.core_services import es_client
from app.services.core_services import embeddings_model
from app.services.llm import DefaultAssistant
from fastapi.templating import Jinja2Templates
from fastapi.responses import JSONResponse, HTMLResponse
from sse_starlette.sse import EventSourceResponse

templates = Jinja2Templates(directory="app/templates")
router = APIRouter()


@router.get("/healthcheck")
async def health_check():
    return {"status": "ok"}


@router.get("/", response_class=HTMLResponse)
async def index():
    with open("static/index.html", "r") as file:
        content = file.read()
    return HTMLResponse(content=content)


@router.post("/add_document/")
async def add_document(document: dict = Body(...)):
    try:
        # Combine fields for embedding generation
        text = f"{document.get('description', '')} {document.get('name', '')} {document.get('species', '')} {document.get('type', '')}"
        embedding = embeddings_model.encode([text])[0].tolist()

        # Add embedding to the document
        document["embedding"] = embedding

        # Index document into Elasticsearch
        res = es_client.index(index="pokemon", body=document)

        return {"message": "Document added successfully", "elasticsearch_response": res}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to add document: {str(e)}")


@router.get("/document/{doc_id}")
async def get_document(doc_id: str):
    try:
        # Retrieve document from Elasticsearch by ID
        res = es_client.get(index="pokemon", id=doc_id)

        # Check if document exists in the response
        if res["found"]:
            document = res["_source"]
            return JSONResponse(content=document)
        else:
            raise HTTPException(
                status_code=404, detail=f"Document with ID '{doc_id}' not found"
            )

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to retrieve document: {str(e)}"
        )


@router.patch("/document/{doc_id}")
async def update_document(doc_id: str, update_data: dict = Body(...)):
    try:
        # Combine updated fields for embedding generation if any of the fields are updated
        text = ""
        if "description" in update_data:
            text += update_data["description"] + " "
        if "name" in update_data:
            text += update_data["name"] + " "
        if "species" in update_data:
            text += update_data["species"] + " "
        if "type" in update_data:
            text += update_data["type"] + " "
        if text:
            embedding = embeddings_model.encode([text.strip()])[0].tolist()
            update_data["embedding"] = embedding

        # Update document in Elasticsearch by ID
        res = es_client.update(index="pokemon", id=doc_id, body={"doc": update_data})

        if res["result"] == "updated":
            return {"message": f"Document with ID '{doc_id}' updated successfully"}
        else:
            raise HTTPException(
                status_code=404, detail=f"Document with ID '{doc_id}' not found"
            )
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to update document: {str(e)}"
        )


@router.delete("/document/{doc_id}")
async def delete_document(doc_id: str):
    try:
        # Delete document from Elasticsearch by ID
        res = es_client.delete(index="pokemon", id=doc_id)

        # Check if deletion was successful
        if res["result"] == "deleted":
            return {"message": f"Document with ID '{doc_id}' deleted successfully"}
        else:
            raise HTTPException(
                status_code=404, detail=f"Document with ID '{doc_id}' not found"
            )

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to delete document: {str(e)}"
        )


@router.get("/documents")
async def get_all_documents():
    try:
        # Search for all documents in Elasticsearch
        res = es_client.search(
            index="pokemon", body={"query": {"match_all": {}}}, size=1000
        )

        # Extract IDs and English names from the response
        documents = [
            {"id": hit["_id"], "name": hit["_source"]["name"]["english"]}
            for hit in res["hits"]["hits"]
        ]

        return JSONResponse(content=documents)

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to retrieve documents: {str(e)}"
        )


@router.get("/semantic_search")
async def semantic_search(query: str = Query(...)):
    try:
        # Generate the query embedding
        query_embedding = embeddings_model.encode([query])[0].tolist()

        # Perform the similarity search in Elasticsearch
        script_query = {
            "script_score": {
                "query": {"match_all": {}},
                "script": {
                    "source": "cosineSimilarity(params.query_vector, 'embedding') + 1.0",
                    "params": {"query_vector": query_embedding},
                },
            }
        }

        response = es_client.search(
            index="pokemon", body={"size": 5, "query": script_query}
        )

        # Extract the descriptions and scores from the response
        documents = [
            {
                "id": hit["_id"],
                "description": hit["_source"]["description"],
                "score": hit["_score"],
            }
            for hit in response["hits"]["hits"]
        ]

        return JSONResponse(content=documents)

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to perform semantic search: {str(e)}"
        )


@router.get("/assistant/ask/stream")
async def ask_stream(question: str = Query(...)):
    try:
        # Process the text using LLMAssistant
        return EventSourceResponse(DefaultAssistant.process(question))

    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=f"Failed to process text: {str(e)}")
