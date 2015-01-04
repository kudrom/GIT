from django.db import models

class Clientes(models.Model)
	id_cliente = models.AutoField(primary_key=True)
	nombre = models.CharField(max_length=45)
	primer_apellido = models.CharField(max_length=50)
	segundo_apellido = models.CharField(max_length=50)

class Inventario(models.Model)
	id_item = models.AutoField(primary_key=True)
	precio_compra = models.FloatField()
	fecha_compra = models.DateField()
	tipo = models.CharField(max_length=8)
	caracteristicas = models.CharField(max_length=200)

class Empleados(models.Model)
	id_empleado = models.AutoField(primary_key=True)
	nombre = models.CharField(max_length=45)
	primer_apellido = models.CharField(max_length=50)
	segundo_apellido = models.CharField(max_length=50)
	puesto = models.CharField(max_length=12)

class Comentarios(models.Model)
	id_comentario = models.AutoField(primary_key=True)
	texto = models.CharField(max_length=200)
	id_empleado = models.ForeignKey(Empleados)

class Notificaciones(models.Model)
	id_notificacion = models.AutoField(primary_key=True)
	texto = models.CharField(max_length=100)
	id_empleado = models.ForeignKey(Empleados)

class Incidencias(models.Model):
	id_incidencia = models.AutoField(primary_key=True)
	nombre_incidencia = models.CharField(max_length=100)
	estado = models.CharField(max_length=22)
	fecha_apertura = models.DateField()
	fecha_cierre = models.DateField()
	descripcion = models.CharField(max_length=300)
	prioridad = models.IntegerField()
	categoria = models.CharField(max_length=80)
	resolucion = models.CharField(max_length=2)
	id_cliente = models.ForeignKey(Clientes)
	id_comentario = models.ForeignKey(Comentarios)
	id_item = models.ForeignKey(Inventario)
	id_empleado = models.ForeignKey(Empleados)
	id_notificacion = models.ForeignKey(Notificaciones)

