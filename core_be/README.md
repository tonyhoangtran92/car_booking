### Build all images

```sh
docker-compose build
```
### Run containers

```sh
docker-compose up -d
```

### Migrate webapp database

```sh
docker-compose run --rm api python3 manage.py migrate
```

### Create superuser by command

```sh
docker-compose run --rm api python3 manage.py createsuperuser
```