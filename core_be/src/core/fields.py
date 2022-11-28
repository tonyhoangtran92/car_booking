from django.conf import settings
from versatileimagefield.fields import VersatileImageField
from versatileimagefield.files import VersatileImageFieldFile

from .storage import CustomS3Boto3Storage_2

# from .storage import CustomS3Boto3Storage_2


class DynamicStorageFieldFile(VersatileImageFieldFile):
    def __init__(self, instance, field, name):
        super(DynamicStorageFieldFile, self).__init__(
            instance, field, name
        )
        storage = CustomS3Boto3Storage_2()
        self.storage = storage


class DynamicStorageFileField(VersatileImageField):
    attr_class = DynamicStorageFieldFile

    def pre_save(self, model_instance, add):
        storage = CustomS3Boto3Storage_2()
        self.storage = storage
        file = super(DynamicStorageFileField, self
                     ).pre_save(model_instance, add)
        return file
