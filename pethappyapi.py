from typing import Optional
from flask import Flask, request, jsonify
from flask_pydantic_spec import FlaskPydanticSpec, Response, Request
from pydantic import BaseModel
from tinydb import TinyDB, Query

server = Flask(__name__)
spec = FlaskPydanticSpec('flask', title='PetHappyAPI')
spec.register(server) #registra os endpoints do servidor 'server'
database = TinyDB('database.json') # "persiste isso aqui pra mim num arquivo database.json"


class Pessoa(BaseModel):
    id: Optional[int]
    nome: str
    idade: int

class Pessoas(BaseModel):
    pessoas: list[Pessoa]
    count: int

@server.get('/pessoas') #_Rota, endpoint, recurso ...
@spec.validate(resp=Response(HTTP_200=Pessoas))
def buscar_pessoas():
    """Retorna todas as Pessoas da base de dados"""
    return jsonify(
        Pessoas(
            pessoas=database.all(),
            count=len(database.all())
        ).dict()
    )

    

@server.post('/pessoas')
@spec.validate(body=Request(Pessoa), resp=Response(HTTP_200=Pessoa) ) # HTTP_200=Pessoa Lê-se que o OK dessa resposta 200 é a classe Pessoa
def inserir_pessoas():
    """Insere uma Pessoa na base de dados"""
    body = request.context.body.dict()
    database.insert(body) # insere uma Pessoa no database
    return body
    
server.run()