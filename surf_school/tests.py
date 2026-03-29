from django.test import TestCase
from django.contrib.auth.models import User
from .models import Alumno, Clase, Reserva
from datetime import date
from django.urls import reverse


class ReservaTestCase(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='test', password='1234')
        self.alumno = Alumno.objects.create(
            user=self.user,
            nombre='Test',
            edad=25,
            nivel='P',
            telefono='123',
            email_contacto='test@test.com'
        )

        self.clase = Clase.objects.create(
            fecha=date.today(),
            turno='1',
            cupo_maximo=5,
            nivel='P'
        )

    def test_crear_reserva(self):
        reserva = Reserva.objects.create(
            alumno=self.alumno,
            clase=self.clase
        )
        self.assertEqual(reserva.estado, 'P')

    def test_no_reserva_duplicada(self):
        Reserva.objects.create(alumno=self.alumno, clase=self.clase)

        with self.assertRaises(Exception):
            Reserva.objects.create(alumno=self.alumno, clase=self.clase)
            
            
class PermisosTestCase(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='user', password='1234')
        self.admin = User.objects.create_superuser(username='admin', password='1234')

    def test_usuario_no_admin_no_accede(self):
        self.client.login(username='user', password='1234')
        response = self.client.get(reverse('gestionar_reservas'))
        self.assertNotEqual(response.status_code, 200)

    def test_admin_accede(self):
        self.client.login(username='admin', password='1234')
        response = self.client.get(reverse('gestionar_reservas'))
        self.assertEqual(response.status_code, 200)