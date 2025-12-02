from flask import Flask, render_template, request, redirect, session, url_for, flash
import requests
import json
import os

app = Flask(__name__)
app.secret_key = 'melyyyyaaasdwwd'

API_KEY = '923b514b2c604404954302eaebfea6fd'
API_URL = 'https://api.spoonacular.com/recipes/findByIngredients'

def recetas_por_ingredientes(ingredientes):
    params = {
        "apiKey": API_KEY,
        "ingredients": ingredientes,  
        "number": 15,
        "ranking": 1,                
        "ignorePantry": True   
    }      

    respuesta = requests.get(API_URL, params=params)

    if respuesta.status_code != 200:
        return []

    return respuesta.json()  

 

USUARIOS_FILE = "usuarios.json"

if os.path.exists(USUARIOS_FILE):
    with open(USUARIOS_FILE, "r") as archivo:
        usuarios = json.load(archivo)
else:
    usuarios = {}



@app.route('/', methods=['GET', 'POST'])
def inicio():
    nombre = session.get("nombre")
    return render_template('inicio.html', nombre=nombre)


@app.route('/registro', methods=['GET', 'POST'])
def registro():
    if request.method == 'POST':

    
        nombre = request.form.get('nombre')
        apellido = request.form.get('apeido')  
        dia = request.form.get('dia')
        mes = request.form.get('mes')
        anio = request.form.get('anio')
        genero = request.form.get('genero')
        email = request.form.get('exampleInputEmail1')  
        password = request.form.get('exampleInputPassword1') 
        actividad = request.form.get('nivelactividad')
        peso = request.form.get('peso')
        altura = request.form.get('altura')

        if email in usuarios:
            flash("El correo ya está registrado. Intenta iniciar sesión.")
            return redirect('/iniciar_sesion')

        usuarios[email] = {
            "nombre": nombre,
            "apellido": apellido,
            "fecha": f"{dia}/{mes}/{anio}",
            "genero": genero,
            "password": password,
            "actividad": actividad,
            "peso": peso,
            "altura": altura
        }

    
        with open(USUARIOS_FILE, "w") as archivo:
            json.dump(usuarios, archivo, indent=4)

        session["usuario"] = email
        session["nombre"] = nombre
        session['genero'] = genero
        session['actividad'] = actividad
        session['peso'] = peso
        session['altura'] = altura

        flash(f"Registro exitoso. ¡Bienvenido {nombre}!")
        return redirect("/")

    return render_template("formulario.html")


@app.route('/iniciar_sesion')
def iniciar_sesion():
    return render_template("iniciar_sesion.html")

@app.route('/educacion')
def educacion():
    return render_template("educacion.html")


@app.route('/descargables')
def descargables():
    if "usuario" not in session:
        flash("Debes iniciar sesión primero.")
        return redirect("/iniciar_sesion")

    return render_template("descargables.html")





@app.route('/login', methods=['POST'])
def login():


    email = request.form.get("email")
    password = request.form.get("password")

    if email not in usuarios:
        flash("El usuario no existe.")
        return redirect("/iniciar_sesion")

    if usuarios[email]["password"] != password:
        flash("Contraseña incorrecta.")
        return redirect("/iniciar_sesion")

    session["usuario"] = email
    session["nombre"] = usuarios[email]["nombre"]

    flash("Inicio de sesión exitoso.")
    return redirect("/perfil")


@app.route('/perfil')
def perfil():
    if "usuario" not in session:
        flash("Debes iniciar sesión primero.")
        return redirect("/iniciar_sesion")

    usuario = usuarios[session["usuario"]]
    return render_template("perfil.html", usuario=usuario)


@app.route('/logout')
def logout():
    session.clear()
    flash("Has cerrado sesión correctamente.")
    return redirect("/")

@app.route('/resultado', methods=['GET','POST'])
def resultado():
    return render_template("resultado.html")

