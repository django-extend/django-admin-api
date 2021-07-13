# auth api list
## /auth/login/
> description: login system (jwt salt by settings.SECRET_KEY)

> method: POST

> params:
```json
{
  "username" : "string",
  "password" : "string",
}
```

> return:
```json
{
  "token" : "string"
}
```
> exception:
```json
status_code = 401
{
  "detail": "string",
  "code": "string"
}
```

## /auth/logout/
> description: logout system (clean token)

> method: POST

> params: None

> return: `{}`

## /auth/userinfo/
> description: get login user's information (frontend need dymic build menus and actions)

> method: GET

> header: `Bearer {token}`

> params: None

> return:
```json
{
  "id": "int",
  "username": "string",
  "role": {
    "permissions": [
      {
        "permissionId": "string",
        "actionList": ["add", "change", "delete", "view"]
      }
    ]
  },
  "menus": [
    {
      "name": "string",
      "key": "string",
      "component": "string",
      "meta": { "title": "string"},
      "children": []
    }
  ]
}
```

# resource api list
## /resource/{app}/{model}/
> description: list models' objects

> method: GET

> params: None

> return:
```json
{
  "message": "string",
  "status": "int",
  "result": {
    "pageSize": "int",
    "pageNo": "int",
    "totalPage": "int",
    "totalCount": "int",
    "data": [],
  },
  "columns": [
    {
      "title": "string",
      "dataIndex": "string"
    }
  ],
  "slots": {
    "{slot_name}": ["{component}", "{params}"]
  },
  "actions": {
    "onTop": "boolean",
    "onButton": "boolean",
    "showSelection": "boolean",
    "items": [
      {
        "name": "string",
        "action": "{action_name}"
      }
    ]
  }
}
```

## /resource/{app}/{model}/
> description: create models' object

> method: POST

## /resource/{app}/{model}/{id}/
> description: models' detail

> method: GET

## /resource/{app}/{model}/{id}/
> description: update model's object

> method: PUT or PATCH

## /resource/{app}/{model}/{id}/
> description: delete model's object

> method: DELETE

## /resource/{app}/{model}/
> description: get models' meta info (frontend need dymic create from)

> method: OPTION

> params: None

> return:
```json
{
  "name": "string",
  "actions": {
    "POST": {
      "{field}": {
        "type": "string",
        "inputy_type": "string",
        "required": "boolean",
        "read_only": "boolean",
        "write_only": "boolean",
        "label": "string",
        "max_length": "int",
        "help_text": "string",
        "field_ype": "string"
      }
    }
  },
  "fieldsets": [
    [
      "{fieldset_name}",
      {
        "fields": [
          "{field1}",
          "{field2}"
        ]
      }
    ]
  ],
  "addFieldsets": []
}
```
## /resource/{app}/{model}/action_{action_name}/
> description: custom action (wrapper of ModelAdmin.actions)

> method: POST

> params: 
```json
{
  "ids": [],
  "all": "boolean"
}
```

## /resource/{app}/{models}/filters/
> description: get filters of listview (wrapper of ModelAdmin.list_filter, search_fields)

> method: GET

> params: None

> return:
```json
{
  "list_filter": [
    {
      "key": "string",
      "label": "string",
      "choices": [
        ["{choice_key}", "{choice_label}"]
      ]
    }
  ],
  "search_fields": [
    {
      "key": "string",
      "label": "string"
    }
  ]
}
```

## /resource/{app}/{model}/{id}/str/
> description: get object's simple-show (use by ForeignKey choice)

> method: GET

> params: None

> return:
```json
{
  "str": "string"
}
```

## /resource/{app}/{model}/autocomplete/
> description: wrapper of ModelAdmin.autocomplete_fields

> method: GET

> params: None

> return:
```json
{
  "message": "string",
  "status": "int",
  "result": {
    "pageSize": "int",
    "pageNo": "int",
    "totalPage": "int",
    "totalCount": "int",
    "data": [
      {
        "key": "string",
        "label": "string"
      }
    ],
  },
```
