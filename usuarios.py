import requests
import json
import os
import getpass
import re
import glpi_api

#Conexión con la base de datos de odoo
odoo_url = "http://odoo.iesfernandoasir.net"
odoo_db = "bd_odoo"
odoo_usuario = "admin"
odoo_contraseña = "admin"

nuevo_usuario = {
    "nombre": input("Introduce el nombre del usuario: "),
    "login": input("Introduce el login del usuario: "),
    "email": input("Introduce el email del usuario: "),
    "contraseña": input("Introduce la contraseña del usuario: ")
}

#Creamos el usuario primero en el sistema para ello haremos uso de la libreria os

contraseña_linux = getpass.getpass(prompt="Introduce la contraseña del usuario de Linux: ")
nuevo_usuario["contraseña_linux"] = contraseña_linux

# Crear el usuario primero en el sistema
adduser_command = f"sudo adduser --disabled-password --gecos '' {nuevo_usuario['login']}"
os.system(adduser_command)

# Establecer la contraseña del nuevo usuario de Linux
os.system(f"echo '{nuevo_usuario['login']}:{nuevo_usuario['contraseña_linux']}' | sudo chpasswd")

nombre_grupo = input("Introduce el nombre del grupo al que quieres añadir el usuario: ")

def crear_usuario_odoo():
    try:
        # Nos autenticamos en Odoo
        url_autenticacion = f"{odoo_url}/web/session/authenticate"
        payload_autenticacion = {
            "jsonrpc": "2.0",
            "method": "call",
            "params": {
                "db": odoo_db,
                "login": odoo_usuario,
                "password": odoo_contraseña
            }
        }
        headers_autenticacion = {
            "Content-Type": "application/json"
        }
        respuesta_autenticacion = requests.post(url_autenticacion, json=payload_autenticacion, headers=headers_autenticacion)
        
        datos_autenticacion = respuesta_autenticacion.json()
        if 'error' in datos_autenticacion:
            print("Error en la autenticación de Odoo:", datos_autenticacion['error']['data']['message'])
            return
        
        session_id = respuesta_autenticacion.cookies.get('session_id')
        if not session_id:
            print("No se pudo obtener el ID de sesión.")
            return

        # Creamos el usuario en odoo
        url_creacion = f"{odoo_url}/web/dataset/call_kw"
        headers_creacion = {
            "Content-Type": "application/json",
            "Cookie": f"session_id={session_id}"
        }
        payload_creacion = {
            "jsonrpc": "2.0",
            "method": "call",
            "params": {
                "model": "res.users",
                "method": "create",
                "args": [{
                    "name": nuevo_usuario["nombre"],
                    "login": nuevo_usuario["login"],
                    "email": nuevo_usuario["email"],
                    "password": nuevo_usuario["contraseña"]
                }],
                "kwargs": {}
            }
        }
        respuesta_creacion = requests.post(url_creacion, headers=headers_creacion, json=payload_creacion)
        
        datos_creacion = respuesta_creacion.json()
        if datos_creacion.get("error"):
            print("Error al crear usuario en Odoo:", datos_creacion["error"]["data"]["message"])
            return
        
        usuario_id = datos_creacion["result"]
        print("Usuario creado en Odoo con ID:", usuario_id)
        
        # Obtener el ID del grupo
        payload_busqueda_grupo = {
            "jsonrpc": "2.0",
            "method": "call",
            "params": {
                "model": "res.groups",
                "method": "search_read",
                "args": [[["name", "=", nombre_grupo]]],
                "kwargs": {
                    "fields": ["id", "name", "category_id"]
                }
            }
        }
        respuesta_busqueda_grupo = requests.post(url_creacion, headers=headers_creacion, json=payload_busqueda_grupo)
        
        datos_busqueda_grupo = respuesta_busqueda_grupo.json()
        if datos_busqueda_grupo.get("error") or not datos_busqueda_grupo["result"]:
            print("Error al buscar grupo en Odoo o grupo no encontrado:", datos_busqueda_grupo.get("error", "Grupo no encontrado"))
            return
        
        grupo = datos_busqueda_grupo["result"][0]
        grupo_id = grupo["id"]
        categoria_grupo_id = grupo["category_id"][0]
        print("ID del grupo encontrado:", grupo_id)
        
        # Obtener grupos actuales del usuario
        payload_leer_grupos = {
            "jsonrpc": "2.0",
            "method": "call",
            "params": {
                "model": "res.users",
                "method": "read",
                "args": [[usuario_id], ["groups_id"]],
                "kwargs": {}
            }
        }
        respuesta_leer_grupos = requests.post(url_creacion, headers=headers_creacion, json=payload_leer_grupos)
        
        datos_leer_grupos = respuesta_leer_grupos.json()
        if datos_leer_grupos.get("error"):
            print("Error al leer grupos del usuario en Odoo:", datos_leer_grupos["error"]["data"]["message"])
            return
        
        grupos_actuales = datos_leer_grupos["result"][0]["groups_id"]
        
        ids_grupos_actuales = ','.join(map(str, grupos_actuales))
        payload_leer_categorias = {
            "jsonrpc": "2.0",
            "method": "call",
            "params": {
                "model": "res.groups",
                "method": "search_read",
                "args": [[["id", "in", ids_grupos_actuales.split(",")]]],
                "kwargs": {
                    "fields": ["id", "name", "category_id"]
                }
            }
        }
        respuesta_leer_categorias = requests.post(url_creacion, headers=headers_creacion, json=payload_leer_categorias)
        
        datos_leer_categorias = respuesta_leer_categorias.json()
        if datos_leer_categorias.get("error"):
            print("Error al leer categorías de grupos actuales del usuario en Odoo:", datos_leer_categorias["error"]["data"]["message"])
            return
        
        categorias_actuales = [grupo["category_id"][0] for grupo in datos_leer_categorias["result"] if grupo["category_id"]]
        
        # Eliminar el usuario de los grupos de la misma categoría para poder añadirlos al grupo que eligamos
        grupos_conflictivos = [grupo["id"] for grupo in datos_leer_categorias["result"] if grupo["category_id"] and grupo["category_id"][0] == categoria_grupo_id]
        if grupos_conflictivos:
            payload_eliminar_grupos = {
                "jsonrpc": "2.0",
                "method": "call",
                "params": {
                    "model": "res.users",
                    "method": "write",
                    "args": [[usuario_id], {
                        "groups_id": [(3, grupo_id) for grupo_id in grupos_conflictivos]
                    }],
                    "kwargs": {}
                }
            }
            respuesta_eliminar_grupos = requests.post(url_creacion, headers=headers_creacion, json=payload_eliminar_grupos)
            datos_eliminar_grupos = respuesta_eliminar_grupos.json()
            if datos_eliminar_grupos.get("error"):
                print("Error al eliminar usuario de los grupos conflictivos en Odoo:", datos_eliminar_grupos["error"]["data"]["message"])
                return
            print(f"Usuario eliminado de los grupos conflictivos: {grupos_conflictivos}")

        # Añadir el usuario al grupo si no está ya en el grupo
        if grupo_id not in grupos_actuales:
            payload_añadir_grupo = {
                "jsonrpc": "2.0",
                "method": "call",
                "params": {
                    "model": "res.users",
                    "method": "write",
                    "args": [[usuario_id], {
                        "groups_id": [(4, grupo_id)]
                    }],
                    "kwargs": {}
                }
            }
            respuesta_añadir_grupo = requests.post(url_creacion, headers=headers_creacion, json=payload_añadir_grupo)
            
            datos_añadir_grupo = respuesta_añadir_grupo.json()
            if datos_añadir_grupo.get("error"):
                print("Error al añadir usuario al grupo en Odoo:", datos_añadir_grupo["error"]["data"]["message"])
            else:
                print("Usuario añadido al grupo con éxito.")
        else:
            print("El usuario ya pertenece al grupo especificado.")
    
    except requests.exceptions.RequestException as e:
        print("Error de conexión con Odoo:", e)
    except ValueError as e:
        print("Error al procesar la respuesta de Odoo:", e)

