import requests
import json

# Credenciales de la aplicación de Facebook
app_id = "1041818674491633"
app_secret = "3cc02c3b831b8ed65ef8b3088385693a"
# Página/usuario de Facebook que quieres consultar
page_id = "568673773003284"  # Puedes usar "me" para tu propia página o el ID de la página
# Token de acceso (necesitas un token con permisos pages_read_engagement, pages_show_list, pages_read_user_content)
user_access_token = "EAAOzh1ADcPEBO2bJZCIEVuhjkQQhE9lEsrRdYMd6hfI23p3TGTqZAl0ZBrZAsPJuQZAwxR5FiljofydUi0tHSlB4mDnHmTY0xBLKLBLXteJ2w3wE9rEVmXuNj8J2hYT1X5qnnecZBr5F8FkpwTq2TdLq1IKBx81y2AJgG3ZBfkMCbzQkpOBztxKPZBoBHh13dTqd"


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


def get_page_access_token(page_id="me"):
    """Obtiene el token de acceso específico para una página."""
    url = f"https://graph.facebook.com/v22.0/{page_id}"
    params = {
        "fields": "access_token",
        "access_token": user_access_token
    }
    response = requests.get(url, params=params)
    data = response.json()
    if "error" in data:
        print(f"Error al obtener token de página: {data['error']['message']}")
        print("Por favor, verifica que:")
        print("1. El usuario tenga permisos de administrador en la página")
        print("2. El token tenga los permisos: pages_read_engagement, pages_show_list, pages_read_user_content")
        print("3. La aplicación tenga configurada la API de Facebook y los permisos adecuados")
        return user_access_token
    return data.get("access_token", user_access_token)

# Verificar los permisos del token de usuario
def check_token_permissions():
    """Verifica los permisos del token de usuario."""
    url = "https://graph.facebook.com/v22.0/debug_token"
    params = {
        "input_token": user_access_token,
        "access_token": f"{app_id}|{app_secret}"  # Se usa app_id|app_secret como token de acceso
    }
    response = requests.get(url, params=params)
    data = response.json()
    
    if "data" in data:
        print("\n--- Información del token ---")
        if "scopes" in data["data"]:
            print("Permisos del token:")
            for permission in data["data"]["scopes"]:
                print(f"- {permission}")
            
            # Verificar permisos específicos necesarios
            required_permissions = ["pages_read_engagement", "pages_show_list", "pages_read_user_content"]
            missing_permissions = [p for p in required_permissions if p not in data["data"]["scopes"]]
            
            if missing_permissions:
                print("\n¡ATENCIÓN! Faltan estos permisos importantes:")
                for p in missing_permissions:
                    print(f"- {p}")
                print("\nDebes solicitar estos permisos en tu aplicación de Facebook Developer.")
        
        if "app_id" in data["data"]:
            print(f"\nID de la aplicación: {data['data']['app_id']}")
        if "expires_at" in data["data"]:
            print(f"El token expira en: {data['data']['expires_at']}")
    return data

# Primero verificamos los permisos del token
token_info = check_token_permissions()

# Obtenemos el token de página 
page_token = get_page_access_token(page_id)
print(f"Token de página obtenido: {page_token[:20]}...") # Mostramos solo el inicio por seguridad

# Obtener publicaciones
def get_user_posts(page_id="me", limit=10, access_token=None):
    """Obtiene las publicaciones de una página o usuario de Facebook."""
    if access_token is None:
        access_token = user_access_token
        
    url = f"https://graph.facebook.com/v22.0/{page_id}/posts"
    params = {
        "access_token": access_token,
        "limit": limit,
        "fields": "id,message,created_time,permalink_url,full_picture,reactions.summary(true),comments.summary(true),shares"
    }
    response = requests.get(url, params=params)
    data = response.json()
    
    # Manejar errores específicos
    if "error" in data:
        error_msg = data["error"]["message"]
        error_code = data["error"].get("code", "desconocido")
        
        print(f"\nError ({error_code}): {error_msg}")
        
        if "Missing Permissions" in error_msg:
            print("\nSolución recomendada:")
            print("1. Visita https://developers.facebook.com/tools/explorer/")
            print("2. Selecciona tu aplicación")
            print("3. Genera un nuevo token de usuario con los siguientes permisos:")
            print("   - pages_read_engagement")
            print("   - pages_show_list")
            print("   - pages_read_user_content")
            print("   - pages_manage_posts (si necesitas publicar)")
            print("4. Asegúrate de ser administrador de la página")
            
        if "User Access Token Is Not Supported" in error_msg:
            print("\nEste error indica que necesitas un token específico de página para esta operación.")
            print("Asegúrate de que el token de página se obtuvo correctamente.")
            
    return data

