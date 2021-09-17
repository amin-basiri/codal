# Codal

Codal is a django website to dealing with codal.ir Letters

## Installation

Run above commands to create network to use program

```bash
docker network create codal_network
```

## Usage
To run application just run above command
```python
docker-compose up -d
```

## Run Celery
To Run Celery Workers
```python
celery -A codal worker -l info -P solo
```
To Run Celery Beat
```python
celery -A codal beat -l info
```

## Purge Celery
To clear all pending celery tasks
```python
celery -A codal purge
```

To check redis
```python
docker exec -it redis redis-cli ping
```

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

Please make sure to update tests as appropriate.

## License
[Amin-Bs](https://choosealicense.com/licenses/mit/)