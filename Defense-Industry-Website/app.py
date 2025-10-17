from flask import Flask, render_template, request, redirect, url_for, abort
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.utils import secure_filename
import os

from models import db, User, Product, CarouselItem
from forms import LoginForm


app = Flask(__name__)
app.secret_key = "SayGex"

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///users.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["UPLOAD_FOLDER"] = "static/img"
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}

db.init_app(app)

login_manager = LoginManager(app)
login_manager.login_view = "admin"


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


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


@app.route("/admin", methods=["GET", "POST"])
def admin():
    form = LoginForm()
    error = None

    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            return redirect(url_for("admin_dashboard"))
        error = "Невірний логін або пароль"

    return render_template("admin.html", form=form, error=error)


@app.route("/admin/dashboard")
@login_required
def admin_dashboard():
    q = request.args.get("q", "").lower()
    products = Product.query.filter(Product.name.ilike(f"%{q}%")).all() if q else Product.query.all()
    return render_template("admin_dashboard.html", products=products, admin_name=current_user.name)


@app.route("/admin/add_product", methods=["GET", "POST"])
@login_required
def add_product():
    if request.method == "POST":
        name = request.form.get("name")
        desc = request.form.get("desc")
        file = request.files.get("img_file")

        if name and desc and file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
            product = Product(name=name, desc=desc, img=filename)
            db.session.add(product)
            db.session.commit()
            return redirect(url_for("admin_dashboard"))

    return render_template("add_product.html")

@app.route("/admin/edit/<int:product_id>", methods=["GET", "POST"])
@login_required
def edit_product(product_id):
    product = Product.query.get_or_404(product_id)

    if request.method == "POST":
        product.name = request.form.get("name")
        product.desc = request.form.get("desc")

        file = request.files.get("img_file")
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
            product.img = filename

        db.session.commit()
        return redirect(url_for("admin_dashboard"))

    return render_template("edit_product.html", product=product)


@app.route("/admin/delete/<int:product_id>", methods=["POST"])
@login_required
def delete_product(product_id):
    product = Product.query.get_or_404(product_id)
    db.session.delete(product)
    db.session.commit()
    return redirect(url_for("admin_dashboard"))


@app.route("/admin/carousel")
@login_required
def admin_carousel():
    carousel_items = CarouselItem.query.all()
    return render_template("admin_carousel.html", carousel_items=carousel_items, admin_name=current_user.name)


@app.route("/admin/add_carousel_item", methods=["GET", "POST"])
@login_required
def add_carousel_item():
    if request.method == "POST":
        title = request.form.get("title")
        desc = request.form.get("desc")
        text_position = request.form.get("text_position") or "center"
        button_text = request.form.get("button_text") or ""
        button_link = request.form.get("button_link") or "#"
        file = request.files.get("img_file")

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))

            item = CarouselItem(
                img=filename,
                title=title,
                desc=desc,
                text_position=text_position,
                button_text=button_text,
                button_link=button_link,
            )
            db.session.add(item)
            db.session.commit()
            return redirect(url_for("admin_carousel"))

    return render_template("add_carousel_item.html")


@app.route("/admin/carousel/edit/<int:item_id>", methods=["GET", "POST"])
@login_required
def edit_carousel(item_id):
    item = CarouselItem.query.get_or_404(item_id)

    if request.method == "POST":
        file = request.files.get("img_file")
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
            item.img = filename

        item.title = request.form.get("title") or item.title
        item.desc = request.form.get("desc") or item.desc
        item.text_position = request.form.get("text_position") or item.text_position
        item.button_text = request.form.get("button_text") or item.button_text
        item.button_link = request.form.get("button_link") or item.button_link

        db.session.commit()
        return redirect(url_for("admin_carousel"))

    return render_template("edit_carousel.html", item=item)


@app.route("/admin/carousel/delete/<int:item_id>", methods=["POST"])
@login_required
def delete_carousel_item(item_id):
    item = CarouselItem.query.get_or_404(item_id)
    db.session.delete(item)
    db.session.commit()
    return redirect(url_for("admin_carousel"))


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("admin"))

if __name__ == "__main__":
    with app.app_context():
        db.create_all()

        if not User.query.first():
            admins = [
                {"username": "admin", "password": "12345", "name": "Головний Адмін", "email": "admin@example.com"},
                {"username": "root", "password": "qwerty", "name": "Супер Адмін", "email": "root@example.com"},
            ]
            for a in admins:
                user = User(**a)
                db.session.add(user)
            db.session.commit()

        if not CarouselItem.query.first():
            default_items = [
                CarouselItem(
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
