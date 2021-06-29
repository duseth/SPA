from django.test import TestCase
from .models import Medicine, Product, Pharmacy
from . import views


class MedicineTest(TestCase):

    def setUp(self):
        self.medicines = Medicine.objects.bulk_create(
            [Medicine(
                title="Парацетамол в таблетках 50гр",
                price=50,
                photo='/img.jpg',
                url='/someurl',
                pharmacy='pharmacy'
            ),
                Medicine(
                title="Парацетамол порошок 200гр",
                price=50,
                photo='/img.jpg',
                url='/someurl',
                pharmacy='pharmacy'
            ),
                Medicine(
                title="Найз в таблетках 50гр",
                price=50,
                photo='/img.jpg',
                url='/someurl',
                pharmacy='pharmacy'
            ),
                Medicine(
                title="Ибупрофен 20гр",
                price=50,
                photo='/img.jpg',
                url='/someurl',
                pharmacy='pharmacy'
            )]
        )

        Product.objects.create(
            title='prod1',
            photo='somephoto.png'
        )

    """
    Models tests
    """

    def test_verbose_names_of_medicine_model(self):
        medicine = self.medicines[0]

        expected_verbose_title = medicine._meta.get_field('title').verbose_name
        expected_verbose_photo = medicine._meta.get_field('photo').verbose_name
        expected_verbose_url = medicine._meta.get_field('url').verbose_name
        expected_verbose_pharmacy = medicine._meta.get_field(
            'pharmacy').verbose_name
        expected_verbose_price = medicine._meta.get_field('price').verbose_name

        self.assertEqual(expected_verbose_title, 'title')
        self.assertEqual(expected_verbose_photo, 'photo')
        self.assertEqual(expected_verbose_url, 'url')
        self.assertEqual(expected_verbose_pharmacy, 'pharmacy')
        self.assertEqual(expected_verbose_price, 'price')

    def test_verbose_names_of_product_model(self):
        product = Product.objects.create(
            title='prod1',
            photo='somephoto.png'
        )

        expected_verbose_title = product._meta.get_field('title').verbose_name
        expected_verbose_photo = product._meta.get_field('photo').verbose_name

        self.assertEqual(expected_verbose_title, 'title')
        self.assertEqual(expected_verbose_photo, 'photo')

    def test_verbose_names_of_pharmacy_model(self):
        product = Product.objects.create(
            title='prod1',
            photo='somephoto.png'
        )

        pharmacy = Pharmacy.objects.create(
            pharmacy='pharmacy',
            price=40,
            url='pharmacy_url',
            product=product
        )

        expected_verbose_product = pharmacy._meta.get_field(
            'product').verbose_name
        expected_verbose_url = pharmacy._meta.get_field('url').verbose_name
        expected_verbose_pharmacy = pharmacy._meta.get_field(
            'pharmacy').verbose_name
        expected_verbose_price = pharmacy._meta.get_field('price').verbose_name

        self.assertEqual(expected_verbose_product, 'product')
        self.assertEqual(expected_verbose_url, 'url')
        self.assertEqual(expected_verbose_pharmacy, 'pharmacy')
        self.assertEqual(expected_verbose_price, 'price')

    """
    Views tests
    """

    def test_search_by_query(self):
        query = 'пар'
        result = views.get_medicines(query, 'name')
        self.assertEqual(len(result), 2)

    def test_for_short_query(self):
        response = self.client.get('/search?query=со&sort=name')
        self.assertRedirects(response, '/', status_code=302)

    def test_for_right_query(self):
        response = self.client.get('/search?query=пар&sort=name')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'search.html')

    def test_contact_view(self):
        resp = self.client.get('/contacts')
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'contacts.html')

    def test_pharmacies_view(self):
        resp = self.client.get('/pharmacies')
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'pharmacies.html')

    def test_main_page_view(self):
        resp = self.client.get('/')
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'index.html')
