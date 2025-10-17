from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from flask import Flask, render_template, request, redirect, url_for, abort, flash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.utils import secure_filename
import os

from models import db, User, Product, CarouselItem
from forms import LoginForm, ProductForm, CarouselItemForm, SearchForm

app = Flask(__name__)
app.secret_key = "SayGex"

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///app_data.db"  # Змінено назву файлу БД
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["UPLOAD_FOLDER"] = "static/img"
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}

db.init_app(app)

login_manager = LoginManager(app)
login_manager.login_view = "admin"
login_manager.login_message = "Будь ласка, авторизуйтеся для доступу."


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


# -------------------- Маршрути Користувачів -------------------- #
@app.route("/")
def index():
    carousel_items = CarouselItem.query.all()
    return render_template("index.html", carousel_items=carousel_items)


@app.route("/products")
def products_page():
    products = Product.query.all()
    return render_template("products.html", products=products)


@app.route("/products/<int:product_id>")
def product_detail(product_id):
    product = Product.query.get_or_404(product_id)
    return render_template("product_detail.html", product=product)


# -------------------- Маршрути Адміністратора -------------------- #
@app.route("/admin", methods=["GET", "POST"])
def admin():
    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        # Пароль має бути захешований у реальному проєкті (наприклад, за допомогою werkzeug.security)
        if user and user.check_password(form.password.data):
            login_user(user)
            return redirect(url_for("admin_dashboard"))

        flash("Невірний логін або пароль", "error")  # Використовуємо flash для виведення повідомлення

    return render_template("admin.html", form=form)


@app.route("/admin/dashboard", methods=["GET"])
@login_required
def admin_dashboard():
    # Використовуємо форму для обробки пошуку
    search_form = SearchForm(request.args)
    q = search_form.q.data if search_form.q.data else ""

    products = Product.query.filter(Product.name.ilike(f"%{q}%")).all() if q else Product.query.all()

    return render_template(
        "admin_dashboard.html",
        products=products,
        admin_name=current_user.name,
        search_form=search_form
    )


# -------------------- Продукти (CRUD) -------------------- #
@app.route("/admin/add_product", methods=["GET", "POST"])
@login_required
def add_product():
    form = ProductForm()

    if form.validate_on_submit():
        file = form.img_file.data

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            try:
                # Зберігаємо файл
                # file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))

                # Створюємо новий об'єкт продукту
                product = Product(
                    name=form.name.data,
                    desc=form.desc.data,
                    img=filename
                )
                db.session.add(product)
                db.session.commit()
                flash(f"Продукт '{product.name}' успішно додано.", "success")
                return redirect(url_for("admin_dashboard"))
            except Exception as e:
                # В реальному оточенні тут має бути логування
                flash(f"Помилка при збереженні даних: {e}", "error")
        else:
            flash("Необхідно завантажити коректне зображення.", "error")

    return render_template("add_product.html", form=form)


@app.route("/admin/edit/<int:product_id>", methods=["GET", "POST"])
@login_required
def edit_product(product_id):
    product = Product.query.get_or_404(product_id)

    # Заповнюємо форму даними з бази, якщо GET-запит
    form = ProductForm(obj=product)

    if form.validate_on_submit():
        # Оновлюємо текстові поля
        product.name = form.name.data
        product.desc = form.desc.data

        file = form.img_file.data
        if file:
            if allowed_file(file.filename):
                filename = secure_filename(file.filename)
                # file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename)) # Імітація збереження
                product.img = filename
                flash("Зображення оновлено.", "success")
            else:
                flash("Файл зображення має некоректний формат.", "error")
                return render_template("edit_product.html", product=product, form=form)  # Залишаємося на сторінці

        db.session.commit()
        flash(f"Продукт '{product.name}' успішно оновлено.", "success")
        return redirect(url_for("admin_dashboard"))

    # Скидаємо поле файлу, щоб воно не відображало попередній шлях
    form.img_file.data = None

    return render_template("edit_product.html", product=product, form=form)


@app.route("/admin/delete/<int:product_id>", methods=["POST"])
@login_required
def delete_product(product_id):
    product = Product.query.get_or_404(product_id)
    db.session.delete(product)
    db.session.commit()
    flash(f"Продукт '{product.name}' видалено.", "success")
    return redirect(url_for("admin_dashboard"))


# -------------------- Карусель (CRUD) -------------------- #
@app.route("/admin/carousel")
@login_required
def admin_carousel():
    carousel_items = CarouselItem.query.all()
    return render_template("admin_carousel.html", carousel_items=carousel_items, admin_name=current_user.name)


