from Health_agent import run_agent
import uvicorn
from pydantic import BaseModel
from fastapi import FastAPI
from typing import List, Dict, Any
from fastapi.middleware.cors import CORSMiddleware


class ConversationRequest(BaseModel):
    task: str
    conv: List[Dict[str, Any]]
   
   

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Allow only this origin
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods (POST, GET, etc.)
    allow_headers=["*"],  # Allow all headers
)

@app.get("/health_check")
def health_check():
    return {"status": "ok"}



@app.post("/generate")
def generate_endpoint(request: ConversationRequest):
    # Extract data from the request
    try:
        
      
        response = run_agent(request.task, request.conv)
        return {"response":response}
        
    except:
        return {"response":"there has been an error in generating response"}



if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)
