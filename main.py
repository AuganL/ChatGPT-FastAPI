from typing import Union
from fastapi import FastAPI, Request, Body
import uvicorn
from pydantic import BaseModel
import requests
import json
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# 解决跨域
origins = [
    "*",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def send_message(message: str) -> Union[str, None]:
    url = 'https://api.openai.com/v1/completions'.format(token='token')
    headers = {'Content-Type': 'application/json', 'Authorization': 'Bearer {token}'.format(token='YOUR_API_KEY')} # YOUR_API_KEY
    data = {
          "model": "text-davinci-003",
          "prompt": message,
          "max_tokens": 2048,          
          "temperature": 0.9,
          "top_p": 1,
          "frequency_penalty": 0,
          "presence_penalty": 0,
        }
    data = json.dumps(data)
    try:
        response = requests.post(url, headers=headers, data=data)
        return response.json()
    except Exception as e:
        return None

class res(BaseModel):
    code: int
    message: str

def returnMessage(message: str) -> str:
    response = send_message(message)
    if response is None:
        return res(code=500, message="Error")
    if response['choices'] is None:
        return res(code=500, message="Error")
    message_res = response['choices'][0]['text']
    
    message_json = res(code=200, message=message_res)
    return message_json


@app.exception_handler(RequestValidationError)
async def request_validation_exception_handler(request: Request, exc: RequestValidationError):
    print(f"参数不对{request.method} {request.url}")
    return JSONResponse({"code": "400", "message": exc.errors()})

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.post("/api/chat")
async def  chat(
    message: str = Body(..., embed=True)
):
    return returnMessage(message)

if __name__ == "__main__":
    uvicorn.run(app='main:app', host='127.0.0.1', port=8100, reload=True)