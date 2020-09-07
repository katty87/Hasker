# Hasker


### Hasker

Simple version of stackoverflow.

### Requirements

 - Python 3.0 or later
 - Docker
 - Django
 - PosgreSQL

### Using

To start execute command:

```
docker-compose up
```  
After building tests run. 
If tests passed successfully server starts at the 80 port at container. Container's port 80 maps at 8000 port at localhost.
You can start using server at  http://localhost:8000/ 

### Tests 

Tests run automatically after container build. If you want to run them manually use

```
python3 manage.py test 
```




