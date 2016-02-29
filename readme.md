# Zoho Timesheet
----------------
Wraps different hour logging endpoints from Zoho Support and Projects into a single service with a unified interface. (Current only Zoho Support).


## Endpoints
All requests require authentication either via cookie obtained from a `POST` to the `.../v1/rpc/login` endpoint or by providing credentials per request in the request's headers (under `username` as well as `auth_token`).

Arguments are provided in the query tail for `GET` and `DELETE` requests. For both `PUT` and `POST` arguments are supplied in the request body as `JSON`.  

Response body will always be a JSON result, unless the endpoint doesn't need to return - in which case it will return a UTF-8 string of 'Success'.

### Login `/v1/rpc/login`
This endpoint provides a authentication cookie to the client which can be used to authenticate subsequent requests.

#### `POST`
Provide username and password in exchange for authentication cookie.

##### Request
| Argument  | Required | Type   |
| --------- | :------: | :----: |
| username  | yes      | string |
| password  | yes      | string |

##### Response
```
Success
```

#### `DELETE`
Removes the cooking from the client.

### Projects `/v1/resources/projects`
Provides interface to user's projects which can have time logged against them.

#### `GET`
Returns projects for user.

##### Request
N/a

##### Response
```javascript
[
    {
          "id": 1,
        "name": "Zoho Timesheet"
    },
    ...
]
```

### Logs `/v1/resources/logs`
Provides an interface to the user's time logs for projects.

#### `GET`
Returns all the users time logs.

##### Request
N/a

##### Response
```javascript
[
    {
                "id": 1,
        "project_id": 123456789,
              "task": "Working 9 till 5",
             "start": 123456789,
               "end": 123456789,
          "billable": true,
             "notes": "That's a lie; it's way past 5."
    },
    ...
]
```

#### `POST`
Insert a new log entry for a project. Logs that meet minimum requirements of `project_id`, `task`, `start` and `end` will be submitted to Zoho. Otherwise they will be submitted once they are amended by a successive `PUT` which allows them to meet the minimum requirements.

##### Request
| Argument   | Required | Type    | Default |
| ---------  | :------: | :-----: | :-----: |
| project_id | yes      | string  | N/a     |
| task       | yes      | string  | N/a     |
| start      | no       | number  | NOW()   |
| end        | no       | number  | null    |
| billable   | no       | boolean | true    |
| notes      | no       | string  | null    |

```javascript
{
    "project_id": 123456789,
          "task": "Working 9 till 5",
         "start": 123456789,
           "end": 123456789,
      "billable": true,
         "notes": "That's a lie; it's way past 5."
}
```

##### Response
```javascript
[
    {
                "id": 1,
        "project_id": 123456789,
              "task": "Working 9 till 5",
             "start": 123456789,
               "end": 123456789,
          "billable": true,
             "notes": "That's a lie; it's way past 5."
    },
    ...
]
```

#### `POST`
Update an existing log entry with new values. If updating the record adds or removes the necessary components for it to be submitted to Zoho then the corrosonding Zoho record will be create/updated or deleted.

##### Request
| Argument   | Required | Type    |
| ---------  | :------: | :-----: |
| project_id | no       | number  |
| task       | no       | string  |
| start      | no       | number  |
| end        | no       | number  |
| billable   | no       | boolean |
| notes      | no       | string  |

```javascript
{
    "project_id": 123456789,
          "task": "Working 9 till 5",
         "start": 123456789,
           "end": 123456789,
      "billable": true,
         "notes": "That's a lie; it's way past 5."
}
```

##### Response
```javascript
{
            "id": 1,
    "project_id": 123456789,
          "task": "Working 9 till 5",
         "start": 123456789,
           "end": 123456789,
      "billable": true,
         "notes": "That's a lie; it's way past 5."
}
```

#### `DELETE`
Deletes a record and it's corresponding Zoho record (if exists).

##### Request
| Argument   | Required | Type    |
| ---------  | :------: | :-----: |
| project_id | yes      | number  |

##### Response
```
Success
```
