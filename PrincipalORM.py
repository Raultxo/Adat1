import mysql.connector as cn
import sqlite3
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.orm import sessionmaker

engineSQLite = create_engine('sqlite:///olimpiadas.db')
engineMySQL = create_engine('mysql+pymysql://admin:password@127.0.0.1/olimpiadas')

Base = declarative_base()


class Olimpiada(Base):  # Tabla Olimpiada
    __tablename__ = 'Olimpiada'

    id_olimpiada = Column(Integer, primary_key=True)
    nombre = Column(String)
    anio = Column(Integer)
    temporada = Column(String)
    ciudad = Column(String)


class Deporte(Base):  # Tabla Deporte
    __tablename__ = 'Deporte'

    id_deporte = Column(Integer, primary_key=True)
    nombre = Column(String)


class Deportista(Base):  # Tabla Deportista
    __tablename__ = 'Deportista'

    id_deportista = Column(Integer, primary_key=True)
    nombre = Column(String)
    sexo = Column(String)
    peso = Column(Integer)
    altura = Column(Integer)


class Equipo(Base):  # Tabla Equipo
    __tablename__ = 'Equipo'

    id_equipo = Column(Integer, primary_key=True)
    nombre = Column(String)
    iniciales = Column(String)


class Evento(Base):  # Tabla Evento
    __tablename__ = 'Evento'

    id_evento = Column(Integer, primary_key=True)
    nombre = Column(String)
    id_olimpiada = Column(Integer, ForeignKey('Olimpiada.id_olimpiada'))
    id_deporte = Column(Integer, ForeignKey('Deporte.id_deporte'))
    olimpiada = relationship("Olimpiada", back_populates="eventos")
    deporte = relationship("Deporte", back_populates="eventos")


class Participacion(Base):  # Tabla Participacion
    __tablename__ = 'Participacion'

    id_deportista = Column(Integer, ForeignKey('Deportista.id_deportista'), primary_key=True)
    id_evento = Column(Integer, ForeignKey('Evento.id_evento'), primary_key=True)
    id_equipo = Column(Integer, ForeignKey('Equipo.id_equipo'))
    edad = Column(Integer)
    medalla = Column(String)
    deportista = relationship("Deportista", back_populates="participaciones")
    evento = relationship("Evento", back_populates="participaciones")
    equipo = relationship("Equipo", back_populates="participaciones")


# Relaciones
Olimpiada.eventos = relationship("Evento", order_by=Evento.id_evento, back_populates="olimpiada")
Deporte.eventos = relationship("Evento", order_by=Evento.id_evento, back_populates="deporte")
Deportista.participaciones = relationship("Participacion", order_by=Participacion.id_deportista,
                                          back_populates="deportista")
Evento.participaciones = relationship("Participacion", order_by=Participacion.id_evento, back_populates="evento")
Equipo.participaciones = relationship("Participacion", order_by=Participacion.id_equipo, back_populates="equipo")

Base.metadata.create_all(engineSQLite)
Base.metadata.create_all(engineMySQL)


# Metodo que muestra el menu
def cargarMenu():
    print("""
¿Que quieres hacer?
1. Listado de deportistas participantes
2. Modificar medalla de deportista
3. Añadir deportista o participacion
4. Eliminar participación
0. Salir
        """)
    return int(input())