@app.route("/admin/add_carousel_item", methods=["GET", "POST"])
@login_required
def add_carousel_item():
    form = CarouselItemForm()

    if form.validate_on_submit():
        file = form.img_file.data

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            # file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename)) # Імітація збереження

            item = CarouselItem(
                img=filename,
                title=form.title.data,
                desc=form.desc.data,
                text_position=form.text_position.data,
                button_text=form.button_text.data,
                button_link=form.button_link.data,
            )
            db.session.add(item)
            db.session.commit()
            flash(f"Слайд '{item.title}' успішно додано.", "success")
            return redirect(url_for("admin_carousel"))
        else:
            flash("Необхідно завантажити коректне зображення для слайда.", "error")

    return render_template("add_carousel_item.html", form=form)


@app.route("/admin/carousel/edit/<int:item_id>", methods=["GET", "POST"])
@login_required
def edit_carousel(item_id):
    item = CarouselItem.query.get_or_404(item_id)

    # Заповнюємо форму даними з бази, якщо GET-запит
    form = CarouselItemForm(obj=item)

    if form.validate_on_submit():
        file = form.img_file.data
        if file:
            if allowed_file(file.filename):
                filename = secure_filename(file.filename)
                # file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename)) # Імітація збереження
                item.img = filename
                flash("Зображення слайда оновлено.", "success")
            else:
                flash("Файл зображення має некоректний формат.", "error")
                return render_template("edit_carousel.html", item=item, form=form)

        # Оновлюємо дані об'єкта item з даних форми
        item.title = form.title.data
        item.desc = form.desc.data
        item.text_position = form.text_position.data
        item.button_text = form.button_text.data
        item.button_link = form.button_link.data

        db.session.commit()
        flash(f"Слайд '{item.title}' успішно оновлено.", "success")
        return redirect(url_for("admin_carousel"))

    # Скидаємо поле файлу
    form.img_file.data = None

    return render_template("edit_carousel.html", item=item, form=form)


@app.route("/admin/carousel/delete/<int:item_id>", methods=["POST"])
@login_required
def delete_carousel_item(item_id):
    item = CarouselItem.query.get_or_404(item_id)
    db.session.delete(item)
    db.session.commit()
    flash(f"Слайд '{item.title}' видалено.", "success")
    return redirect(url_for("admin_carousel"))


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("admin"))


if __name__ == "__main__":
    # Щоб уникнути помилок Circular Import
    from models import db, User, Product, CarouselItem

    with app.app_context():
        # Створення таблиць
        db.create_all()

        # Ініціалізація користувачів
        if not User.query.first():
            admins = [
                {"username": "admin", "password": "12345", "name": "Головний Адмін", "email": "admin@example.com"},
                {"username": "root", "password": "qwerty", "name": "Супер Адмін", "email": "root@example.com"},
            ]
            for a in admins:
                user = User(**a)
                db.session.add(user)
            db.session.commit()

        # Ініціалізація ПРОДУКТІВ (ОНОВЛЕНО: Використовуються наявні імена файлів)
        if not Product.query.first():
            default_products = [
                Product(
                    name="Тактичні навушники X1",
                    desc="Професійні активні навушники для захисту слуху в бойових умовах. Збільшують чутність оточення, приглушуючи гучні звуки.",
                    # Використовуємо наявне hero.png
                    img="hero.png"
                ),
                Product(
                    name="FPV-дрон 'Колібрі'",
                    desc="Маневрений FPV-дрон для розвідки та коригування вогню. Надзвичайно швидкий та стійкий до перешкод.",
                    # Використовуємо наявне innovation.jpg
                    img="innovation.jpg"
                ),
                Product(
                    name="Польовий рюкзак 'Бастіон'",
                    desc="Надійний 80-літровий рюкзак з ергономічною системою розвантаження. Виготовлений з водонепроникної тканини CORDURA.",
                    # Використовуємо наявне security.jpeg
                    img="security.jpeg"
                ),
            ]
            db.session.add_all(default_products)
            db.session.commit()

        # Ініціалізація каруселі (також перевіряю імена файлів тут)
        if not CarouselItem.query.first():
            default_items = [
                CarouselItem(
                    # su-27.jpg присутній
                    img="su-27.jpg",
                    title="Технології для нашої авіації",
                    desc="Технології, з якими 'Привид Києва' став Легендою.",
                    text_position="right",
                    button_text="Переглянути продукцію",
                    button_link="/products"
                ),
                CarouselItem(
                    img="fpv.jpeg",
                    title="FPV — дрони",
                    desc="Зброя, що змінила сучасну війну.",
                    text_position="left",
                    button_text="Переглянути продукцію",
                    button_link="/products"
                ),
                CarouselItem(
                    # ssu2.jpg присутній
                    img="ssu2.jpg",
                    title="Якісне спорядження",
                    desc="Комфорт та безпека.",
                    text_position="center",
                    button_text="Переглянути продукцію",
                    button_link="/products"
                ),
            ]
            db.session.add_all(default_items)
            db.session.commit()

    app.run(debug=True)

