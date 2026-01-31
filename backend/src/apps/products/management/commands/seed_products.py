import random
from django.core.management.base import BaseCommand
from apps.products.models import Category, Product


class Command(BaseCommand):
    help = 'Seed database with 40 mock products'

    def handle(self, *args, **options):
        # Create categories if they don't exist
        categories_data = [
            {'title': 'Букеты', 'slug': 'bukety', 'sort_order': 1},
            {'title': 'Композиции', 'slug': 'kompozitsii', 'sort_order': 2},
            {'title': 'Розы', 'slug': 'rozy', 'sort_order': 3},
            {'title': 'Сухоцветы', 'slug': 'suhotsvety', 'sort_order': 4},
            {'title': 'Подарки', 'slug': 'podarki', 'sort_order': 5},
        ]

        categories = {}
        for cat_data in categories_data:
            cat, created = Category.objects.get_or_create(
                slug=cat_data['slug'],
                defaults={
                    'title': cat_data['title'],
                    'sort_order': cat_data['sort_order'],
                    'is_active': True,
                }
            )
            categories[cat_data['slug']] = cat
            if created:
                self.stdout.write(f'Created category: {cat.title}')

        # Mock products data
        products_data = [
            # Букеты (12 items)
            {
                'category': 'bukety',
                'title': 'Нежность весны',
                'description': 'Легкий весенний букет из тюльпанов, нарциссов и зелени. Идеален для подарка любимым.',
                'price': 350000,
                'old_price': None,
                'qty_available': 15,
            },
            {
                'category': 'bukety',
                'title': 'Солнечный день',
                'description': 'Яркий букет из подсолнухов и желтых хризантем. Подарит хорошее настроение!',
                'price': 420000,
                'old_price': 500000,
                'qty_available': 8,
            },
            {
                'category': 'bukety',
                'title': 'Романтика Парижа',
                'description': 'Элегантный букет из пионовидных роз, эустомы и эвкалипта в нежных тонах.',
                'price': 650000,
                'old_price': None,
                'qty_available': 5,
            },
            {
                'category': 'bukety',
                'title': 'Летний бриз',
                'description': 'Полевые цветы: ромашки, васильки, лаванда. Как прогулка по летнему лугу.',
                'price': 280000,
                'old_price': None,
                'qty_available': 20,
            },
            {
                'category': 'bukety',
                'title': 'Королевский',
                'description': 'Роскошный букет из пионов, роз и орхидей. Для особенных моментов.',
                'price': 890000,
                'old_price': 1050000,
                'qty_available': 3,
            },
            {
                'category': 'bukety',
                'title': 'Весенняя капель',
                'description': 'Нежный букет из гиацинтов и фрезий с ароматом весны.',
                'price': 320000,
                'old_price': None,
                'qty_available': 12,
            },
            {
                'category': 'bukety',
                'title': 'Морской бриз',
                'description': 'Букет в сине-белых тонах: гортензии, дельфиниум, белые розы.',
                'price': 550000,
                'old_price': None,
                'qty_available': 7,
            },
            {
                'category': 'bukety',
                'title': 'Осенний вальс',
                'description': 'Тёплые оттенки: оранжевые розы, хризантемы, ягоды.',
                'price': 480000,
                'old_price': 560000,
                'qty_available': 9,
            },
            {
                'category': 'bukety',
                'title': 'Первое свидание',
                'description': 'Скромный, но элегантный букет из розовых роз и альстромерий.',
                'price': 250000,
                'old_price': None,
                'qty_available': 25,
            },
            {
                'category': 'bukety',
                'title': 'Праздничный',
                'description': 'Яркий микс из гербер, роз и хризантем. Для любого праздника!',
                'price': 390000,
                'old_price': None,
                'qty_available': 18,
            },
            {
                'category': 'bukety',
                'title': 'Монобукет из лилий',
                'description': 'Изысканный букет из белых лилий с насыщенным ароматом.',
                'price': 450000,
                'old_price': None,
                'qty_available': 6,
            },
            {
                'category': 'bukety',
                'title': 'Нежный пион',
                'description': 'Роскошные пионы в крафтовой упаковке. Сезонное предложение.',
                'price': 720000,
                'old_price': 850000,
                'qty_available': 4,
            },

            # Композиции (8 items)
            {
                'category': 'kompozitsii',
                'title': 'Цветочная шляпная коробка',
                'description': 'Стильная композиция в шляпной коробке: розы, гвоздики, эвкалипт.',
                'price': 520000,
                'old_price': None,
                'qty_available': 10,
            },
            {
                'category': 'kompozitsii',
                'title': 'Корзина изобилия',
                'description': 'Большая корзина с сезонными цветами. Идеальна для юбилея.',
                'price': 980000,
                'old_price': None,
                'qty_available': 3,
            },
            {
                'category': 'kompozitsii',
                'title': 'Сердце из роз',
                'description': 'Композиция в форме сердца из красных роз. Признание в любви.',
                'price': 750000,
                'old_price': 890000,
                'qty_available': 5,
            },
            {
                'category': 'kompozitsii',
                'title': 'Мини-сад',
                'description': 'Композиция с суккулентами и мхом в стеклянном террариуме.',
                'price': 380000,
                'old_price': None,
                'qty_available': 8,
            },
            {
                'category': 'kompozitsii',
                'title': 'Ящик с цветами',
                'description': 'Деревянный ящик с пионовидными розами и лизиантусом.',
                'price': 620000,
                'old_price': None,
                'qty_available': 6,
            },
            {
                'category': 'kompozitsii',
                'title': 'Цветы в конверте',
                'description': 'Миниатюрная композиция в конверте из крафт-бумаги.',
                'price': 220000,
                'old_price': None,
                'qty_available': 15,
            },
            {
                'category': 'kompozitsii',
                'title': 'Luxury Box',
                'description': 'Премиум композиция в бархатной коробке с розами и орхидеями.',
                'price': 1200000,
                'old_price': 1450000,
                'qty_available': 2,
            },
            {
                'category': 'kompozitsii',
                'title': 'Настольная композиция',
                'description': 'Низкая композиция для украшения стола на мероприятии.',
                'price': 480000,
                'old_price': None,
                'qty_available': 7,
                'is_unlimited': True,
            },

            # Розы (10 items)
            {
                'category': 'rozy',
                'title': '25 красных роз',
                'description': 'Классика жанра. Эквадорские розы премиум качества.',
                'price': 550000,
                'old_price': None,
                'qty_available': 0,
                'is_unlimited': True,
            },
            {
                'category': 'rozy',
                'title': '51 роза микс',
                'description': 'Букет из роз разных оттенков: красные, розовые, белые.',
                'price': 950000,
                'old_price': 1100000,
                'qty_available': 0,
                'is_unlimited': True,
            },
            {
                'category': 'rozy',
                'title': '101 роза',
                'description': 'Впечатляющий букет для грандиозных событий.',
                'price': 1800000,
                'old_price': None,
                'qty_available': 0,
                'is_unlimited': True,
            },
            {
                'category': 'rozy',
                'title': '11 белых роз',
                'description': 'Элегантный букет из белых роз. Символ чистоты.',
                'price': 280000,
                'old_price': None,
                'qty_available': 0,
                'is_unlimited': True,
            },
            {
                'category': 'rozy',
                'title': '15 розовых роз',
                'description': 'Нежный букет из розовых роз с эвкалиптом.',
                'price': 350000,
                'old_price': None,
                'qty_available': 0,
                'is_unlimited': True,
            },
            {
                'category': 'rozy',
                'title': 'Радужные розы',
                'description': 'Уникальные розы с разноцветными лепестками. 15 штук.',
                'price': 680000,
                'old_price': None,
                'qty_available': 5,
            },
            {
                'category': 'rozy',
                'title': 'Кустовые розы',
                'description': 'Букет из нежных кустовых роз. 9 веток.',
                'price': 320000,
                'old_price': 380000,
                'qty_available': 10,
            },
            {
                'category': 'rozy',
                'title': 'Розы в коробке',
                'description': '25 красных роз в круглой шляпной коробке.',
                'price': 680000,
                'old_price': None,
                'qty_available': 0,
                'is_unlimited': True,
            },
            {
                'category': 'rozy',
                'title': 'Пионовидные розы',
                'description': 'Ароматные пионовидные розы David Austin. 11 штук.',
                'price': 720000,
                'old_price': 850000,
                'qty_available': 4,
            },
            {
                'category': 'rozy',
                'title': 'Метровые розы',
                'description': 'Впечатляющие розы на длинном стебле. 15 штук.',
                'price': 890000,
                'old_price': None,
                'qty_available': 0,
                'is_unlimited': True,
            },

            # Сухоцветы (5 items)
            {
                'category': 'suhotsvety',
                'title': 'Букет из лаванды',
                'description': 'Ароматный букет из сушёной лаванды. Прослужит годы.',
                'price': 180000,
                'old_price': None,
                'qty_available': 30,
            },
            {
                'category': 'suhotsvety',
                'title': 'Пампасная трава',
                'description': 'Стильная пампасная трава для интерьера. 5 стеблей.',
                'price': 250000,
                'old_price': None,
                'qty_available': 20,
            },
            {
                'category': 'suhotsvety',
                'title': 'Букет сухоцветов микс',
                'description': 'Композиция из различных сухоцветов в пастельных тонах.',
                'price': 320000,
                'old_price': 380000,
                'qty_available': 15,
            },
            {
                'category': 'suhotsvety',
                'title': 'Хлопок',
                'description': 'Ветки натурального хлопка. 5 веток.',
                'price': 150000,
                'old_price': None,
                'qty_available': 25,
            },
            {
                'category': 'suhotsvety',
                'title': 'Интерьерный букет',
                'description': 'Большой букет сухоцветов для украшения интерьера.',
                'price': 480000,
                'old_price': None,
                'qty_available': 8,
            },

            # Подарки (5 items)
            {
                'category': 'podarki',
                'title': 'Букет с шоколадом',
                'description': 'Букет из роз с набором бельгийского шоколада.',
                'price': 580000,
                'old_price': None,
                'qty_available': 10,
            },
            {
                'category': 'podarki',
                'title': 'Цветы и макаруны',
                'description': 'Нежный букет с коробкой макарунов (12 шт).',
                'price': 520000,
                'old_price': 620000,
                'qty_available': 8,
            },
            {
                'category': 'podarki',
                'title': 'Букет с мягкой игрушкой',
                'description': 'Букет из мини-роз с плюшевым мишкой.',
                'price': 450000,
                'old_price': None,
                'qty_available': 12,
            },
            {
                'category': 'podarki',
                'title': 'Подарочный набор',
                'description': 'Букет, шампанское и конфеты в подарочной корзине.',
                'price': 1100000,
                'old_price': 1350000,
                'qty_available': 5,
            },
            {
                'category': 'podarki',
                'title': 'Цветы с воздушными шарами',
                'description': 'Букет с композицией из гелиевых шаров.',
                'price': 680000,
                'old_price': None,
                'qty_available': 7,
            },
        ]

        created_count = 0
        for idx, prod_data in enumerate(products_data):
            category = categories[prod_data['category']]

            # Check if product already exists
            existing = Product.objects.filter(title=prod_data['title']).first()
            if existing:
                self.stdout.write(f'Product already exists: {prod_data["title"]}')
                continue

            product = Product.objects.create(
                category=category,
                title=prod_data['title'],
                description=prod_data['description'],
                price=prod_data['price'],
                old_price=prod_data.get('old_price'),
                qty_available=prod_data.get('qty_available', 0),
                is_unlimited=prod_data.get('is_unlimited', False),
                is_active=True,
                sort_order=idx,
            )
            created_count += 1
            self.stdout.write(f'Created product: {product.title}')

        self.stdout.write(
            self.style.SUCCESS(f'\nSuccessfully created {created_count} products!')
        )