def listadoDeportistas():
    # Elegimos la BBDD en la que hacer la consulta
    bbdd = input("En que base de datos quieres buscar? (MySQL/SQLite): ").lower()
    while bbdd != "mysql" and bbdd != "sqlite":
        bbdd = input("En que base de datos quieres buscar? (MySQL/SQLite): ").lower()

    if bbdd == "mysql":
        Session = sessionmaker(bind=engineMySQL)
    else:
        Session = sessionmaker(bind=engineSQLite)

    session = Session()
    # Pedimos la temporada
    temporada = input("Temporada? (W - Winter/S - Summer): ").lower()
    while temporada != "w" and temporada != "s":
        temporada = input("Temporada? (W - Winter/S - Summer): ").lower()

    if temporada == "s":
        temporada = "Summer"
    else:
        temporada = "Winter"

    # Mostramos las olimpiadas
    result = session.query(Olimpiada).filter(Olimpiada.temporada == temporada)
    listaIDs = {}
    for row in result:
        print(row.id_olimpiada, "\t", row.anio, "\t", row.ciudad)
        listaIDs[row.id_olimpiada] = row.eventos

    # Pedimos la olimpiada
    idOlimpiada = int(input("Introduce el numero de la olimpiada: "))
    while idOlimpiada not in listaIDs:
        idOlimpiada = int(input("Introduce el numero de la olimpiada: "))

    # Mostramos los deportes
    listaDeportes = []
    for evento in listaIDs[idOlimpiada]:
        if evento.deporte.id_deporte not in listaDeportes:
            print(evento.deporte.id_deporte, "\t", evento.deporte.nombre)
            listaDeportes.append(evento.deporte.id_deporte)

    # Pedimos el deporte
    idDeporte = int(input("Introduce el numero del deporte: "))
    while idDeporte not in listaDeportes:
        idDeporte = int(input("Introduce el numero del deporte: "))

    # Mostramos los eventos
    listaEventos = {}
    for evento in listaIDs[idOlimpiada]:
        if evento.id_deporte == idDeporte:
            listaEventos[evento.id_evento] = evento.participaciones
            print(evento.id_evento, "\t", evento.nombre)

    # Pedimos el evento
    idEvento = int(input("Introduce el numero del evento: "))
    while idEvento not in listaEventos:
        idEvento = int(input("Introduce el numero del evento: "))

    # Listamos los deportistas
    for participacion in listaEventos[idEvento]:
        part = ""
        part += participacion.deportista.nombre + "\t"
        if participacion.deportista.altura is not None:
            part = part + str(participacion.deportista.altura) + "cm\t"
        if participacion.deportista.peso is not None:
            part = part + str(participacion.deportista.peso) + "kg\t"
        if participacion.edad is not None:
            part = part + str(participacion.edad) + " años\t"
        part += participacion.equipo.nombre
        if participacion.medalla is None:
            part = part + " sin medalla"
        else:
            part = part + " " + participacion.medalla
        print(part)

    session.close()


# Metodo para modificar la medalla de una participacion
def modificarMedalla():

    # Pedimos un deportista
    deportista = input("Que deportista quieres buscar: ")

    # Creamos la conexion
    Session = sessionmaker(bind=engineSQLite)
    session = Session()
    result = session.query(Deportista).filter(Deportista.nombre.ilike("%" + deportista + "%"))

    # Mostramos los deportistas que coincidan con lo introducido
    listaDeportistas = {}
    for row in result:
        listaDeportistas[row.id_deportista] = row.participaciones
        print(row.id_deportista, "\t", row.nombre)

    if len(listaDeportistas) > 0:
        # Pedimos que seleccione el deportista
        idDeportista = int(input("Selecciona el numero del deportista: "))
        while idDeportista not in listaDeportistas:
            idDeportista = int(input("Selecciona el numero del deportista: "))

        # Mostramos las participaciones de ese deportista
        listaParticipacion = []
        medalla = None
        for participacion in listaDeportistas[idDeportista]:
            stri = str(participacion.id_deportista) + "_" + str(participacion.id_evento)
            listaParticipacion.append(stri)
            stri = stri + " " + session.query(Evento).get(participacion.id_evento).nombre
            if participacion.medalla is None:
                stri = stri + " sin medalla"
            else:
                stri = stri + " " + participacion.medalla
            print(stri)
            medalla = participacion.medalla
        # Pedimos que seleccione la participacion
        idParticipacion = input("Selecciona el numero de la participacion: ")
        while idParticipacion not in listaParticipacion:
            idParticipacion = input("Selecciona el numero de la participacion: ")

        if medalla is None:
            print("Esa participacion no tiene medalla")
        else:
            print("La medalla es: " + medalla)

        # Pedimos que introduzca la nueva medalla
        nuevaMedalla = input("Inserta la nueva medalla: (Bronze, Silver, Gold, NA): ").capitalize()
        while nuevaMedalla != "Bronze" and nuevaMedalla != "Silver" and nuevaMedalla != "Gold" and nuevaMedalla != "Na":
            nuevaMedalla = input("Inserta la nueva medalla (Bronze, Silver, Gold, Na): ").capitalize()

        idDeportista, idEvento = idParticipacion.split("_")

        # Ejecutamos la consulta en SQLite
        if nuevaMedalla == "Na":
            session.query(Participacion).get((idDeportista, idEvento)).medalla = None
        else:
            session.query(Participacion).get((idDeportista, idEvento)).medalla = nuevaMedalla
        session.commit()
        session.close()

        # Ejecutamos la consulta en MYSQL
        Session = sessionmaker(bind=engineMySQL)
        session = Session()
        if nuevaMedalla == "Na":
            session.query(Participacion).get((idDeportista, idEvento)).medalla = None
        else:
            session.query(Participacion).get((idDeportista, idEvento)).medalla = nuevaMedalla
        session.commit()
        session.close()
    else:
        print("No existe ese deportista")
        session.close()


