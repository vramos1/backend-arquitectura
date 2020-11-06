## Entrega 1 - Grupo 7

### Consideraciones
- El backend utiliza el header "instance_id"
- Se implementa un elastic loadBalancer
- Se implementa ssl para los dominios de backend y frontend respectivamente
- Se implementan los mensajes en tiempo real por medio de websockets
- Por un error en la librería de cords en django, es necesario habilitar la extensión Cors para acceder a todas las funcionalidades (Agregar Sala de chat)
- Tanto backend como frontend se encuentran en docker
- Se cuenta con Django admin en la api
- Se implementa un auto skaling group
- Se desarrolla el frontend en ReactJs, haciendo llamadas a endpoints HTTP del backend (Django)


### Dominios
Frontend: frontend.vicho-arquitectura.tk
API: vicho-arquitectura.tk

### Metodo de entrada
Dado que el autoscaling cambia contantemente las instancias, se deja el codigo general para entrada, usando el archivo pem

ssh -i path/to/pem ec2-user@dns-ec2
