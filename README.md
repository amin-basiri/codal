# Codal

Codal is a django website to dealing with codal.ir Letters


## Usage
First make sure you have docker installed in your os.

To run application just run below command
```python
docker-compose up -d
```
To prepare database to use:
```python
docker exec -it web python manage.py makemigrations
docker exec -it web python manage.py migrate
```
To create a user and use codal administration
```python
docker exec -it web python manage.py createsuperuser
```
Then Enjoy Codal Administration In localhost


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

## Check Redis
```python
docker exec -it redis redis-cli ping
```

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

Please make sure to update tests as appropriate.

## License
[Amin-Bs](https://choosealicense.com/licenses/mit/)