# Metodo para añadir un deportista y una participacion
def aniadirParticipacion():
    # Creamos las sesiones
    Session1 = sessionmaker(bind=engineSQLite)
    session1 = Session1()

    Session2 = sessionmaker(bind=engineMySQL)
    session2 = Session2()

    # Pedimos un deportista
    deportista = input("Que deportista quieres buscar: ")
    result = session1.query(Deportista).filter(Deportista.nombre.ilike("%" + deportista + "%"))

    # Mostramos los deportistas
    listaDeportsitas = []
    for row in result:
        listaDeportsitas.append(row.id_deportista)
        print(row.id_deportista, "\t", row.nombre)

    # Si el deportista no existe, pedimos si quiere crearlo
    if len(listaDeportsitas) == 0:
        respuesta = input("Ese deportista no existe, crearlo? (Si/No)").capitalize()
        while respuesta != "Si" and respuesta != "No":
            respuesta = input("Ese deportista no existe, crearlo? (Si/No)").capitalize()
        if respuesta == "Si":
            # Si quiere crearlo, pedimos los datos y lo insertamos en las 2 BBDD
            sexo = input("Sexo del deportista (M/F): ").upper()
            while sexo != "M" and sexo != "F":
                sexo = input("Sexo del deportista (M/F): ").upper()
            peso = int(input("Peso del deportista (0 si se desconoce): "))
            altura = int(input("Altura del deportista (0 si se desconoce): "))
            if peso == 0:
                peso = None
            if altura == 0:
                altura = None

            # Añadimos el deportista a las 2 BBDD
            nuevoDeportista = Deportista(nombre=deportista, sexo=sexo, peso=peso, altura=altura)
            session1.add(nuevoDeportista)
            session1.commit()

            session2.add(nuevoDeportista)
            session2.commit()

            # Como id, seleccionamos el del ultimo deportista añadido
            idDeportista = nuevoDeportista.id_deportista
        else:
            return
    else:
        # Si existen deportistas, pedimos que seleccione uno
        idDeportista = int(input("Selecciona el numero del deportista: "))
        while idDeportista not in listaDeportsitas:
            idDeportista = int(input("Selecciona el numero del deportista: "))

    # Pedimos la temporada
    temporada = input("Temporada? (W - Winter/S - Summer): ").lower()
    while temporada != "w" and temporada != "s":
        input("Temporada? (W - Winter/S - Summer): ").lower()

    if temporada == "s":
        temporada = "Summer"
    else:
        temporada = "Winter"

    # Mostramos las olimpiadas
    result = session1.query(Olimpiada).filter(Olimpiada.temporada == temporada)
    listaIDs = {}
    for row in result:
        print(row.id_olimpiada, "\t", row.anio, "\t", row.ciudad)
        listaIDs[row.id_olimpiada] = row.eventos

    # Pedimos que seleccione la olimpiada
    idOlimpiada = int(input("Introduce el numero de la olimpiada: "))
    while idOlimpiada not in listaIDs:
        idOlimpiada = int(input("Introduce el numero de la olimpiada: "))

    # Mostrar los deportes
    listaDeportes = []
    for evento in listaIDs[idOlimpiada]:
        if evento.deporte.id_deporte not in listaDeportes:
            print(evento.deporte.id_deporte, "\t", evento.deporte.nombre)
            listaDeportes.append(evento.deporte.id_deporte)

    # Pedimos el deporte
    idDeporte = int(input("Introduce el numero del deporte: "))
    while idDeporte not in listaDeportes:
        idDeporte = int(input("Introduce el numero del deporte: "))

    # Mostramos los eventos
    listaEventos = {}
    for evento in listaIDs[idOlimpiada]:
        if evento.id_deporte == idDeporte:
            listaEventos[evento.id_evento] = evento.participaciones
            print(evento.id_evento, "\t", evento.nombre)

    # Pedimos el evento
    idEvento = int(input("Introduce el numero del evento: "))
    while idEvento not in listaEventos:
        idEvento = int(input("Introduce el numero del evento: "))

    # Mostramos los equipos
    listaEquipos = []
    result = session1.query(Equipo).all()
    for row in result:
        listaEquipos.append(row.id_equipo)
        print(row.id_equipo, "\t", row.nombre, "\t", row.iniciales)

    # Pedimos que seleccione el equipo
    idEquipo = int(input("Introduce el numero del equipo: "))
    while idEquipo not in listaEquipos:
        idEquipo = int(input("Introduce el numero del equipo: "))

    # Ejecutamos la consulta en SQLite
    nuevaParticipacion = Participacion(id_deportista=idDeportista, id_evento=idEvento, id_equipo=idEquipo, edad=None,
                                       medalla=None)
    session1.add(nuevaParticipacion)
    session1.commit()
    session1.close()

    # Ejecutamos la consulta en MYSQL
    session2.add(nuevaParticipacion)
    session2.commit()
    session2.close()


