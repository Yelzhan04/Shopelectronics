from django.urls import reverse
from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from PIL import Image

User = get_user_model()


def get_product_url(obj, viewname):
    ct_model = obj.__class__.meta.model_name
    return reverse(viewname, kwargs={"ct_model": ct_model, "slug": obj.slug})


class LatestProductManager:
    @staticmethod  # static method for work
    def get_product_for_main_page(*args, **kwargs):
        with_respect_to = kwargs.get("with_respect_to")
        products = []
        ct_models = ContentType.objects.filter(model__in=args)
        for ct_model in ct_models:
            model_products = ct_model.model_class()._base_manager.all().order_by('-id')[:5]
            products.extend(model_products)
        if with_respect_to:
            ct_model = ContentType.objects.filter(model=with_respect_to)
            if ct_model.exists():
                if with_respect_to in args:
                    return sorted(products, key=lambda x: x.__class__._meta.model_name.startswith(with_respect_to),
                                  reverse=True)

        return products


class LatestProduct:
    objects = LatestProductManager()


# **********
# 1.Product
# 2.Category
# 3.BasketProduct
# 4.Basket
# 5.Order
# **********
# 6.Customer
class Category(models.Model):
    name = models.CharField(max_length=250)
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.name


class Product(models.Model):
    MIN_RESOLUTION = (400, 400)
    MAX_RESOLUTION = (800, 800)
    MAX_IMAGE_SIZE = 3145728

    class Meta:
        abstract = True

    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    title = models.CharField(max_length=250, verbose_name="Product Name")
    slug = models.SlugField(unique=True)
    image = models.ImageField(verbose_name="Product Image")
    description = models.TextField(verbose_name="Product Description", null=True)
    price = models.DecimalField(max_digits=9, decimal_places=2, verbose_name="Price")

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        image = self.image
        img = Image.open(image)
        min_height, min_width = self.MIN_RESOLUTION
        max_height, max_width = self.MAX_RESOLUTION
        if img.height < min_height or img.width < min_width:
            raise Exception("Image resolution less than minimum resolution!")
        if img.height > max_height or img.width > max_width:
            raise Exception("Image resolution more than maximum resolution!")
        super().save(*args, **kwargs)


class BasketProduct(models.Model):
    user = models.ForeignKey('Customer', verbose_name="Buyer", on_delete=models.CASCADE)
    basket = models.ForeignKey('Basket', verbose_name="Basket", on_delete=models.CASCADE,related_name='related_product')
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    quantity = models.PositiveIntegerField(default=1)
    final_price = models.DecimalField(max_digits=9, decimal_places=2, verbose_name='Total price')

    def __str__(self):
        return "Product : {} (for basket)".format(self.content_object.title)


class Basket(models.Model):
    owner = models.ForeignKey('Customer', verbose_name="Owner", on_delete=models.CASCADE)
    products = models.ManyToManyField(BasketProduct, blank=True, related_name='related_basket')
    total_product = models.PositiveIntegerField(default=0)
    final_price = models.DecimalField(max_digits=9, decimal_places=2, verbose_name='Total price')
    in_order = models.BooleanField(default=False)
    for_unkown_user = models.BooleanField(default=False)

    def __str__(self):
        return str(self.id)


class Customer(models.Model):
    user = models.ForeignKey(User, verbose_name='User', on_delete=models.CASCADE)
    phone = models.CharField(max_length=20, verbose_name='Phone number')
    address = models.CharField(max_length=255, verbose_name="Address")

    def __str__(self):
        return "Buyer:{} {}".format(self.user.first_name, self.user.last_name)


class Notebook(Product):
    diagonal = models.CharField(max_length=255, verbose_name='Diagonal')
    display_type = models.CharField(max_length=255, verbose_name='Type of display')
    proccesor_freq = models.CharField(max_length=255, verbose_name='CPU frequency')
    ram = models.CharField(max_length=255, verbose_name='RAM')
    graph_card = models.CharField(max_length=255, verbose_name='Graphics card')
    time_without_charge = models.CharField(max_length=255, verbose_name='Battery life')

    def __str__(self):
        return "{}:{}".format(self.category.name, self.title)

    def get_absolute_url(self):
        return get_product_url(self, 'product_detail')


class Smartphone(Product):
    diagonal = models.CharField(max_length=255, verbose_name='Diagonal')
    display_type = models.CharField(max_length=255, verbose_name='Type of display')
    resolution = models.CharField(max_length=255, verbose_name='Screen resolution')
    battery_volume = models.CharField(max_length=255, verbose_name='Volume of battery')
    ram = models.CharField(max_length=255, verbose_name='RAM')
    sd = models.BooleanField(default=True)
    sd_volume = models.CharField(max_length=255, verbose_name="Maximum built-in memory")
    back_cam_mp = models.CharField(max_length=255, verbose_name="Back camera")
    front_cam_mp = models.CharField(max_length=255, verbose_name="Front camera")

    def __str__(self):
        return "{}:{}".format(self.category.name, self.title)

    def get_absolute_url(self):
        return get_product_url(self, 'product_detail')
