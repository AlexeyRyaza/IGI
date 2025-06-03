from django.test import TestCase
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import timedelta
from core.models import Promo, Article, CompanyInfo, FAQ
from django.core.files.uploadedfile import SimpleUploadedFile

class PromoTests(TestCase):
    def setUp(self):
        self.now = timezone.now()

    def test_promo_creation(self):
        """Test creating promos with different parameters"""
        # Create basic promo
        promo = Promo.objects.create(
            code='TEST10',
            description='Test promo',
            discount=10,
            valid_from=self.now,
            valid_to=self.now + timedelta(days=30)
        )
        self.assertEqual(promo.code, 'TEST10')
        self.assertEqual(promo.discount, 10)
        self.assertTrue(promo.is_active)

    def test_promo_validation(self):
        """Test promo code validation"""
        # Test invalid discount values
        with self.assertRaises(ValidationError):
            promo = Promo(
                code='TEST',
                description='Test promo',
                discount=-10,  # Negative discount
                valid_from=self.now,
                valid_to=self.now + timedelta(days=30)
            )
            promo.full_clean()

        with self.assertRaises(ValidationError):
            promo = Promo(
                code='TEST',
                description='Test promo',
                discount=110,  # Discount > 100
                valid_from=self.now,
                valid_to=self.now + timedelta(days=30)
            )
            promo.full_clean()

        # Test invalid dates
        with self.assertRaises(ValidationError):
            promo = Promo(
                code='TEST',
                description='Test promo',
                discount=10,
                valid_from=self.now + timedelta(days=1),
                valid_to=self.now  # End date before start date
            )
            promo.full_clean()

    def test_promo_validity_period(self):
        """Test promo validity periods"""
        # Test expired promo
        expired_promo = Promo.objects.create(
            code='EXPIRED',
            description='Expired promo',
            discount=20,
            valid_from=self.now - timedelta(days=2),
            valid_to=self.now - timedelta(days=1)
        )
        self.assertFalse(expired_promo.is_valid)

        # Test future promo
        future_promo = Promo.objects.create(
            code='FUTURE',
            description='Future promo',
            discount=15,
            valid_from=self.now + timedelta(days=1),
            valid_to=self.now + timedelta(days=2)
        )
        self.assertFalse(future_promo.is_valid)

        # Test current promo
        current_promo = Promo.objects.create(
            code='CURRENT',
            description='Current promo',
            discount=25,
            valid_from=self.now - timedelta(hours=1),
            valid_to=self.now + timedelta(hours=1)
        )
        self.assertTrue(current_promo.is_valid)

    def test_promo_deactivation(self):
        """Test promo deactivation"""
        promo = Promo.objects.create(
            code='TEST',
            description='Test promo',
            discount=10,
            valid_from=self.now,
            valid_to=self.now + timedelta(days=30)
        )
        self.assertTrue(promo.is_valid)

        # Deactivate promo
        promo.is_active = False
        promo.save()
        self.assertFalse(promo.is_valid)

class ArticleTests(TestCase):
    def setUp(self):
        # Create a test image file
        self.image_file = SimpleUploadedFile(
            "test_image.jpg",
            b"file_content",
            content_type="image/jpeg"
        )

    def test_article_creation(self):
        """Test creating articles"""
        article = Article.objects.create(
            title='Test Article',
            content='Test content',
            short_description='Short description',
            image=self.image_file,
            is_published=True
        )
        
        self.assertEqual(article.title, 'Test Article')
        self.assertTrue(article.is_published)
        self.assertIsNotNone(article.created_at)

    def test_article_ordering(self):
        """Test that articles are ordered by created_at in descending order"""
        # Create articles with different creation times
        article1 = Article.objects.create(
            title='First Article',
            content='Content 1',
            short_description='Description 1'
        )
        
        article2 = Article.objects.create(
            title='Second Article',
            content='Content 2',
            short_description='Description 2'
        )
        
        # Get ordered articles
        articles = Article.objects.all()
        self.assertEqual(articles[0], article2)
        self.assertEqual(articles[1], article1)

    def test_article_validation(self):
        """Test article validation"""
        # Test empty title
        article_no_title = Article(
            title='',
            content='Test content',
            short_description='Short description'
        )
        with self.assertRaises(ValidationError) as context:
            article_no_title.full_clean()
        self.assertIn('title', str(context.exception))

        # Test empty content
        article_no_content = Article(
            title='Test Title',
            content='',
            short_description='Short description'
        )
        with self.assertRaises(ValidationError) as context:
            article_no_content.full_clean()
        self.assertIn('content', str(context.exception))

        # Test short description length
        article_long_desc = Article(
            title='Test Article',
            content='Test content',
            short_description='x' * 301  # More than 300 characters
        )
        with self.assertRaises(ValidationError) as context:
            article_long_desc.full_clean()
        self.assertIn('short_description', str(context.exception))

        # Test valid article
        article_valid = Article(
            title='Test Article',
            content='Test content',
            short_description='Valid short description'
        )
        try:
            article_valid.full_clean()
        except ValidationError:
            self.fail("Valid article should not raise ValidationError")