# Metodo que elimina una participacion y que si el deportista se queda sin participaciones, se elimina
def eliminarDeportista():
    # Creamos las sesiones
    Session1 = sessionmaker(bind=engineSQLite)
    session1 = Session1()

    Session2 = sessionmaker(bind=engineMySQL)
    session2 = Session2()

    # Pedimos un deportista
    deportista = input("Que deportista quieres buscar: ")
    result = session1.query(Deportista).filter(Deportista.nombre.ilike("%" + deportista + "%"))

    # Mostramos los deportistas que coincidan con lo introducido
    listaDeportistas = {}
    for row in result:
        listaDeportistas[row.id_deportista] = row.participaciones
        print(row.id_deportista, "\t", row.nombre)

    if len(listaDeportistas) > 0:
        # Pedimos que seleccione el deportista
        idDeportista = int(input("Selecciona el numero del deportista: "))
        while idDeportista not in listaDeportistas:
            idDeportista = int(input("Selecciona el numero del deportista: "))

        # Mostramos las participaciones de ese deportista
        listaParticipacion = []
        for participacion in listaDeportistas[idDeportista]:
            stri = str(participacion.id_deportista) + "_" + str(participacion.id_evento)
            listaParticipacion.append(stri)
            stri = stri + " " + session1.query(Evento).get(participacion.id_evento).nombre
            if participacion.medalla is None:
                stri = stri + " sin medalla"
            else:
                stri = stri + " " + participacion.medalla
            print(stri)

        # Pedimos que seleccione la participacion
        idParticipacion = input("Selecciona el numero de la participacion: ")
        while idParticipacion not in listaParticipacion:
            idParticipacion = input("Selecciona el numero de la participacion: ")

        idDeportista, idEvento = idParticipacion.split("_")

        # Borramos la participacion
        session1.query(Participacion).filter(Participacion.id_deportista == idDeportista,
                                             Participacion.id_evento == idEvento).delete()
        session1.commit()

        session2.query(Participacion).filter(Participacion.id_deportista == idDeportista,
                                             Participacion.id_evento == idEvento).delete()
        session2.commit()

        # Si el count devuelve 0, elimina el deportista
        result = session1.query(Participacion.id_deportista).filter(Participacion.id_deportista == idDeportista).count()
        if result == 0:
            session1.query(Deportista).filter(Deportista.id_deportista == idDeportista).delete()
            session1.commit()

        # Lo separo en 2 porque mi base de datos de MySQL y SQLite no estan igual y me daba excepciones
        result = session2.query(Participacion.id_deportista).filter(Participacion.id_deportista == idDeportista).count()
        if result == 0:
            session2.query(Deportista).filter(Deportista.id_deportista == idDeportista).delete()
            session2.commit()
    else:
        print("No existe ese deportista")


# El programa principal, que va pidiendo una opcion
resp = cargarMenu()
while resp != 0:
    print()
    if resp == 1:
        listadoDeportistas()
    elif resp == 2:
        modificarMedalla()
    elif resp == 3:
        aniadirParticipacion()
    elif resp == 4:
        eliminarDeportista()
    else:
        print("No existe esa opcion")
    resp = cargarMenu()
exit("Adios")
