from django.conf.urls import url, include
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from . import views

app_name = 'parts'
urlpatterns = [

    url(r'^$', views.index, name='index'),
    url(r'^test/$', views.test, name='test'),
    url(r'^orders/$', views.orders, name='orders'),
    url(r'^orders/order-detail/(?P<id_order>[0-9]+)/$', views.order_detail, name='order_detail'),
    url(r'^part-detail/(?P<id_part>[0-9]+)$', views.part_detail, name='part_detail'),
    url(r'^part-detail/add-3mf/$', views.add_3mf, name='add_3mf'),
    url(r'^part-detail/add-cad2d/$', views.add_cad2d, name='add_cad2d'),
    url(r'^part-detail/add-stl/$', views.add_stl, name='add_stl'),
    url(r'^part-detail/add-bulk/$', views.add_bulk, name='add_bulk'),
    url(r'^part-detail/(?P<id_part>[0-9]+)/checkout-cad/(?P<id_cad>[0-9]+)$', views.checkout_cad, name='checkout_cad'),
    url(r'^part-detail/(?P<id_part>[0-9]+)/local$', views.checkout_part, name='checkout_part'),
    url(r'^part-detail/(?P<id_part>[0-9]+)/local1$', views.checkout_part1, name='checkout_part1'),
    url(r'^catalogue/$', views.index, name='catalogue'),
    url(r'^add-part/$', views.add_part, name='add_part'),
    url(r'^add-client/$', views.add_client, name='add_client'),
    url(r'^add-order/$', views.add_order, name='add_order'),
    url(r'^update-order/$', views.update_order, name='update_order'),
    url(r'^print-finished/$', views.print_finished, name='print_finished'),
    url(r'^prints/$', views.prints, name='prints'),
    url(r'^prints/download-log/(?P<id_print>[0-9]+)/$', views.download_log, name='download_log'),
    url(r'^ajax/print/$', views.ajax_print, name='ajax_print'),
    url(r'^ajax/update-notes/$', views.update_notes, name='update_notes'),
    url(r'^ajax/new-part-number/$', views.new_part_number, name='new_part_number'),
    url(r'^ajax/delete-image/$', views.delete_image, name='delete_image'),
    url(r'^ajax/delete-cad/$', views.delete_cad, name='delete_cad'),
    url(r'^ajax/delete-3mf/$', views.delete_3mf, name='delete_3mf'),
    url(r'^ajax/delete-cad2d/$', views.delete_cad2d, name='delete_cad2d'),
    url(r'^ajax/delete-stl/$', views.delete_stl, name='delete_stl'),
    url(r'^ajax/delete-bulk/$', views.delete_bulk, name='delete_bulk'),
    url(r'^ajax/delete-part/$', views.delete_part, name='delete_part'),
    url(r'^ajax/change-status-eng/$', views.change_status_eng, name='change_status_eng'),
    url(r'^part-detail/(?P<id_part>[0-9]+)/push-cad/$', views.push_cad, name='push_cad'),
    url(r'^part-detail/(?P<id_part>[0-9]+)/upload-image/$', views.upload_image, name='upload_image'),
    url(r'^part-detail/(?P<id_part>[0-9]+)/upload-cad/$', views.upload_cad_direct, name='upload_cad_direct'),
    # url(r'^part-detail/(?P<id_part>[0-9]+)/upload-amf/$', views.upload_amf_direct, name='upload_amf_direct'),
    # url(r'^part-detail/(?P<id_part>[0-9]+)/upload-config/$', views.upload_config_direct, name='upload_config_direct'),
    url(r'^part-detail/(?P<id_part>[0-9]+)/download_cad/(?P<id_cad>[0-9]+)/$', views.download_cad, name='download_cad'),
    url(r'^part-detail/(?P<id_part>[0-9]+)/download_bulk/(?P<id_bulk>[0-9]+)/$', views.download_bulk, name='download_bulk'),
    url(r'^part-detail/(?P<id_part>[0-9]+)/download_amf/(?P<id_3mf>[0-9]+)/$', views.download_amf, name='download_amf'),
    url(r'^part-detail/(?P<id_part>[0-9]+)/download_config/(?P<id_3mf>[0-9]+)/$', views.download_config, name='download_config'),
    url(r'^part-detail/(?P<id_part>[0-9]+)/download_configb/(?P<id_3mf>[0-9]+)/$', views.download_configb, name='download_configb'),
    url(r'^part-detail/(?P<id_part>[0-9]+)/download_gcode/(?P<id_3mf>[0-9]+)/$', views.download_gcode, name='download_gcode'),
    url(r'^part-detail/(?P<id_part>[0-9]+)/download_stl/(?P<id_stl>[0-9]+)/$', views.download_stl, name='download_stl'),
    url(r'^part-detail/(?P<id_part>[0-9]+)/download_cad2d/(?P<id_cad2d>[0-9]+)/$', views.download_cad2d, name='download_cad2d'),
    url(r'^(?P<id>[0-9]+)/slice_and_download/$', views.slice_and_download, name='slice_and_download'),

]


urlpatterns += staticfiles_urlpatterns()
