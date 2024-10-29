# test project

Using this API you can manage Post and Comments. When creating post or comment
its text checked by AI on containing offensive language. User can enable automatic response
feature for his post and set delay for that answer. There is everyday statistics on created/blocked comments

Vertex AI used for AI generation and validation. It hosted on separate google cloud project
and accessed through service account, that have rights only to interact with AI.

#### Technologies:
- Python == 3.10
- Fast Api == 0.115.0
- MongoDB == 7.0.14
- Pytest == 8.3.3
- Docker == 27.2.1
- docker-compose == 2.29.2

#### Environment variables:
    Application have next environment variables:
      
      REQUIRED:
        - MONGO_URL - Connection string to MongoDB. REQUIRED if application is started manually. It is already placed in a yml file to run through docker
        - SECRET_KEY - Used to encrypt and decrypt JWT token. You can generate it with this command: openssl rand -hex 32 

      OTHER:
        - ALGORITHM - Type of algorithm used in JWT encoding process. Default value - HS256
        - ACCESS_TOKEN_LIFETIME_MINUTES - Defines JWT token lifetime. Default value - 15 minutes
        - DATABASE_NAME - Name of database. Default value - starnavi.
        - LOGS_ENABLED - Turns on or off logging. Default value - True.
        - USE_AI_FOR_TEXT_VALIDATION - Turns on or off AI text validation. Default value - True
        - AI_MODEL_NAME - AI model used in project. Default value - gemini-1.5-flash-002.
        - GOOGLE_CLOUD_PROJECT_ID - Id of project on google cloud that use Vertex AI.
        - GOOGLE_CLOUD_PROJECT_LOCATION - Google cloud project location. Default value - us-central1
        - GOOGLE_CLOUD_PROJECT_CREDENTIALS_PATH - Path to project credentials.
  
    Before run application manually or through docker you need to create .env file where REQUIRED variables will be defined. 
  
    If you run application manually create .env in project root directory, if you run through docker create .env inside deployment/local
                

#### Run application with docker:

- ##### Install Docker and docker-compose
        1. Add Docker`s official GPG key:
            sudo apt-get update
            sudo apt-get install ca-certificates curl
            sudo install -m 0755 -d /etc/apt/keyrings
            sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
            sudo chmod a+r /etc/apt/keyrings/docker.asc

        2. Add repository to Apt sources:
            echo \
              "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu \
              $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
              sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
            sudo apt-get update

        3. Install Docker packages:
            sudo apt-get install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

- ##### Run application
        1. From project root go to deployment/local:
            cd deployment/local

        2. Create .env file with environment variables

        3. Run containers using docker-compose:
            docker-compose up --build

#### Run application manually:
    # For Ubuntu 20.04

- ##### Install MongoDB
        1. Import the Public Key
            From a terminal, install gnupg and curl if they are not already available:
              sudo apt-get install gnupg curl

            Import the MongoDB public GPG key:
              curl -fsSL https://www.mongodb.org/static/pgp/server-7.0.asc | \
              sudo gpg -o /usr/share/keyrings/mongodb-server-7.0.gpg \
              --dearmor

        2. Create the List File:
            Create the list file /etc/apt/sources.list.d/mongodb-org-7.0.list for your version of Ubuntu.
            # https://www.mongodb.com/docs/manual/tutorial/install-mongodb-on-ubuntu/#create-the-list-file
            # For Ubuntu 20.04:
              echo "deb [ arch=amd64,arm64 signed-by=/usr/share/keyrings/mongodb-server-7.0.gpg ] https://repo.mongodb.org/apt/ubuntu focal/mongodb-org/7.0 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-7.0.list

        3. Reload the Package Database:
            sudo apt-get update

        4. Install MongoDB:
            sudo apt-get install -y mongodb-org=7.0.14

        5. Start MongoDB:
            sudo systemctl start mongod

- ##### Install Python
        1. Add DeadSnakes PPA:
            sudo add-apt-repository ppa:deadsnakes/ppa
 
        2. Update package list:
            sudo apt update

        3.  Install Python:
            sudo apt install python3.10 -y

- ##### Setup Environment
        1. Install venv package:
            sudo apt install python3.10-venv

        2. Create virtual environment:
            python3.10 -m venv project_env

        3. Go to environment folder and activate it:
            source project_env/bin/activate

        4. Install requirements from application folder:
            pip install -r requirements.txt

- ##### Run application
      1. Go to project root

      2. Create .env file with environment variables

      3. Run application:
        uvicorn app.main:app --reload

#### Run Tests
      1. From root directory run:
        pytest