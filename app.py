import sqlite3
import os
from flask import Flask, render_template, g, abort, url_for, session, redirect, request

app = Flask(__name__)
app.secret_key = 'yerevan_city_secret_key_123'
DATABASE = 'yerevan.db'

# Multi-language Translations
TRANSLATIONS = {
    'hy': {
        'home': 'Գլխավոր',
        'districts': 'Վարչական շրջաններ',
        'buildings': 'Քաղաքացիական շենքեր',
        'explore': 'Բացահայտել շրջանները',
        'see_buildings': 'Տեսնել շենքերը',
        'welcome_title': 'Երևան',
        'welcome_subtitle': 'Բարի գալուստ Հայաստանի սիրտը: Բացահայտեք հնագույն քաղաքի ժամանակակից շունչը:',
        'adm_districts': 'Վարչական շրջաններ',
        'adm_districts_sub': 'Երևանի 12 ինքնատիպ համայնքները',
        'famous_buildings': 'Քաղաքացիական շենքեր',
        'famous_buildings_sub': 'Ճարտարապետական գլուխգործոցներ',
        'see_all': 'Տեսնել բոլորը',
        'discover': 'Բացահայտել',
        'back_to_districts': 'Վերադառնալ վարչական շրջաններին',
        'back_to_buildings': 'Վերադառնալ քաղաքացիական շենքերին',
        'area': 'Տարածք',
        'population': 'Բնակչություն',
        'features': 'Առանձնահատկություններ',
        'history': 'Պատմություն',
        'view_3d': '3D դիտում',
        'view_3d_desc': '* 3D մոդելը բեռնվում է GLB ֆորմատով: Դուք կարող եք պտտել և մեծացնել մոդելը:',
        'footer_rights': 'Բոլոր իրավունքները պաշտպանված են',
        'lang_name': 'Հայերեն'
    },
    'ru': {
        'home': 'Главная',
        'districts': 'Округа',
        'buildings': 'Гражданские здания',
        'explore': 'Исследовать округа',
        'see_buildings': 'Посмотреть здания',
        'welcome_title': 'Ереван',
        'welcome_subtitle': 'Добро пожаловать в сердце Армении. Откройте для себя современный дух древнего города.',
        'adm_districts': 'Административные округа',
        'adm_districts_sub': '12 уникальных общин Еревана',
        'famous_buildings': 'Гражданские здания',
        'famous_buildings_sub': 'Архитектурные шедевры',
        'see_all': 'Посмотреть все',
        'discover': 'Открыть',
        'back_to_districts': 'Назад к округам',
        'back_to_buildings': 'Назад к зданиям',
        'area': 'Площадь',
        'population': 'Население',
        'features': 'Особенности',
        'history': 'История',
        'view_3d': '3D Просмотр',
        'view_3d_desc': '* 3D модель загружается в формате GLB. Вы можете вращать и масштабировать её.',
        'footer_rights': 'Все права защищены',
        'lang_name': 'Русский'
    },
    'en': {
        'home': 'Home',
        'districts': 'Districts',
        'buildings': 'Civil Buildings',
        'explore': 'Explore Districts',
        'see_buildings': 'See Buildings',
        'welcome_title': 'Yerevan',
        'welcome_subtitle': 'Welcome to the heart of Armenia. Discover the modern spirit of the ancient city.',
        'adm_districts': 'Administrative Districts',
        'adm_districts_sub': '12 unique communities of Yerevan',
        'famous_buildings': 'Civil Buildings',
        'famous_buildings_sub': 'Architectural Masterpieces',
        'see_all': 'See All',
        'discover': 'Discover',
        'back_to_districts': 'Back to Districts',
        'back_to_buildings': 'Back to Buildings',
        'area': 'Area',
        'population': 'Population',
        'features': 'Features',
        'history': 'History',
        'view_3d': '3D View',
        'view_3d_desc': '* The 3D model is loaded in GLB format. You can rotate and zoom using the mouse.',
        'footer_rights': 'All rights reserved',
        'lang_name': 'English'
    }
}

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def init_db():
    if os.path.exists(DATABASE):
        os.remove(DATABASE)
        
    with app.app_context():
        db = get_db()
        # Create Districts Table with multi-lang support
        db.execute('''
            CREATE TABLE IF NOT EXISTS districts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name_hy TEXT NOT NULL,
                name_ru TEXT NOT NULL,
                name_en TEXT NOT NULL,
                name_key TEXT NOT NULL,
                image_url TEXT,
                desc_hy TEXT,
                desc_ru TEXT,
                desc_en TEXT,
                area TEXT,
                population TEXT,
                features_hy TEXT,
                features_ru TEXT,
                features_en TEXT
            )
        ''')
        # Create Buildings Table with multi-lang support
        db.execute('''
            CREATE TABLE IF NOT EXISTS buildings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name_hy TEXT NOT NULL,
                name_ru TEXT NOT NULL,
                name_en TEXT NOT NULL,
                image_url TEXT,
                desc_hy TEXT,
                desc_ru TEXT,
                desc_en TEXT,
                model_id TEXT
            )
        ''')
        
        # Seed Districts with ALL 12 communities and full translations
        districts_data = [
            ('Աջափնյակ', 'Ачапняк', 'Ajapnyak', 'Ajapnyak', 'images/Ajapnyak.jpg', 
             'Աջափնյակ վարչական շրջանը գտնվում է Երևանի հյուսիս-արևմտյան մասում:', 
             'Район Ачапняк расположен в северо-западной части Еревана.',
             'Ajapnyak district is located in the north-western part of Yerevan.',
             '25.8 km²', '109,600', 'Բժշկական կենտրոններ', 'Медицинские центры', 'Medical centers'),
            ('Ավան', 'Аван', 'Avan', 'Avan', 'images/Avan.jpg', 
             'Ավանը Երևանի ամենահին և բարեկարգ շրջաններից է:', 
             'Аван - один из старейших и благоустроенных районов Еревана.',
             'Avan is one of the oldest and most well-maintained districts of Yerevan.',
             '8.3 km²', '53,100', 'Ավանի տաճար', 'Храм Авана', 'Avan Temple'),
            ('Արաբկիր', 'Арабкир', 'Arabkir', 'Arabkir', 'images/Arabkir.jpg', 
             'Արաբկիրը Երևանի խոշորագույն և զարգացած վարչական շրջաններից մեկն է:', 
             'Арабкир - один из крупнейших и развитых районов Еревана.',
             'Arabkir is one of the largest and most developed districts of Yerevan.',
             '12.3 km²', '115,800', 'Կոմիտասի պողոտա', 'Проспект Комитаса', 'Komitas Avenue'),
            ('Դավթաշեն', 'Давташен', 'Davtashen', 'Davtashen', 'images/Davtashen.jpg', 
             'Դավթաշենը գտնվում է Հրազդան գետի աջ ափին:', 
             'Давташен расположен на правом берегу реки Раздан.',
             'Davtashen is located on the right bank of the Hrazdan River.',
             '6.4 km²', '42,500', 'Դավթաշենի կամուրջ', 'Давташенский мост', 'Davtashen Bridge'),
            ('Էրեբունի', 'Эребуни', 'Erebuni', 'Erebuni', 'images/Erebuni.png', 
             'Էրեբունին Երևանի պատմական սիրտն է:', 
             'Эребуни - историческое сердце Еревана.',
             'Erebuni is the historical heart of Yerevan.',
             '48.4 km²', '126,300', 'Էրեբունի ամրոց', 'Крепость Эребуни', 'Erebuni Fortress'),
            ('Քանաքեռ-Զեյթուն', 'Канакер-Зейтун', 'Kanaker-Zeytun', 'Kanaker-Zeytun', 'images/Qanaqer.png', 
             'Այս շրջանը գտնվում է բարձրլեռնային գոտում:', 
             'Этот район расположен в высокогорной зоне.',
             'This district is located in a high-altitude zone.',
             '7.7 km²', '74,100', 'Հաղթանակ զբոսայգի', 'Парк Победы', 'Victory Park'),
            ('Կենտրոն', 'Кентрон', 'Kentron', 'Kentron', 'images/Kentron.jpg', 
             'Երևանի վարչական, մշակութային և տուրիստական կենտրոնն է:', 
             'Административный, культурный и туристический центр Еревана.',
             'The administrative, cultural, and tourist center of Yerevan.',
             '13.3 km²', '125,400', 'Օպերա, Կասկադ', 'Опера, Каскад', 'Opera, Cascade'),
            ('Մալաթիա-Սեբաստիա', 'Малатия-Себастия', 'Malatia-Sebastia', 'Malatia-Sebastia', 'images/Malatia_Sebastia.jpg', 
             'Մալաթիա-Սեբաստիան ունի հարուստ մշակութային և կրոնական պատմություն:', 
             'Малатия-Себастия имеет богатую культурную и религиозную историю.',
             'Malatia-Sebastia has a rich cultural and religious history.',
             '25.2 km²', '181,800', 'Սուրբ Երրորդություն եկեղեցի', 'Церковь Св. Троицы', 'Holy Trinity Church'),
            ('Նոր Նորք', 'Нор Норк', 'Nor Nork', 'Nor_Nork', 'images/Nor_Nork.jpg', 
             'Գտնվում է քաղաքի արևելյան մասում:', 
             'Расположен в восточной части города.',
             'Located in the eastern part of the city.',
             '14.1 km²', '126,300', 'Գայ պողոտա', 'Проспект Гая', 'Gai Avenue'),
            ('Նորք-Մարաշ', 'Норк-Мараш', 'Nork-Marash', 'Nork-Marash', 'images/Norq.jpg', 
             'Այս շրջանը հայտնի է իր գեղեցիկ առանձնատներով:', 
             'Этот район известен своими красивыми особняками.',
             'This district is known for its beautiful mansions.',
             '4.7 km²', '12,000', 'Հեռուստաաշտարակ', 'Телебашня', 'TV Tower'),
            ('Նուբարաշեն', 'Нубарашен', 'Nubarashen', 'Nubarashen', 'images/Nubarashen.jpg', 
             'Երևանի ամենափոքր բնակչությամբ վարչական շրջանն է:', 
             'Административный район с самым маленьким населением в Ереване.',
             'The administrative district with the smallest population in Yerevan.',
             '17.2 km²', '9,800', 'Էկոլոգիական գոտի', 'Экологическая зона', 'Ecological zone'),
            ('Շենգավիթ', 'Шенгавит', 'Shengavit', 'Shengavit', 'images/Shengavit.jpg', 
             'Շենգավիթը Երևանի հնագույն բնակավայրերից մեկն է:', 
             'Шенгавит - одно из древнейших поселений Еревана.',
             'Shengavit is one of the oldest settlements in Yerevan.',
             '40.6 km²', '135,500', 'Կոմիտասի պանթեոն', 'Пантеон Комитаса', 'Komitas Pantheon')
        ]
        db.executemany('''
            INSERT INTO districts (name_hy, name_ru, name_en, name_key, image_url, desc_hy, desc_ru, desc_en, area, population, features_hy, features_ru, features_en)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', districts_data)

        # Seed Buildings
        buildings_data = [
            ('111 Սերիայի "Վրացական" նախագիծ', '111 Серия "Грузинский" проект', '111 Series "Georgian" project', 'images/3dmodels/111.jpg', 
             'Հայտնի է նաև "Վրացական նախագիծ" անվամբ:', 
             'Также известен как "Грузинский проект".',
             'Also known as the "Georgian Project".',
             '111'),
            ('Բադալյան նախագիծ', 'Проект Бадалян', 'Badalyan project', 'images/3dmodels/14.jpg', 
             'Հայաստանում այս կոնստրուկցիայով շենքերը կառուցվել են միայն Երևանում:', 
             'Здания этой конструкции в Армении строились только в Ереване.',
             'Buildings of this design in Armenia were built only in Yerevan.',
             '14'),
            ('Երևանյան ԴՍԿ նախագիծ', 'Ереванский ДСК проект', 'Yerevan DSK project', 'images/3dmodels/9.4.jpg', 
             'Խորհրդային ժամանակաշրջանի պանելային բազմաբնակարան շենք:', 
             'Панельный многоквартирный дом советского периода.',
             'Soviet-era panel apartment building.',
             '9.4')
        ]
        db.executemany('''
            INSERT INTO buildings (name_hy, name_ru, name_en, image_url, desc_hy, desc_ru, desc_en, model_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', buildings_data)
        
        db.commit()

@app.before_request
def before_request():
    if 'lang' not in session:
        session['lang'] = 'hy'

@app.context_processor
def inject_lang():
    def t(key):
        lang = session.get('lang', 'hy')
        return TRANSLATIONS.get(lang, TRANSLATIONS['hy']).get(key, key)
    
    def get_val(obj, field_prefix):
        lang = session.get('lang', 'hy')
        field_name = f"{field_prefix}_{lang}"
        try:
            return obj[field_name]
        except:
            return obj[f"{field_prefix}_hy"]

    return dict(t=t, get_val=get_val, current_lang=session.get('lang', 'hy'))

@app.route('/set_lang/<lang>')
def set_lang(lang):
    if lang in TRANSLATIONS:
        session['lang'] = lang
    return redirect(request.referrer or url_for('index'))

@app.route('/')
def index():
    db = get_db()
    districts_list = db.execute('SELECT * FROM districts LIMIT 3').fetchall()
    buildings_list = db.execute('SELECT * FROM buildings LIMIT 3').fetchall()
    return render_template('index.html', districts=districts_list, buildings=buildings_list)

@app.route('/districts')
def districts():
    db = get_db()
    districts_list = db.execute('SELECT * FROM districts').fetchall()
    return render_template('districts.html', districts=districts_list)

@app.route('/district/<name>')
def district_detail(name):
    db = get_db()
    district = db.execute('SELECT * FROM districts WHERE name_key = ?', (name,)).fetchone()
    if district is None:
        abort(404)
    return render_template('district.html', district=district)

@app.route('/buildings')
def buildings():
    db = get_db()
    buildings_list = db.execute('SELECT * FROM buildings').fetchall()
    return render_template('buildings.html', buildings=buildings_list)

@app.route('/building/<int:id>')
def building_detail(id):
    db = get_db()
    building = db.execute('SELECT * FROM buildings WHERE id = ?', (id,)).fetchone()
    if building is None:
        abort(404)
    return render_template('building.html', building=building)

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
