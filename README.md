# Timesheet [![Build Status](https://travis-ci.org/JamesStidard/Timesheet-Server.svg?branch=master)](https://travis-ci.org/JamesStidard/Timesheet-Server)
Unified endpoint for hours logging for multiple services, such as: Zoho Projects and Support.

## General Architecture
Wraps the API's of the provided integrations giving a unified REST-like API.

A `User` has multiple `Integrations` and multiple `Logs`.

A `Project` persisted in the model; actions performed on the `timesheet.handlers.resources.project_handler` just delegate to the integrated services - Getting each of the user's integrations and running a `get_projects` for each and returning the cumulative result. The result will hold the `integration_id` of the integration which acquired the project and the `id` used to identify that project again on the integrated service. the `integration_id` allows us to target subsequent requests to the correct service and the `id` allows us to retarget the correct resource. In future, persisting the `Project` objects with a relationship to the integration source would get rid of the need for the client to know about the `integration_id`.

`Logs` can be created against a `Project` and require both the `project_id` and the `integration_id` to be created (as described above). These time logs are persisted to the database and will be kept in sync with the integrated service it's project was acquired from. If the `Log` doesn't have all the required fields to allow it to be created on the integrated service the entry is either never added or is removed until the time it has been updated to allow it to be uploaded to the integrated service.

Each `Integration` that is added to the system defines its own get, insert, update and delete methods and registers them to the appropriate `functools.singledispatch` function. This gives a extendable way to define new service integrations.

### Defining an Integration
Integrations are defined by subclassing the SQLAlchemy `Integration` class, adding any additionally required properties (columns), describing itself with a unique `polymorphic_identity` value, setting their `__tablename__` to None and overriding the `Log` class (found at: `timesheet.model.log`) method to give access to the integration's specific `Log` subclass.

Defining a integration also requires an integration specific subclass of `Log` (found at: `timesheet.model.log`) which sets the `__tablename__` to None, describes itself with a unique `polymorphic_identity` value. The `Log` subclass should also override the `completed` method which evaluated if all required fields have been entered which would allow it to be passed to the integrated service.

For the different integrations to handle their own respective services API they must register to the single dispatches `timesheet.dispatches.get_projects`, `timesheet.dispatches.insert_log`, `timesheet.dispatches.update_log` and `timesheet.dispatches.delete_log` functions. These will register with their respective integrations. `get_projects` will receive an instance of their `Integration` subclass and should return an array of projects with a `id` and `name` property. The log functions will receive an instance of their `Log` subclass and should return the services `id` after successful inserts and updates or throw and exception. Delete will infer its success based on if an exception is raised.

Finally, the `Integration` and `Log` subclasses need to be added to the `timesheet.model.__init__` imports so they can be added to the `Base` for database initialization and the dispatch function imports should be added to the end of the appropriate dispatches file in `timesheet.dispatches`.  


## Endpoints
All requests require authentication either via cookie obtained from a `POST` to the `.../v1/rpc/login` endpoint or by providing credentials per request in the request's headers (under `username` as well as `auth_token`).

Arguments are provided in the query tail for `GET` and `DELETE` requests. For both `PUT` and `POST` arguments are supplied in the request body as `JSON`.  

Response body will always be a JSON result, unless the endpoint doesn't need to return - in which case it will return a UTF-8 string of 'Success'.


#### Login `/v1/rpc/login`
------------------------------
This endpoint provides a authentication cookie to the client which can be used to authenticate subsequent requests.

##### `POST`
Provide username and password in exchange for authentication cookie.

###### Request
| Argument  | Required | Type   |
| --------: | :------: | :----: |
| username  | yes      | string |
| password  | yes      | string |

###### Response
```
Success
```

##### `DELETE`
Removes the cooking from the client.


#### Projects `/v1/resources/projects`
------------------------------
Provides interface to user's projects which can have time logged against them.

##### `GET`
Returns projects for all integrated services for the user user. The result is returned in the order which best match the query provided (i.e. the first item being the one which Timesheet is most confident is the `Project` the search query is looking for).

###### Request
| Argument | Required | Type   |
| -------: | :------: | :----: |
| query    | no       | string |
| limit    | no       | int    |

###### Response
```javascript
{
    "result": [
        {
                        "id": 1,
            "integration_id": 10,
                      "name": "Zoho Timesheet"
        },
        ...
    ]
}
```


#### Logs `/v1/resources/logs`
------------------------------
Provides an interface to the user's time logs for projects.

##### `GET`
Returns all the users time logs which are in the Timesheet database.

###### Request
`n/a`

###### Response
```javascript
{
    "result": [
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
}
```

##### `POST`
Insert a new log entry for a project. Logs that meet minimum requirements of `project_id`, `task`, `start` and `end` will be submitted to Zoho. Otherwise they will be submitted once they are amended by a successive `PUT` which allows them to meet the minimum requirements.

###### Request
| Argument       | Required | Type    | Default |
| -------------: | :------: | :-----: | :-----: |
| project_id     | yes      | int     | `n/a`   |
| integration_id | yes      | int     | `n/a`   |
| task           | yes      | string  | `n/a`   |
| start          | no       | number  | `NOW`   |
| end            | no       | number  | null    |
| billable       | no       | boolean | true    |
| notes          | no       | string  | null    |

```javascript
{
        "project_id": 123456789,
    "integration_id": 10,
              "task": "Working 9 till 5",
             "start": 123456789,
               "end": 123456789,
          "billable": true,
             "notes": "That's a lie; it's way past 5."
}
```

###### Response
```javascript
{
    "result": {
                "id": 1,
        "project_id": 123456789,
              "task": "Working 9 till 5",
             "start": 123456789,
               "end": 123456789,
          "billable": true,
             "notes": "That's a lie; it's way past 5."
    }
}
```

##### `POST`
Update an existing log entry with new values. If updating the record adds or removes the necessary components for it to be submitted to Zoho then the corresponding Zoho record will be create/updated or deleted.

###### Request
| Argument   | Required | Type    |
| ---------: | :------: | :-----: |
| task       | no       | string  |
| start      | no       | number  |
| end        | no       | number  |
| billable   | no       | boolean |
| notes      | no       | string  |

```javascript
{
          "task": "Working 9 till 5",
         "start": 123456789,
           "end": 123456789,
      "billable": true,
         "notes": "That's a lie; it's way past 5."
}
```

###### Response
```javascript
"result": {
            "id": 1,
    "project_id": 123456789,
          "task": "Working 9 till 5",
         "start": 123456789,
           "end": 123456789,
      "billable": true,
         "notes": "That's a lie; it's way past 5."
}
```

##### `DELETE`
Deletes a record and it's corresponding Zoho record (if exists).

###### Request
| Argument | Required | Type    |
| -------: | :------: | :-----: |
| id       | yes      | number  |

###### Response
```
Success
```
