## /auth/login/
> description: login system (jwt salt by settings.SECRET_KEY)

> method: POST

> params:
```json
{
  "username" : string,
  "password: : string
}
```

> return:
```json
{
  "token" : string
}
```
> exception:
```json
status_code = 401
{
  detail: string,
  code: string
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
  "id": int
  "username": string,
  "role": {
    "permissions": [
      {
        "permissionId": string,
        "actionList": ["add", "change", "delete", "view"]
      }
    ]
  },
  "menus": [
    {
      "name": string,
      "key": string,
      "component": string,
      "meta": { "title": string},
      "children": []
    }
  ]
}
```
