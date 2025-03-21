import requests
import json

# Credenciales de la aplicación de Facebook
app_id = "1041818674491633"
app_secret = "3cc02c3b831b8ed65ef8b3088385693a"
# Página/usuario de Facebook que quieres consultar
page_id = "568673773003284"  # Puedes usar "me" para tu propia página o el ID de la página
# Token de acceso (necesitas un token con permisos pages_read_engagement, pages_show_list, pages_read_user_content)
user_access_token = "EAAOzh1ADcPEBO9XGHvEudgxcBZAiZBv5tMTjxpRGpbAHXKMwbLp6YY9Y5yWE9VGpCfFv6dUEPcz3p4Xucw3Jq4Nxiojr53I3O7x5C5ZCs694XYSA1P18u76ogZB9jKYz6ZAD91mXVFkb7hUYk8F6chtkvCApiVvSvIkZAUv077brtR0J1kPlTtSZCZB1t4KUHXkjR5DcP6CTPkvpxGaevZB5t8VS4pjYZD"


def get_long_lived_token():
    """Obtiene un token de larga duración intercambiando el token actual."""
    url = "https://graph.facebook.com/v22.0/oauth/access_token"
    params = {
        "grant_type": "fb_exchange_token",
        "client_id": app_id,
        "client_secret": app_secret,
        "fb_exchange_token": user_access_token
    }
    response = requests.get(url, params=params)
    data = response.json()
    return data["access_token"]
print(get_long_lived_token())