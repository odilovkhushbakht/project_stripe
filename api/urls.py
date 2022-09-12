from django.urls import path, re_path

from api import views

urlpatterns = [
    path('buy/<int:pk>/', views.BuyView.as_view()),
    path('item/<int:id>/', views.ItemView.as_view()),
    path('order/', views.order_view),
    re_path(r'^order/(?P<id>\d+)/$', views.order_by_id_view),
    path('order/buy/<int:pk>/', views.OrderBuyView.as_view()),
    path('order/add/', views.order_add_view),
    path('order/delete/', views.order_delete_view),
    path('order/product/delete/', views.order_product_delete_view),
    path('success/', views.successView, name='success'),
    path('cancel/', views.cancelView, name='cancel')
]
