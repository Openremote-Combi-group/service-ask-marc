# service-ask-marc
A bridge for OpenRemote to communicate with AI models like ChatGPT or Claude. And provide configuration to connect them to tools using MCP.



## Setup Developement

### Backend (MCP client & server)
Install packages
```shell
uv sync
```

Run the server
```shell
uvicorn app:app --reload
```

### Frontend (UI only)
Install packages
```shell
cd ui && npm install
```

Run the server
```shell 
npm run dev
```