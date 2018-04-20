from builtins import print

from MySQLdb.constants.ER import TRANS_CACHE_FULL
from flask import Flask, render_template, url_for, flash, request, redirect, session
from functools import wraps

from dbconnect import connection
from passlib.hash import sha256_crypt
from MySQLdb import escape_string
import gc, os
import cv2
from PIL import Image
import numpy as np
import scipy.misc

APP_ROOT = os.path.dirname(os.path.abspath(__file__))

app = Flask(__name__)
app.config['SECRET_KEY'] = 'dfgbsry%$#W^B$#Vre'


def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash('Você precisa logar primeiro.')
            return redirect(url_for('login'))

    return wrap


@app.route('/login', methods=['GET', 'POST'])
def login():
    try:
        if 'logged_in' in session:
            return redirect(url_for('home'))
        if request.method == 'POST':
            c, conn = connection()
            query = c.execute("SELECT * FROM usuario WHERE login = '{}'".format(request.form['usuario']))
            senha = str(c.fetchone()[2])
            query2 = c.execute("SELECT * FROM usuario WHERE login = '{}'".format(request.form['usuario']))
            id_usuario = str(c.fetchone()[0])
            if sha256_crypt.verify(request.form['senha'], senha):
                session['logged_in'] = True
                session['usuario'] = request.form['usuario'];
                session['id_usuario'] = id_usuario
                flash('Logado com sucesso')
                return redirect(url_for('home'))
            else:
                flash('Credenciais inválidas, tente novamente.')

            c.close()
            conn.close()
            gc.collect()

    except Exception as e:
        c.close()
        conn.close()
        gc.collect()
        flash(str(e))
    return render_template('login.html')


@app.route('/register/', methods=['GET', 'POST'])
def register():
    if 'logged_in' in session:
        return redirect(url_for('home'))

    if request.method == 'POST':
        images = []
        labels = []
        x = 1
        for file in request.files.getlist('imagens'):
            cascade_path = "haarcascade_frontalface_default.xml"
            face_cascade = cv2.CascadeClassifier(cascade_path)
            image_pil = Image.open(file).convert('L')
            image = np.array(image_pil, 'uint8')
            faces = face_cascade.detectMultiScale(image)
            filename = file.filename
            label = x
            x = x + 1
            for (x, y, w, h) in faces:
                img = Image.fromarray(image[y: y + h, x: x + w])
                print(img)
                size = (100, 100)
                img.thumbnail(size)
                # img.resize(size, Image.ANTIALIAS)
                print(img)
                img = np.array(img)
                print(img)
                images.append(img)
                # images.append(image[y: y + h, x: x + w])
                labels.append(label)
                # salva imagen
                face = image[y: y + h, x: x + w]
                scipy.misc.imsave('images/' + filename, face)
        recognizer = cv2.face.FisherFaceRecognizer_create()
        recognizer.train(images, np.array(labels))
        recognizer.save('trainer/trainer.yml')

        usuario = request.form['usuario']
        senha = sha256_crypt.encrypt(str(request.form['senha']))
        email = request.form['email']
        c, conn = connection()
        x = c.execute("SELECT * FROM usuario WHERE login = '{}'".format(usuario))

        if int(x) > 0:
            flash("Usuário ja existe")
            return render_template('register.html')
        else:
            c.execute("INSERT INTO usuario (login, senha, email) VALUES ('{}','{}','{}')".format(usuario, senha, email))
            conn.commit()
            flash("Obrigado por se registrar")
            c.close()
            conn.close()
            gc.collect()
            session['logged_in'] = True
            session['usuario'] = usuario
            return redirect(url_for('home'))

    return render_template('register.html')


@app.route('/')
@login_required
def home():
    c, conn = connection()
    query = c.execute("SELECT * FROM senha WHERE id_usuario = '{}'".format(session['id_usuario']))
    usuarios = c.fetchall()

    c.close()
    conn.close()
    gc.collect()

    return render_template('home.html', usuarios = usuarios)


@app.route('/logout/')
@login_required
def logout():
    session.clear()
    flash('Você foi deslogado')
    gc.collect()
    return redirect(url_for('login'))


if __name__ == '__main__':
    app.run()
