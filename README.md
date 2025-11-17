# Ask-Marc MCP Service
A bridge for OpenRemote to communicate with AI models like ChatGPT or Claude. And provide configuration to connect them to tools using MCP.


## Installation
1. **Create service user**

    In your OpenRemote instances, create a new service user and give it the permissions you want to have.
    Ask-Marc will auto discover the tools that are available.

   2. **Setup docker services**
  
       Create a docker-compose.yml file, and configure the service.
       ```yaml
      services:
        # Other OpenRemote services...
      
        ask-marc:
          image: ########
          restart: always
          depends_on:
            manager:
              condition: service_healthy
          ports:
            - "8042:8042"
          environment:
            OPENAI_API_KEY=
            OPENREMOTE_CLIENT_ID=<OPENREMOTE_CLIENT_ID>
            OPENREMOTE_CLIENT_SECRET=<OPENREMOTE_CLIENT_SECRET>
            OPENREMOTE_URL=<OPENREMOTE_URL>
            OPENREMOTE_VERIFY_SSL=1
      ```

If the service user is setup correctly the Ask-Marc service will auto register to OpenRemote and you can see the service on the dashboard!

## Development guide

### Backend (MCP client & server)
1. **Create service user**

    In your OpenRemote instances, create a new service user and give it the permissions you want to have.
    Ask-Marc will auto discover the tools that are available.


2. **Install packages**
    ```shell
    uv sync
    ```

3. **Setup environment variables**
    
    Create a new file `.env` in the root of the project directory. and fill in the following variables replacing the brackets with your own values.
    ```dotenv
    OPENAI_API_KEY=
    OPENREMOTE_CLIENT_ID=<OPENREMOTE_CLIENT_ID>
    OPENREMOTE_CLIENT_SECRET=<OPENREMOTE_CLIENT_SECRET>
    OPENREMOTE_URL=<OPENREMOTE_URL>
    OPENREMOTE_VERIFY_SSL=1
    ```

4. **Run the server**
    ```shell
    uvicorn app:app --reload
    ```
