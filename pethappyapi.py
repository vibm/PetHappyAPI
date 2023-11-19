from itertools import count
from typing import Optional
from flask import Flask, request, jsonify
from flask_pydantic_spec import FlaskPydanticSpec, Response, Request
from pydantic import BaseModel, Field
from tinydb import TinyDB, Query
from tinydb.storages import MemoryStorage

server = Flask(__name__)
spec = FlaskPydanticSpec('flask', title='PetHappyAPI')
spec.register(server) #registra os endpoints do servidor 'server'
database = TinyDB(storage=MemoryStorage) # "persiste isso aqui pra mim num arquivo database.json"
c = count()


class Pessoa(BaseModel):
    id: Optional[int] = Field(default_factory=lambda: next(c))
    nome: str
    idade: int

class Pessoas(BaseModel):
    pessoas: list[Pessoa]
    count: int

## -------->>   GET   <<--------   
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


## -------->>   GET para uma pessoa  <<--------   
@server.get('/pessoas/<int:id>') #_Rota, endpoint, recurso ...
@spec.validate(resp=Response(HTTP_200=Pessoa))
def buscar_pessoa(id): ##  tem que especificar id., por isso '(id)'
    """Retorna uma Pessoa da base de dados"""
    try:
        pessoa = database.search(Query().id == id)[0]
    except IndexError:
        return {'message': 'Pessoa not found'}, 404
    return jsonify(pessoa)


## -------->>   POST   <<--------   
@server.post('/pessoas')
@spec.validate(body=Request(Pessoa), resp=Response(HTTP_200=Pessoa) ) # HTTP_200=Pessoa Lê-se que o OK dessa resposta 200 é a classe Pessoa
def inserir_pessoas():
    """Insere uma Pessoa na base de dados"""
    body = request.context.body.dict()
    database.insert(body) # insere uma Pessoa no database
    return body


## -------->>   PUT   <<--------   
@server.put('/pessoas/<int:id>')
@spec.validate(body=Request(Pessoa), resp=Response(HTTP_201=Pessoa))
def altera_pessoa(id):
    """Altera uma Pessoa do banco de dados"""
    Pessoa = Query() ##Pessoa é só uma variável pra deixar mais simples
    body = request.context.body.dict()
    database.update(body, Pessoa.id == id)
    #database.update(body, Query().id == id) << poderia ser assim, e sem o 'Pessoa = Query()' ali em cima
    return jsonify(body)


## -------->>   DELETE   <<--------   
@server.delete('/pessoas/<int:id>')
@spec.validate(resp=Response('HTTP_204'))
def delete_pessoa(id):
    """Remove uma Pessoa do banco de dados"""
    Pessoa = Query()##Pessoa é só uma variável pra deixar mais simples
    database.remove(Pessoa.id == id) #Remove onde a Pessoa tiver o id igual a 'tal'
    return jsonify({}) # =====> POR DEFINIÇÃO, O DELETE NÃO RETORNA NADA. POR ISSO USA-SE {}

server.run()