# Función para probar el acceso con diferentes tokens
def test_access():
    """Prueba diferentes métodos de acceso para diagnosticar problemas."""
    print("\n--- Pruebas de acceso ---")
    
    # 1. Probar acceso a información básica de la página con token de usuario
    print("\n1. Probando acceso básico a la página con token de usuario:")
    url = f"https://graph.facebook.com/v22.0/{page_id}"
    params = {"access_token": user_access_token, "fields": "name,category,fan_count"}
    response = requests.get(url, params=params)
    data = response.json()
    print(json.dumps(data, indent=2))
    
    # 2. Probar acceso con token de página
    print("\n2. Probando acceso básico a la página con token de página:")
    params["access_token"] = page_token
    response = requests.get(url, params=params)
    data = response.json()
    print(json.dumps(data, indent=2))
    
    # 3. Probar acceso a publicaciones (feed) en lugar de posts
    print("\n3. Probando acceso al feed de la página con token de página:")
    url = f"https://graph.facebook.com/v22.0/{page_id}/feed"
    params = {
        "access_token": page_token,
        "limit": 5,
        "fields": "id,message,created_time"
    }
    response = requests.get(url, params=params)
    data = response.json()
    print(json.dumps(data, indent=2))
    
    return True

# Ejecutar las pruebas de acceso
test_access()

# Obtener publicaciones usando el token de página
posts_result = get_user_posts(page_id, access_token=page_token)
print("\n--- Publicaciones de la página ---")
print(json.dumps(posts_result, indent=2))

def get_post_comments(post_id, limit=25, access_token=None):
    """Obtiene los comentarios de una publicación específica de Facebook."""
    if access_token is None:
        access_token = user_access_token
        
    url = f"https://graph.facebook.com/v22.0/{post_id}/comments"
    params = {
        "access_token": access_token,
        "limit": limit,
        "fields": "id,message,created_time,attachment,comment_count,like_count,from{id,name,picture}"
    }
    response = requests.get(url, params=params)
    return response.json()


def get_user_profile(user_id, access_token=None):
    """Obtiene información del perfil de un usuario de Facebook."""
    if access_token is None:
        access_token = user_access_token
        
    url = f"https://graph.facebook.com/v22.0/{user_id}"
    params = {
        "access_token": access_token,
        "fields": "id,name,picture.type(large)"
    }
    response = requests.get(url, params=params)
    return response.json()

# Si hay publicaciones, obtener comentarios de la primera publicación
def get_comments_for_post(posts_result, access_token=None):
    if access_token is None:
        access_token = user_access_token
        
    if "data" in posts_result and len(posts_result["data"]) > 0:
        first_post = posts_result["data"][0]
        first_post_id = first_post["id"]
        
        print(f"\nObteniendo comentarios para la publicación con ID: {first_post_id}")
        print(f"Mensaje de la publicación: {first_post.get('message', 'Sin mensaje')}")
        
        comments = get_post_comments(first_post_id, access_token=access_token)
        print("\nComentarios de la publicación:")
        print(json.dumps(comments, indent=2))
        
        # Mostrar detalles de cada comentario de manera más legible
        if "data" in comments and len(comments["data"]) > 0:
            print("\nDetalle de comentarios:")
            for i, comment in enumerate(comments["data"], 1):
                print(f"--- Comentario #{i} ---")
                
                # Información del autor del comentario
                author = comment.get("from", {})
                author_name = author.get("name", "No disponible")
                author_id = author.get("id", "No disponible")
                
                print(f"Usuario: {author_name} (ID: {author_id})")
                print(f"Texto: {comment.get('message', 'No disponible')}")
                
                # Foto de perfil
                if "picture" in author and "data" in author["picture"] and "url" in author["picture"]["data"]:
                    profile_pic = author["picture"]["data"]["url"]
                    print(f"Foto de perfil: {profile_pic}")
                else:
                    print("Foto de perfil: No disponible directamente")
                    # Intentar obtener la foto de perfil del usuario
                    try:
                        user_info = get_user_profile(author_id, access_token=access_token)
                        if "picture" in user_info and "data" in user_info["picture"] and "url" in user_info["picture"]["data"]:
                            print(f"Foto de perfil (alt): {user_info['picture']['data']['url']}")
                    except Exception as e:
                        print(f"Error al obtener foto de perfil: {str(e)}")
                
                # Información adicional
                print(f"Fecha: {comment.get('created_time', 'No disponible')}")
                print(f"Likes: {comment.get('like_count', 0)}")
                
                # Si hay algún adjunto en el comentario
                if "attachment" in comment:
                    attach = comment["attachment"]
                    if "media" in attach and "image" in attach["media"]:
                        print(f"Imagen adjunta: {attach['media']['image']['src']}")
                    elif "url" in attach:
                        print(f"Adjunto URL: {attach['url']}")
                    else:
                        print("Tiene adjunto pero no se puede mostrar el detalle")
                
                print("")
        else:
            print("No hay comentarios en esta publicación")
    else:
        print("No se encontraron publicaciones para este usuario/página")


# Obtener y mostrar comentarios para la primera publicación usando el token de página
get_comments_for_post(posts_result, access_token=page_token)

# Si quieres obtener el token de larga duración, descomenta:
# long_lived_token = get_long_lived_token()
# print(f"Token de larga duración: {long_lived_token}")
