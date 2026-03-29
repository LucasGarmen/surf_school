from rest_framework.routers import DefaultRouter
from django.contrib.auth import views as auth_views
from .views import (
    AlumnoViewSet,
    ClaseViewSet,
    ReservaViewSet,
    mis_reservas,
    clases_view,
    login_view,
    logout_view,
    reservar_clase,
    register_view,
    crear_clase_view,
    editar_clase_view,
    eliminar_clase_view,
    gestionar_reservas_view,
    cambiar_estado_reserva_view,
    cancelar_reserva_view,
    solicitar_cancelacion_view,
    gestionar_solicitudes_cancelacion_view,
    responder_solicitud_cancelacion_view,
    instrucciones_pago_view,
    editar_perfil_view,
    cambiar_password_view,
)
from django.urls import path

router = DefaultRouter()#genera rutas automaticamente para los viewset(solo API)
router.register(r'api/alumnos', AlumnoViewSet)
router.register(r'api/clases', ClaseViewSet)
router.register(r'api/reservas', ReservaViewSet)

urlpatterns = [
    path('login/', login_view, name='login'),
    path('register/', register_view, name='register'),
    path('clases/', clases_view, name='clases'),
    path('clases/crear/', crear_clase_view, name='crear_clase'),
    path('clases/editar/<int:clase_id>/', editar_clase_view, name='editar_clase'),
    path('mis-reservas/', mis_reservas, name='mis_reservas'),
    path('reservar/<int:clase_id>/', reservar_clase, name='reservar_clase'),
    path('reservas/gestionar/', gestionar_reservas_view, name='gestionar_reservas'),
    path('reservas/<int:reserva_id>/estado/<str:nuevo_estado>/', cambiar_estado_reserva_view, name='cambiar_estado_reserva'),
    path('logout/', logout_view, name='logout'),
    path('clases/eliminar/<int:clase_id>/', eliminar_clase_view, name='eliminar_clase'),
    path('reservas/cancelar/<int:reserva_id>/', cancelar_reserva_view, name='cancelar_reserva'),
    path('reservas/solicitar-cancelacion/<int:reserva_id>/', solicitar_cancelacion_view, name='solicitar_cancelacion'),
    path('solicitudes-cancelacion/', gestionar_solicitudes_cancelacion_view, name='gestionar_solicitudes_cancelacion'),
    path('solicitudes-cancelacion/<int:solicitud_id>/<str:accion>/', responder_solicitud_cancelacion_view, name='responder_solicitud_cancelacion'),
    path('reservas/<int:reserva_id>/pago/', instrucciones_pago_view, name='instrucciones_pago'),
    path('perfil/editar/', editar_perfil_view, name='editar_perfil'),
    path('perfil/cambiar-password/', cambiar_password_view, name='cambiar_password'),
    path('password-reset/',auth_views.PasswordResetView.as_view(template_name='password_reset_form.html'),
        name='password_reset'),
    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='password_reset_done.html'),
        name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='password_reset_confirm.html'),
        name='password_reset_confirm'),
    path('reset/done/',auth_views.PasswordResetCompleteView.as_view(template_name='password_reset_complete.html'),
        name='password_reset_complete'),
]

urlpatterns += router.urls#agrega las rutas creadas con DefaultRouter a urlpatterns