# Dteam IA Chatbot
## API con FastAPI y OpenAI 

- **Paquetes:**

  ```python 
  pip install -r requirements.txt
  ````

## Funciones
- Brindar soporte tecnico a los clientes
- Divulgar servicios y misión de Dteam

## Endpoint
## `POST /chat`
  ### request example {
      "chat_id": "12345",
      "message": "Hola, ¿cómo estás?",
      "secret": "Secret"
  }

  ### response example {
    "chat_id": "12345",
    "message": "Bien...",
    "interactions": 2
  }