#GLPI creación de usuarios

# Solicitar información de configuración al usuario , API de la aplicación y del usuario.
url_glpi = "http://localhost/apirest.php/"
user_token = "IKsSmGP5gW1p0cA55pGP4hz165c4vjolqQzsargQ"
app_token = "QHbvfxu7eD1O5MRyxxVhztRyDkJTuD1m8YfDxY8o"

# Cabeceras para la autenticación
cabeceras = {
    'Content-Type': 'application/json',
    'Authorization': f'user_token {user_token}',
    'App-Token': app_token
}

# Función para obtener un token de sesión
def obtener_token_sesion():
    print("Intentando obtener token de sesión...")
    respuesta = requests.get(f'{url_glpi}/initSession', headers=cabeceras)
    print(f"Respuesta de la API: {respuesta.status_code}, {respuesta.text}")
    if respuesta.status_code == 200:
        return respuesta.json()['session_token']
    else:
        print(f"Error al iniciar sesión: {respuesta.status_code}")
        return None

def obtener_id_perfil(token_sesion, nombre_perfil):
    cabeceras_sesion = cabeceras.copy()
    cabeceras_sesion['Session-Token'] = token_sesion

    respuesta = requests.get(f'{url_glpi}/search/Profile', headers=cabeceras_sesion, params={
        'criteria[0][field]': 1,
        'criteria[0][searchtype]': 'contains',
        'criteria[0][value]': nombre_perfil,
        'forcedisplay[0]': 'id'
    })
    print(f"Respuesta de la API al buscar perfil: {respuesta.status_code}, {respuesta.text}")
    if respuesta.status_code == 200:
        datos_respuesta = respuesta.json()
        print(f"Datos de respuesta: {datos_respuesta}")
        if datos_respuesta['count'] > 0 and 'data' in datos_respuesta and len(datos_respuesta['data']) > 0:
            print("Estructura de los datos devueltos:", datos_respuesta['data'][0])
            for key, value in datos_respuesta['data'][0].items():
                if value == nombre_perfil:
                    return int(key)
            print(f"Error: la clave 'id' no se encuentra en la respuesta.")
            return None
        else:
            print(f"No se encontró el perfil con el nombre: {nombre_perfil}")
            return None
    else:
        print(f"Error al obtener el ID del perfil: {respuesta.status_code} - {respuesta.text}")
        return None

