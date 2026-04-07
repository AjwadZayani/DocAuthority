docker build -t docauthority-identity . && docker run --env-file .env --network container:local-kafka docauthority-identity