@app.route('/buscar', methods=['GET','POST'])
def buscar():
    if "usuario" not in session:
        flash("Debes iniciar sesión primero.")
        return redirect("/iniciar_sesion")
    return render_template("buscar.html")



@app.route('/buscador', methods=['GET'])
def buscar_ingredientes():
    
    ingredientes = request.args.get("ingredientes", "")
    if ingredientes.strip() == "":
        return render_template("buscar.html", error="Escribe uno o más ingredientes.")

    recetas = recetas_por_ingredientes(ingredientes)

    return render_template("resultado.html",recetas=recetas,ingredientes=ingredientes)









@app.route('/calcular', methods=['GET', 'POST'])
def calcular():


    if request.method == 'GET':
        return render_template("imc.html")

    try:
        peso = float(request.form['peso'])
        altura = float(request.form['altura']) / 100
        imc = round(peso / (altura ** 2), 2)

        if imc < 18.5:
            clas = "Bajo peso"
        elif imc < 25:
            clas = "Normal"
        elif imc < 30:
            clas = "Sobrepeso"
        else:
            clas = "Obesidad"

        return render_template('imc.html', imc=imc, clasificacion=clas)

    except:
        flash("Error: revisa los datos ingresados.", "error")
        return redirect("/calcular")
    

@app.route('/tmb', methods=['GET', 'POST'])
def tmb():
    if request.method == "GET":
        return render_template("tmb.html")

    try:
        sexo = request.form.get("sexo")
        edad = int(request.form.get("edad"))
        peso = float(request.form.get("peso"))
        altura = float(request.form.get("altura"))

        if sexo == "hombre":
            tmb = 88.36 + (13.4 * peso) + (4.8 * altura) - (5.7 * edad)
        else:
            tmb = 447.6 + (9.2 * peso) + (3.1 * altura) - (4.3 * edad)

        tmb = round(tmb, 2)

        return render_template("tmb.html", tmb=tmb)

    except:
        return "Error: revisa los datos ingresados."
    




@app.route('/macronutrientes', methods=['POST', 'GET'])
def macro():
    if request.method == 'POST':
        calorias = float(request.form['calorias'])

    
        p_prot = 0.30
        p_carb = 0.40
        p_grasa = 0.30

        proteina = round((calorias * p_prot) / 4, 2)
        carbos = round((calorias * p_carb) / 4, 2)
        grasas = round((calorias * p_grasa) / 9, 2)

        return render_template(
            'macronutrientes.html',
            calorias=calorias,
            proteina=proteina,
            carbos=carbos,
            grasas=grasas
        )
    if "usuario" not in session:
        flash("Debes iniciar sesión primero.")
        return redirect("/iniciar_sesion")

    return render_template('macronutrientes.html')

    


@app.route('/peso_ideal', methods=['POST', 'GET'])
def peso_ideal():
    if request.method == 'GET':
        return render_template('psoideal.html')

    try:
        altura = float(request.form['altura'])
        sexo = request.form['sexo']

        if altura <= 0:
            flash("La altura debe ser un número positivo.")
            return redirect(url_for('peso_ideal'))


        if sexo == 'hombre':
            peso_ideal = 50 + 2.3 * ((altura - 152) / 2.54)
        elif sexo == 'mujer':
            peso_ideal = 45.5 + 2.3 * ((altura - 152) / 2.54)
        else:
            flash("Selecciona un sexo válido.")
            return redirect(url_for('peso_ideal'))

        peso_ideal = round(peso_ideal, 2)

        return render_template('psoideal.html', resultado=peso_ideal)

    except ValueError:
        flash("Ingresa valores numéricos válidos.")
        return redirect(url_for('peso_ideal'))


@app.route('/gct', methods=['POST', 'GET'])
def gct():
    if request.method == 'POST':
        tmb = float(request.form['tmb'])  
        actividad = float(request.form['actividad'])

        gct = round(tmb * actividad, 2)

        return render_template('gct.html', gct=gct, tmb=tmb)

    return render_template('gct.html')



    


if __name__ == '__main__':
    app.run(debug=True)