# Función para crear un usuario en GLPI
def crear_usuario(token_sesion, datos_usuario):
    cabeceras_sesion = cabeceras.copy()
    cabeceras_sesion['Session-Token'] = token_sesion

    respuesta = requests.post(f'{url_glpi}/User', headers=cabeceras_sesion, data=json.dumps(datos_usuario))
    if respuesta.status_code == 201:
        print("Usuario creado exitosamente:", respuesta.json())
        return respuesta.json()['id']
    else:
        print(f"Error al crear usuario: {respuesta.status_code} - {respuesta.text}")
        return None

# Solicitar información del usuario a crear
nombre_usuario = input("Introduce el nombre de usuario de la cuenta de GLPI: ")
nombre_real = input("Introduce el apellido del usuario de la cuenta de GLPI: ")
primer_nombre = input("Introduce el primer nombre del usuario de la cuenta de GLPI: ")
email = input("Introduce el correo electrónico del usuario de la cuenta de GLPI: ")
telefono = input("Introduce el teléfono del usuario de la cuenta de GLPI : ")
movil = input("Introduce el móvil del usuario de la cuenta de GLPI: ")
nombre_perfil = input("Introduce el nombre del perfil al que quieres agregar el usuario: ")
titulo_id = int(input("Introduce el ID del título del usuario en GLPI: "))

token_sesion = obtener_token_sesion()

if token_sesion:
    id_perfil = obtener_id_perfil(token_sesion, nombre_perfil)
    if id_perfil:
        # Datos del usuario a crear
        datos_usuario = {
            "input": {
                "name": nombre_usuario,
                "realname": nombre_real,
                "firstname": primer_nombre,
                "email": email,
                "phone": telefono,
                "mobile": movil,
                "usertitles_id": titulo_id,
                "profiles_id": id_perfil
            }
        }

        id_usuario = crear_usuario(token_sesion, datos_usuario)

    requests.get(f'{url_glpi}/killSession', headers=cabeceras)
else:
    print("No se pudo obtener el token de sesión.")
crear_usuario_odoo()
