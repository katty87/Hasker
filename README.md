# Hasker


### Hasker

Simple version of stackoverflow.

### Requirements

 - Python 3.6+
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

### API

#### Get all questions

Return all questions with pagination

```http
GET /api/questions/?page=1&page_size
```
| Parameter | Type | Description |
| :--- | :--- | :--- |
| `page` | `integer` | Page number |
| `page_size` | `integer` | Number of questions by page. Default: 20 |

#### Get question details

Return question details

```http
GET /api/questions/<id>
```

#### Get question answers

Return all question answers with pagination

```http
GET /api/questions/<id>/answers?page=1&page_size
```
| Parameter | Type | Description |
| :--- | :--- | :--- |
| `page` | `integer` | Page number |
| `page_size` | `integer` | Number of answers by page. Default: 20 |


#### Get trending questions

Return 20 most popular questions 

```http
GET /api/questions/trending
```

#### Get new questions

Return all questions sorted by create date with pagination

```http
GET /api/questions/new
```

| Parameter | Type | Description |
| :--- | :--- | :--- |
| `page` | `integer` | Page number |
| `page_size` | `integer` | Number of answers by page. Default: 20 |


#### Get hot questions

Return all questions sorted by vote count with pagination

```http
GET /api/questions/hot
```

| Parameter | Type | Description |
| :--- | :--- | :--- |
| `page` | `integer` | Page number |
| `page_size` | `integer` | Number of answers by page. Default: 20 |

#### Get API documentation

Return  swagger scheme. Without format parameter return UI scheme

```http
GET /api/swagger
```

| Parameter | Type | Description |
| :--- | :--- | :--- |
| `format` | `string` | Format type: .json|.yaml |


Documentation

```http
GET /api/redoc
```

### Tests 

Tests run automatically after container build. If you want to run them manually use

```
python3 manage.py test 
```




