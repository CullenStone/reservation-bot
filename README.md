# Build docker container
`docker build -t tatiana:dev .`

# Run docker container
`docker run -it -v /dev/shm:/dev/shm --env-file ./.docker_env tatiana:dev /bin/bash`