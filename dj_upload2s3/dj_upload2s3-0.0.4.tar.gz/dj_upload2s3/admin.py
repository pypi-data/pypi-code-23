from django.views.generic import TemplateView
from django.conf import settings

from dj_upload2s3.s3_signature import Signature


class Upload2S3AdminView(TemplateView):
    template_name = 'dj_upload2s3/admin_upload.html'
    app_verbose_name = 'Upload to S3'
    app_name = 'dj_upload2s3'
    credentials_options = {}

    def get_s3_credentials(self):
        s = Signature(settings.MEDIA_S3_ACCESS_KEY_ID,
                      settings.MEDIA_S3_ACCESS_KEY_SECRET,
                      settings.MEDIA_S3_BUCKET,
                      settings.MEDIA_S3_REGION, self.credentials_options)
        return s.get_s3_credentials()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        s3_credentials = self.get_s3_credentials()
        context['s3_credentials'] = s3_credentials
        context['app_verbose_name'] = self.app_verbose_name
        context['app_name'] = self.app_name
        return context
