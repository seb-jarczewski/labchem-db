from flask import Flask, render_template, redirect, url_for
from flask_bootstrap import Bootstrap5
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
from flask_ckeditor import CKEditor

app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
Bootstrap5(app)
ckeditor = CKEditor(app)

# Connect to db
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///reagents.db'
db = SQLAlchemy()
db.init_app(app)


# Configure database table
class LabChem(db.Model):
    lab_id = db.Column(db.Integer, primary_key=True)
    cabinet_number = db.Column(db.String(250), nullable=False)
    english_name = db.Column(db.String(250), nullable=False)
    polish_name = db.Column(db.String(250), nullable=False)
    cas_number = db.Column(db.String(250), nullable=False)
    producer = db.Column(db.String(250), nullable=False)
    packaging_capacity = db.Column(db.String(250), nullable=False)


with app.app_context():
    db.create_all()


# Create new reagent form
class NewChem(FlaskForm):
    lab_id = StringField("Lab id", validators=[DataRequired()])
    cabinet_number = StringField("Cabinet number", validators=[DataRequired()])
    english_name = StringField("English name", validators=[DataRequired()])
    polish_name = StringField("Polish name", validators=[DataRequired()])
    cas_number = StringField("CAS number", validators=[DataRequired()])
    producer = StringField("Producer", validators=[DataRequired()])
    packaging_capacity = StringField("Packaging capacity", validators=[DataRequired()])
    submit = SubmitField("Add to database")


@app.route('/')
def get_all_reagents():
    # Query the database for all reagents. Convert the data to a python list.
    result = db.session.execute(db.select(LabChem))
    reagents = result.scalars().all()
    return render_template("index.html", all_reagents=reagents)


# Add_new_chem() to create a new record
@app.route('/new_chem', methods=["GET", "POST"])
def add_new_chem():
    new_chem_form = NewChem()
    if new_chem_form.validate_on_submit():
        new_chem = LabChem(
            lab_id=new_chem_form.lab_id.data,
            cabinet_number=new_chem_form.cabinet_number.data,
            english_name=new_chem_form.english_name.data,
            polish_name=new_chem_form.polish_name.data,
            cas_number=new_chem_form.cas_number.data,
            producer=new_chem_form.producer.data,
            packaging_capacity=new_chem_form.packaging_capacity.data,
        )
        db.session.add(new_chem)
        db.session.commit()
        return redirect(url_for("get_all_reagents"))
    return render_template("add-record.html", form=new_chem_form)


# Edit_chem() to change an existing record
@app.route('/edit_chem/<int:lab_id>', methods=["GET", "POST"])
def edit_chem(lab_id):
    reagent = db.get_or_404(LabChem, lab_id)
    edit_form = NewChem(
        lab_id=reagent.lab_id,
        cabinet_number=reagent.cabinet_number,
        english_name=reagent.english_name,
        polish_name=reagent.polish_name,
        cas_number=reagent.cas_number,
        producer=reagent.producer,
        packaging_capacity=reagent.packaging_capacity,
    )
    if edit_form.validate_on_submit():
        reagent.lab_id = edit_form.lab_id.data
        reagent.cabinet_number = edit_form.cabinet_number.data
        reagent.english_name = edit_form.english_name.data
        reagent.packaging_capacity = edit_form.packaging_capacity.data
        reagent.producer = edit_form.producer.data
        reagent.cas_number = edit_form.cas_number.data
        reagent.packaging_capacity = edit_form.packaging_capacity.data
        db.session.commit()
        return redirect(url_for("get_all_reagents"))
    return render_template("add-record.html", form=edit_form, is_edit=True)


# Delete_chem() to remove a reagent from the database
@app.route("/delete/<lab_id>")
def delete_chem(lab_id):
    reagent_to_delete = db.get_or_404(LabChem, lab_id)
    db.session.delete(reagent_to_delete)
    db.session.commit()
    return redirect(url_for("get_all_reagents"))


if __name__ == "__main__":
    app.run(debug=True, port=5003)