class CompanyInfoTests(TestCase):
    def setUp(self):
        self.logo = SimpleUploadedFile(
            "logo.jpg",
            b"file_content",
            content_type="image/jpeg"
        )

    def test_company_info_creation(self):
        """Test creating company info"""
        info = CompanyInfo.objects.create(
            title='Test Company',
            content='Company description',
            year=2020,
            logo=self.logo,
            video_url='https://youtube.com/watch?v=test'
        )
        
        self.assertEqual(info.title, 'Test Company')
        self.assertEqual(info.year, 2020)

    def test_company_info_ordering(self):
        """Test company info ordering"""
        info1 = CompanyInfo.objects.create(
            title='Info 1',
            content='Content 1',
            order=2
        )
        
        info2 = CompanyInfo.objects.create(
            title='Info 2',
            content='Content 2',
            order=1
        )
        
        infos = CompanyInfo.objects.all()
        self.assertEqual(infos[0], info2)  # Lower order should be first
        self.assertEqual(infos[1], info1)

    def test_company_info_validation(self):
        """Test company info validation"""
        # Test empty title
        info_no_title = CompanyInfo(
            title='',
            content='Test content'
        )
        with self.assertRaises(ValidationError) as context:
            info_no_title.full_clean()
        self.assertIn('title', str(context.exception))

        # Test empty content
        info_no_content = CompanyInfo(
            title='Test Title',
            content=''
        )
        with self.assertRaises(ValidationError) as context:
            info_no_content.full_clean()
        self.assertIn('content', str(context.exception))

        # Test invalid year
        info_future_year = CompanyInfo(
            title='Test Company',
            content='Test content',
            year=timezone.now().year + 1
        )
        with self.assertRaises(ValidationError) as context:
            info_future_year.full_clean()
        self.assertIn('year', str(context.exception))

class FAQTests(TestCase):
    def test_faq_creation(self):
        """Test creating FAQ entries"""
        # Create term entry
        term = FAQ.objects.create(
            title='What is service center?',
            content='A place where devices are repaired',
            entry_type='term'
        )
        self.assertEqual(term.entry_type, 'term')

        # Create question entry
        question = FAQ.objects.create(
            title='How to contact us?',
            content='You can call us or visit our office',
            entry_type='question'
        )
        self.assertEqual(question.entry_type, 'question')

    def test_faq_ordering(self):
        """Test FAQ entries ordering"""
        faq1 = FAQ.objects.create(
            title='B Question',
            content='Content',
            entry_type='question',
            order=1
        )
        
        faq2 = FAQ.objects.create(
            title='A Question',
            content='Content',
            entry_type='question',
            order=1
        )
        
        faqs = FAQ.objects.all()
        # Should be ordered by order first, then by title
        self.assertEqual(faqs[0], faq2)  # 'A' comes before 'B'
        self.assertEqual(faqs[1], faq1)

    def test_faq_validation(self):
        """Test FAQ validation"""
        # Test invalid entry type
        faq_invalid_type = FAQ(
            title='Test',
            content='Content',
            entry_type='invalid_type'
        )
        with self.assertRaises(ValidationError) as context:
            faq_invalid_type.full_clean()
        self.assertIn('entry_type', str(context.exception))

        # Test empty title
        faq_no_title = FAQ(
            title='',
            content='Content',
            entry_type='question'
        )
        with self.assertRaises(ValidationError) as context:
            faq_no_title.full_clean()
        self.assertIn('title', str(context.exception))

        # Test empty content
        faq_no_content = FAQ(
            title='Test',
            content='',
            entry_type='question'
        )
        with self.assertRaises(ValidationError) as context:
            faq_no_content.full_clean()
        self.assertIn('content', str(context.exception)) 