from django.contrib import admin
from django.core.exceptions import ValidationError
from django.utils.safestring import mark_safe
from .models import *
from django.forms import ModelChoiceField, ModelForm
from PIL import Image


class NotebookAdminForm(ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['image'].help_text = mark_safe(
            '<span style="color:red;font-size:15px;">Upload image with minimum resolution{}x{}</span>'.format(
                *Product.MIN_RESOLUTION
            )
        )

    def clean_image(self):
        image = self.cleaned_data['image']
        img = Image.open(image)
        min_height, min_width = Product.MIN_RESOLUTION
        max_height, max_width = Product.MAX_RESOLUTION
        if image.size > Product.MAX_IMAGE_SIZE:
            raise ValidationError("Image size must not exceed 3 MB")
        if img.height < min_height or img.width < min_width:
            raise ValidationError("Image resolution less than minimum resolution!")
        if img.height > max_height or img.width > max_width:
            raise ValidationError("Image resolution more than maximum resolution!")
        return image


# Метод formfield_for_foreignkey позволяет вам переопределить поле для внешнего ключа.
# Например, изменить выбор объектов в зависимости от пользователя:
class NotebookAdmin(admin.ModelAdmin):
    form = NotebookAdminForm

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'category':
            return ModelChoiceField(Category.objects.filter(slug="notebook"))
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


class SmartphoneAdmin(admin.ModelAdmin):

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'category':
            return ModelChoiceField(Category.objects.filter(slug="smartphone"))
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


admin.site.register(Category)
admin.site.register(Notebook, NotebookAdmin)
admin.site.register(Smartphone, SmartphoneAdmin)
admin.site.register(BasketProduct)
admin.site.register(Basket)
admin.site.register(Customer)
