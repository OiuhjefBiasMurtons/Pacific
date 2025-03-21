import requests
import json

ig_user_id = "17841465712624860"
app_id = "1041818674491633"
app_secret = "3cc02c3b831b8ed65ef8b3088385693a"
user_access_token = "EAAOzh1ADcPEBOZBHcNaZBLyVnXfOoGSaplMjMKs19VMubZAztkwUvbzKvXF2ZBXOUcUZBSPJT0RjBqnyCOLI8iiByG680zSQqXKoExIWXokSS4wZALn6IZCxHWTdWPiB8liUEFUQQVXgj1n6TkurLL5O7D8QozNLMB6ZAsEpQZAiJOTKZASnJrd1KZAzZAA5ze1q1P3z"

def get_long_lived_token():
    """Obtiene un token de larga duración intercambiando el token actual."""
    url = f"https://graph.facebook.com/v22.0/oauth/access_token"
    params = {
        "grant_type": "fb_exchange_token",
        "client_id": app_id,
        "client_secret": app_secret,
        "fb_exchange_token": user_access_token
    }
    response = requests.get(url, params=params)
    data = response.json()
    return data["access_token"]

def get_user_media(user_id):
    """Obtiene los media items (fotos, videos) de un usuario de Instagram.
    En la API de Instagram Graph, se usa 'media' en lugar de 'posts'."""
    url = f"https://graph.facebook.com/v22.0/{user_id}/media"
    params = {
        "access_token": user_access_token,
        "fields": "id,caption,media_type,media_url,permalink,thumbnail_url,timestamp,username,comments_count,like_count"
    }
    response = requests.get(url, params=params)
    return response.json()

def get_media_comments(media_id):
    """Obtiene los comentarios de una publicación específica,
    incluyendo el nombre de usuario, el texto del comentario y (si está disponible) información del perfil."""
    url = f"https://graph.facebook.com/v22.0/{media_id}/comments"
    params = {
        "access_token": user_access_token,
        "fields": "id,text,username,timestamp,like_count,user{id,username,profile_picture_url}"
    }
    response = requests.get(url, params=params)
    return response.json()

# Obtén primero todas las publicaciones del usuario
media_result = get_user_media(ig_user_id)
print("Publicaciones del usuario:")
print(json.dumps(media_result, indent=2))

# Si hay publicaciones, obtén los comentarios de la primera publicación
def get_comments(media_result):
    if "data" in media_result and len(media_result["data"]) > 0:
        first_media_id = media_result["data"][0]["id"]
        print(f"\nObteniendo comentarios para la publicación con ID: {first_media_id}")
        comments = get_media_comments(first_media_id)
        print("\nComentarios de la publicación:")
        print(json.dumps(comments, indent=2))
            
            # Mostrar detalles de cada comentario de manera más legible
        if "data" in comments and len(comments["data"]) > 0:
            print("\nDetalle de comentarios:")
            for i, comment in enumerate(comments["data"], 1):
                username = comment.get('username', 'No disponible')
                print(f"--- Comentario #{i} ---")
                print(f"Usuario: {username}")
                print(f"Texto: {comment.get('text', 'No disponible')}")
                    
                # Verificar si hay información del usuario y su foto de perfil
                has_profile_pic = "user" in comment and "profile_picture_url" in comment["user"]
                    
                if has_profile_pic:
                    print(f"Foto de perfil: {comment['user']['profile_picture_url']}")
                    print("Tipo: Propietario del token (tu cuenta) o usuario que ha dado permisos")
                else:
                    print("Foto de perfil: No disponible mediante comentarios API")
                    # Intentar obtener la foto de perfil a través de business_discovery
                    if username != 'No disponible':
                        print("Intentando obtener foto de perfil mediante business_discovery...")
                        profile_pic = get_profile_picture(username)
                        if profile_pic:
                            print(f"Foto de perfil (alternativa): {profile_pic}")
                        else:
                            print("No se pudo obtener foto de perfil alternativa")
                        print("Tipo: Comentario de otro usuario - acceso limitado por privacidad")
                    print("")
        else:
                print("No hay comentarios en esta publicación")
    else:
            print("No se encontraron publicaciones para este usuario")

# Si quieres obtener el token de larga duración, descomenta:
# long_lived_token = get_long_lived_token()
# print(f"Token de larga duración: {long_lived_token}")

# El comando curl equivalente como referencia:
# curl -i -X GET \
#  "https://graph.facebook.com/v22.0/17841465712624860 \
#   ?fields=business_discovery.username(bluebottle){followers_count,media_count} \
#   &access_token=EAAOzh1ADcPEBOZBHcNaZBLyVnXfOoGSaplMjMKs19VMubZAztkwUvbzKvXF2ZBXOUcUZBSPJT0RjBqnyCOLI8iiByG680zSQqXKoExIWXokSS4wZALn6IZCxHWTdWPiB8liUEFUQQVXgj1n6TkurLL5O7D8QozNLMB6ZAsEpQZAiJOTKZASnJrd1KZAzZAA5ze1q1P3z"

# Función para obtener información de otro perfil de negocio
def get_business_discovery(ig_user_id, username):
    """Obtiene información de un perfil de negocio de Instagram por su nombre de usuario."""
    url = f"https://graph.facebook.com/v22.0/{ig_user_id}"
    params = {
        "access_token": user_access_token,
        "fields": f"business_discovery.username({username}){{username,profile_picture_url,followers_count,media_count}}"
    }
    response = requests.get(url, params=params)
    return response.json()

def get_profile_picture(username):
    """Intenta obtener la foto de perfil de un usuario a través de business_discovery."""
    try:
        business_info = get_business_discovery(ig_user_id, username)
        if "business_discovery" in business_info and "profile_picture_url" in business_info["business_discovery"]:
            return business_info["business_discovery"]["profile_picture_url"]
    except Exception as e:
        print(f"Error al obtener foto de perfil para {username}: {str(e)}")
    return None

# Descomenta para usar:
# print(get_business_discovery(ig_user_id, "bluebottle"))

get_comments(media_result)