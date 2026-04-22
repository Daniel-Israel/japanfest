# Backend do projeto JapanFest Fukushima

## Execução
1. Builde a imagem docker do backend
```
docker build -t backend-festival:1.0 .
```
2. Execute o backend e o bd postgres
```
docker compose up -d
```
3. Acesse http://localhost:8000/docs


## DEV

1. Crie a venv python
```
python3.13 -m venv venv
```
2. Instale as dependências do backend
```
pip install -r requirements.txt
```
3. Execute a API em modo de desenvolvimento
```
fastapi dev app/api/routes.py
```