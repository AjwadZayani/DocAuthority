docker build -t docauthority-identity . && docker run --env-file .env -p 5001:5001 docauthority-identity
