class Estudiante:
    """Entidad que representa a un estudiante o aspirante en el sistema."""
    def __init__(self, id_estudiante, cedula, nombres, apellidos, email=None, telefono=None, password=None):
        self.id_estudiante = id_estudiante
        self.cedula = cedula
        self.nombres = nombres
        self.apellidos = apellidos
        self.email = email
        self.telefono = telefono
        self.password = password

class Carrera:
    """Entidad que representa un programa académico ofertado."""
    def __init__(self, id_carrera, nombre, cupos, estado):
        self.id_carrera = id_carrera
        self.nombre = nombre
        self.cupos = cupos
        self.estado = estado

class Postulacion:
    """Representa la intención de ingreso de un estudiante a una carrera."""
    def __init__(self, id_postulacion, carrera_nombre, estado, fecha):
        self.id_postulacion = id_postulacion
        self.carrera_nombre = carrera_nombre
        self.estado = estado
        self.fecha = fecha