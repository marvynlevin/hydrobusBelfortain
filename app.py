from datetime import datetime

from flask import Flask, render_template, g, request, redirect, flash
import pymysql.cursors

import db
import requests

app = Flask(__name__)
app.secret_key = "e%3v*/=Nj8Zbzz=$bqr1DA$BM7V6/sgWiFD7/NUa6F$psx3wZC6zr~C8MxGAM)#F"

app.config['TEMPLATES_AUTO_RELOAD'] = True


def get_db():
    """
    Establish and return a connection to the MySQL database.
    This function uses the PyMySQL library to establish a connection,
    with connection parameters such as the host, user, password, and database specified.

    The connection uses the 'utf8mb4' charset and DictCursor for cursor-class, which returns rows
    from the database as dictionaries instead of tuples.

    If a connection (denoted as 'db') does not exist in the current application context (g), a new
    connection is established.

    Once established, the connection is saved in the application context to be reused
    on subsequent database queries in the same request.

    :return: The MySQL database connection
    """
    if 'db' not in g:
        g.db = pymysql.connect(
            host=db.HOST,
            user=db.USER,
            password=db.PASSWORD,
            database=db.DATABASE,
            port=db.PORT,
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )
    return g.db


@app.teardown_appcontext
def teardown_db(exception):
    db = g.pop('db', None)
    if db is not None:
        db.close()


@app.route('/')
def home():
    return render_template('layout.html')


@app.route('/reservoirs/show')
def show_reservoirs():
    cursor = get_db().cursor()
    cursor.execute(requests.GET_BUSES)
    buses = cursor.fetchall()

    cursor.execute(requests.GET_RESERVOIRS_INSIDE_BUSES)
    reservoirs_bus = cursor.fetchall()

    cursor.execute(requests.GET_RESERVOIRS_WITHOUT_BUS)
    reservoirs = cursor.fetchall()
    print(reservoirs)

    cursor.execute(requests.GET_RESERVOIRS_MODELS)
    modeles_reservoirs = cursor.fetchall()

    cursor.execute(requests.GET_RESERVOIRS_POSITION)
    positions = cursor.fetchall()

    return render_template(
        'reservoirs/show_reservoirs.html',
        buses=buses,
        reservoirs_bus=reservoirs_bus,
        reservoirs=reservoirs,
        modeles_reservoirs=modeles_reservoirs,
        positions=positions
    )


@app.route('/reservoirs/new', methods=["POST"])
def new_reservoir():
    cursor = get_db().cursor()

    # Retrieve form data
    id_bus = int(request.form['id_bus']) if 'id_bus' in request.form and request.form['id_bus'] != '' else None
    taille_reservoir = request.form['taille_reservoir']
    id_modele_reservoir = request.form['id_modele_reservoir']
    position_dans_bus = request.form['position_dans_bus'] if 'position_dans_bus' in request.form else None
    nb_cycles_reels = request.form['nb_cycles_reels']
    date_mise_service_str = request.form['date_mise_service']
    date_retrait_service_str = request.form['date_retrait_service'] if 'date_retrait_service' in request.form else None

    if date_mise_service_str:
        date_mise_service = datetime.strptime(date_mise_service_str, "%Y-%m-%d").date()
    else:
        date_mise_service = None

    if date_retrait_service_str:
        date_retrait_service = datetime.strptime(date_retrait_service_str, "%Y-%m-%d").date()
    else:
        date_retrait_service = None

    if date_mise_service is not None and date_retrait_service is not None and date_mise_service > date_retrait_service:
        flash("La date de mise en service doit être inférieure à la date de retrait.", "error")
        return redirect('/reservoirs/show')

    # Execute the SQL query
    cursor.execute(requests.INSERT_NEW_RESERVOIR, (
        id_bus,
        date_mise_service,
        None if date_retrait_service is None or date_retrait_service == '' else date_retrait_service,
        taille_reservoir,
        id_modele_reservoir,
        position_dans_bus,
        nb_cycles_reels
    ))

    # Commit the changes to the database
    get_db().commit()

    id_reservoir = cursor.lastrowid
    flash(f"L'ajout du Réservoir n°{id_reservoir} a été appliqué avec id_bus: {id_bus}, id_reservoir: {id_reservoir}, date_mise_service: {date_mise_service}, date_retrait_service: {date_retrait_service}, taille_reservoir: {taille_reservoir}, id_modele_reservoir: {id_modele_reservoir}, position_dans_bus: {position_dans_bus}, nb_cycles_reels: {nb_cycles_reels}.", "success")

    return redirect('/reservoirs/show')


@app.route('/reservoirs/delete', methods=["GET"])
def delete_reservoir():
    # Retrieve form data from request.args
    id_reservoir = request.args.get('id_reservoir')

    print(id_reservoir)

    cursor = get_db().cursor()
    # Delete associated controle records
    cursor.execute(requests.DELETE_CONTROLES, id_reservoir)
    # Delete the reservoir
    cursor.execute(requests.DELETE_RESERVOIR, id_reservoir)

    get_db().commit()

    flash(f"Le réservoir n°{id_reservoir} a été supprimé.", "success")

    return redirect('/reservoirs/show')


@app.route('/reservoirs/edit', methods=["POST"])
def edit_reservoir():
    cursor = get_db().cursor()

    # Retrieve form data
    id_bus = request.form['id_bus'] if 'id_bus' in request.form else None
    id_reservoir = request.form['id_reservoir']
    date_mise_service_str = request.form['date_service_' + id_reservoir]
    date_retrait_service_str = request.form['date_retrait_' + id_reservoir] if 'date_retrait_' + id_reservoir in request.form else None

    if date_mise_service_str:
        date_mise_service = datetime.strptime(date_mise_service_str, "%Y-%m-%d").date()
    else:
        date_mise_service = None

    if date_retrait_service_str:
        date_retrait_service = datetime.strptime(date_retrait_service_str, "%Y-%m-%d").date()
    else:
        date_retrait_service = None

    if date_mise_service is not None and date_retrait_service is not None and date_mise_service > date_retrait_service:
        flash("La date de mise en service doit être inférieure à la date de retrait.", "error")
        return redirect('/reservoirs/show')

    taille_reservoir = request.form['taille_reservoir_' + id_reservoir]
    id_modele_reservoir = request.form['modele_reservoir_' + id_reservoir]
    position_dans_bus = request.form['position_reservoir_' + id_reservoir] if 'position_reservoir_' + id_reservoir in request.form else None
    nb_cycles_reels = request.form['cycle_reel_' + id_reservoir]

    # Edit in the database
    cursor.execute(requests.EDIT_RESERVOIR, (
        None if id_bus is None or id_bus == '' else id_bus,
        date_mise_service,
        None if date_retrait_service is None or date_retrait_service == '' else date_retrait_service,
        taille_reservoir,
        id_modele_reservoir,
        position_dans_bus,
        nb_cycles_reels,
        id_reservoir
    ))

    flash(f"Le réservoir a bien été modifié avec id_bus: {id_bus}, id_reservoir: {id_reservoir}, date_mise_service: {date_mise_service}, date_retrait_service: {date_retrait_service}, taille_reservoir: {taille_reservoir}, id_modele_reservoir: {id_modele_reservoir}, position_dans_bus: {position_dans_bus}, nb_cycles_reels: {nb_cycles_reels}.", "success")

    get_db().commit()

    return redirect('/reservoirs/show')


@app.route('/reservoirs/etat', methods=["GET"])
def etat_reservoirs():
    filter_word = request.args.get("filter_word")
    date_mise_service_str = request.args.get("date_mise_service")
    date_retrait_service_str = request.args.get("date_retrait_service")

    if date_mise_service_str:
        date_mise_service = datetime.strptime(date_mise_service_str, "%Y-%m-%d").date()
    else:
        date_mise_service = None

    if date_retrait_service_str:
        date_retrait_service = datetime.strptime(date_retrait_service_str, "%Y-%m-%d").date()
    else:
        date_retrait_service = None

    if date_mise_service is not None and date_retrait_service is not None and date_mise_service > date_retrait_service:
        flash("La date de mise en service doit être inférieure à la date de retrait.", "error")
        return redirect('/reservoirs/etat')

    taille_reservoir_min = request.args.get("taille_reservoir_min")
    taille_reservoir_max = request.args.get("taille_reservoir_max")

    if taille_reservoir_min and taille_reservoir_max and int(taille_reservoir_min) > int(taille_reservoir_max):
        flash("La taille minimale du réservoir doit être inférieure à la taille maximale.", "error")
        return redirect('/reservoirs/etat')

    modele_filter = request.args.get("modele_filter") or None
    position_filter = request.args.get("position_filter") or None

    cycle_reel_min = request.args.get("cycle_reel_min")
    cycle_reel_max = request.args.get("cycle_reel_max")

    if cycle_reel_min and cycle_reel_max and int(cycle_reel_min) > int(cycle_reel_max):
        flash("Le cycle réel minimum doit être inférieur au cycle réel maximum.", "error")
        return redirect('/reservoirs/etat')

    cursor = get_db().cursor()
    cursor.execute(
        requests.GET_RESERVOIRS_FILTER,
        (
            f"%{filter_word}%" if filter_word is not None else "%",
            date_mise_service or "1090-01-01",
            date_retrait_service or "3000-01-01",
            modele_filter,
            position_filter,
            f"%{filter_word}%" if filter_word is not None else "%",
            int(taille_reservoir_min) if taille_reservoir_min else 0,
            int(taille_reservoir_max) if taille_reservoir_max else 100,
            int(cycle_reel_min) if cycle_reel_min else 0,
            int(cycle_reel_max) if cycle_reel_max else 100000
        )
    )
    all_reservoirs = cursor.fetchall()
    print(all_reservoirs)

    cursor.execute(requests.GET_BUSES)
    buses = cursor.fetchall()

    cursor.execute(requests.GET_RESERVOIRS_MODELS)
    modeles_reservoirs = cursor.fetchall()

    cursor.execute(requests.GET_RESERVOIRS_POSITION)
    positions = cursor.fetchall()

    if any([filter_word, date_mise_service_str, date_retrait_service_str, taille_reservoir_min, taille_reservoir_max,
            modele_filter, position_filter, cycle_reel_min, cycle_reel_max]):
        flash(f"La requête a été prise en compte.", "success")

    return render_template(
        'reservoirs/etat_reservoirs.html',
        buses=buses,
        all_reservoirs=all_reservoirs,
        modeles_reservoirs=modeles_reservoirs,
        positions=positions,
        # Filter
        filter_word=filter_word or "",
        date_mise_service=date_mise_service or '',
        date_retrait_service=date_retrait_service or '',
        taille_reservoir_min=taille_reservoir_min or '',
        taille_reservoir_max=taille_reservoir_max or '',
        modele_filter=modele_filter or '',
        position_filter=position_filter or '',
        cycle_reel_min=cycle_reel_min or '',
        cycle_reel_max=cycle_reel_max or ''
    )


@app.route('/flottes_bus/show')
def show_flottes_bus():
    cursor = get_db().cursor()
    cursor.execute(requests.GET_BUSES_INSIDE_FLEETS)
    buses = cursor.fetchall()

    cursor.execute(requests.GET_FLEETS)
    fleets = cursor.fetchall()

    cursor.execute(requests.GET_BUS_MODELS)
    bus_models = cursor.fetchall()

    prepared_fleets = []
    for fleet in fleets:
        fleet_buses = []
        for bus in buses:
            if bus["id_flotte"] == fleet["id_flotte"]:
                fleet_buses.append(bus)
        prepared_fleets.append({
            "id_flotte": fleet["id_flotte"],
            "nom_flotte": fleet["nom_flotte"],
            "buses": fleet_buses
        })

    return render_template(
        'bus/show_flottes_bus.html',
        flottes=prepared_fleets,
        bus_models=bus_models,
        add_nom_bus=request.args.get("nom_bus", ''),
        add_date_service=request.args.get("date_service", ''),
        add_id_flotte=request.args.get("nom_bus", ''),
    )


@app.route('/flottes_bus/bus/new', methods=["POST"])
def create_bus():
    nom_bus = request.form.get("nom_bus", "")
    if len(nom_bus) < 1:
        flash("Le nom du bus doit être précisé", "error")
        return redirect('/flottes_bus/show')

    date_achat = request.form.get("date_service", "")
    try:
        datetime.strptime(date_achat, '%Y-%m-%d')
    except ValueError:
        flash("La date de service n'est pas en format correct, elle doit être au format YYYY-MM-DD", "error")
        return redirect(f'/flottes_bus/show?nom_bus={nom_bus}')

    id_flotte = int(request.form.get("id_flotte", -1))
    if id_flotte < 0:
        flash("La flotte n'existe pas. Veillez à sélectionner une flotte", "error")
        return redirect(f'/flottes_bus/show?nom_bus={nom_bus}&date_service={date_achat}')

    id_modele_bus = int(request.form.get("id_modele_bus", -1))

    if id_modele_bus < 0:
        flash("Le modèle de bus n'existe pas. Veillez à sélectionner un modèle de bus", "error")
        return redirect(f'/flottes_bus/show?nom_bus={nom_bus}&date_service={date_achat}&id_flotte={id_flotte}')

    # Add to database
    cursor = get_db().cursor()
    cursor.execute(requests.INSERT_NEW_BUS, (nom_bus, date_achat, id_flotte, id_modele_bus))

    get_db().commit()

    flash(f"L'ajout du bus '{nom_bus}' a été appliqué.", "success")

    return redirect('/flottes_bus/show')


@app.route('/flottes_bus/bus/delete', methods=["GET"])
def delete_bus():
    id_bus = request.args.get("id_bus_delete", -1)

    print(id_bus)

    cursor = get_db().cursor()
    # Get bus name
    cursor.execute(requests.GET_BUS_NAME, id_bus)
    bus_name = cursor.fetchone() or {"nom_bus": f"ID({id_bus})"}

    # Delete from database
    try:
        cursor.execute(requests.DELETE_BUS, id_bus)
        get_db().commit()

        flash(f"Le bus {bus_name['nom_bus']} a été supprimé.", "success")

        return redirect('/flottes_bus/show')
    except pymysql.err.IntegrityError:
        flash(f"Le bus {bus_name['nom_bus']} ne peut pas être supprimé.\nVeillez à supprimer ou dé-lier tout réservoir associé à ce bus.", "error")

        return redirect('/flottes_bus/show')


@app.route('/flottes_bus/bus/edit', methods=["POST"])
def edit_bus():
    id_bus = request.form.get("id_bus", -1)

    id_flotte = int(request.form.get("id_flotte", -1))

    if id_flotte < 0:
        flash("La flotte n'existe pas. Veillez à sélectionner une flotte", "error")
        return redirect('/flottes_bus/show')

    id_modele_bus = int(request.form.get("id_modele_bus", -1))

    if id_modele_bus < 0:
        flash("Le modèle de bus n'existe pas. Veillez à sélectionner un modèle de bus", "error")
        return redirect('/flottes_bus/show')

    date_service = request.form.get("date_service", "")

    try:
        datetime.strptime(date_service, '%Y-%m-%d')
    except ValueError:
        flash("La date de service n'est pas en format correct, elle doit être au format YYYY-MM-DD", "error")
        return redirect('/flottes_bus/show')

    nom_bus = request.form.get("nom_bus", "")

    if len(nom_bus) < 1:
        flash("Le nom du bus doit être précisé", "error")
        return redirect('/flottes_bus/show')

    # Edit in the database
    cursor = get_db().cursor()
    cursor.execute(requests.EDIT_BUS, (nom_bus, date_service, id_flotte, id_modele_bus, id_bus))
    get_db().commit()

    flash(f"Les modifications du bus {nom_bus} ont été effectuées.", "success")

    return redirect('/flottes_bus/show')


@app.route('/flottes_bus/etat')
def etat_flottes_bus():
    filter_word = request.args.get("filter_word")

    date_achat_min = request.args.get("date_achat_min")
    date_achat_max = request.args.get("date_achat_max")

    distance_totale_min = request.args.get("distance_totale_min")
    distance_totale_max = request.args.get("distance_totale_max")

    bus_model = request.args.get("modele_bus") or None
    flotte = request.args.get("flotte") or None

    conso_mensuelle_min = request.args.get("conso_mensuelle_min")
    conso_mensuelle_max = request.args.get("conso_mensuelle_max")

    cursor = get_db().cursor()
    cursor.execute(
        requests.GET_BUSES_STATE,
        (
            f"%{filter_word}%" if filter_word is not None else "%",
            date_achat_min or "1990-01-01",
            date_achat_max or "3000-01-01",
            bus_model,
            flotte,
            int(distance_totale_min) if distance_totale_min else 0,
            int(distance_totale_max) if distance_totale_max else 200000000000,
            int(conso_mensuelle_min) if conso_mensuelle_min else 0,
            int(conso_mensuelle_max) if conso_mensuelle_max else 200000000000
        )
    )
    buses = cursor.fetchall()

    cursor.execute(requests.GET_FLEETS)
    fleets = cursor.fetchall()

    cursor.execute(requests.GET_BUS_MODELS)
    bus_models = cursor.fetchall()

    return render_template(
        'bus/etat_bus.html',
        buses=buses,
        bus_models=bus_models,
        flottes=fleets,
        # Filter
        filter_word=filter_word or "",
        date_achat_min=date_achat_min or '',
        date_achat_max=date_achat_max or '',
        bus_model=bus_model or '',
        flotte_filter=flotte or '',
        distance_totale_min=distance_totale_min or '',
        distance_totale_max=distance_totale_max or '',
        conso_mensuelle_min=conso_mensuelle_min or '',
        conso_mensuelle_max=conso_mensuelle_max or ''
    )


@app.route('/controles/show')
def show_controles():
    cursor = get_db().cursor()
    cursor.execute(requests.GET_CONTROLE)
    controles = cursor.fetchall()

    cursor.execute(requests.GET_RESERVOIRS_MODELS)
    modeles_reservoirs = cursor.fetchall()

    return render_template('controles/show_controles.html',
                           controles = controles,
                           modeles_reservoirs = modeles_reservoirs)

@app.route('/controles/new', methods=['POST'])
def new_controle():
    cursor = get_db().cursor()

    # Retrieve form data
    date_controle = request.form['date_controle_2']
    description = request.form['description_2'] if 'description_2' in request.form else None
    id_modele_reservoir = request.form['id_modele_reservoir']
    prix = request.form['prix_controle_2']

    cursor.execute(requests.INSERT_NEW_CONTROLE, (
        date_controle,
        description,
        id_modele_reservoir,
        prix
    ))

    # Commit the changes to the database
    get_db().commit()

    id_controle = cursor.lastrowid
    flash(f"L'ajout du controle n°{id_controle} a été appliqué.", "success")

    return redirect('/controles/show')


@app.route('/controles/delete', methods=["GET"])
def delete_controle():
    # Retrieve form data from request.args
    id_controle = request.args.get('id_controle')

    print(id_controle)

    cursor = get_db().cursor()
    # Delete the control
    cursor.execute(requests.DELETE_CONTROLE, (id_controle,))

    get_db().commit()

    flash(f"Le controle n°{id_controle} a été supprimé.", "success")

    print(f"Avant la redirection : {id_controle}")
    return redirect('/controles/show')

@app.route('/controles/edit', methods=["POST"])
def edit_controles():
    # Retrieve form data
    id_controle = int(request.form.get('id_controle',''))
    date_controle = request.form.get('date_controle-2','')
    description = request.form.get('description_2','')
    id_modele_reservoir = int(request.form.get('id_modele_reservoir',''))
    prix = float(request.form.get('prix_controle_2',''))

    cursor = get_db().cursor()

    # Edit in the database
    cursor.execute(requests.EDIT_CONTROLE, (
        date_controle,
        description,
        id_modele_reservoir,
        prix,
        id_controle
    ))

    flash(f"Le contrôle n°{id_controle} a bien été modifié avec date: {date_controle}, description: {description}, id_modele_reservoir: {id_modele_reservoir}, prix: {prix}",
        "success")

    get_db().commit()

    return redirect('/controles/show')

@app.route('/controles/etat')
def etat_controles():
    filter_id = request.args.get("numero_controle")

    filter_date_min_str = request.args.get("filter_date_min")
    filter_date_max_str = request.args.get("filter_date_max")

    if filter_date_min_str:
        filter_date_min = datetime.strptime(filter_date_min_str, "%Y-%m-%d").date()
    else:
        filter_date_min = None

    if filter_date_max_str:
        filter_date_max = datetime.strptime(filter_date_max_str, "%Y-%m-%d").date()
    else:
        filter_date_max = None

    if filter_date_min is not None and filter_date_max is not None and filter_date_min > filter_date_max:
        flash("La date minimum en service doit être inférieure à la date de maximum.", "error")
        return redirect('/controles/etat')

    prix_min = request.args.get("prix_controle_min ")
    prix_max = request.args.get("prix_controle_max")

    modele_reservoir = request.args.get("modele_reservoir")
    print(filter_id)
    cursor = get_db().cursor()
    cursor.execute(requests.GET_CONTROLE_FILTER,
                   (filter_id,
                    filter_date_min,
                    filter_date_max,
                    modele_reservoir,
                    prix_min,
                    prix_max))

    cursor.execute(requests.GET_CONTROLE)
    controles = cursor.fetchall()

    cursor.execute(requests.GET_RESERVOIRS_MODELS)
    modeles_reservoirs = cursor.fetchall()



    if any([filter_id, filter_date_min, filter_date_max, prix_min, prix_max]):
        flash(f"La requête a été prise en compte.", "success")


    return render_template('controles/etat_controles.html',
                           controles = controles,
                           modeles_reservoirs = modeles_reservoirs,
                           filter_id = filter_id or '',
                           filter_date_min = filter_date_min or '',
                           filter_date_max = filter_date_max or '',
                           prix_min = prix_min or '',
                           prix_max = prix_max or '',
                           modele_reservoir = modele_reservoir or '')


@app.route('/consommation/show', methods=["GET"])
def show_consommation():
    cursor = get_db().cursor()
    cursor.execute(requests.GET_CONSOMMATION)
    consommations = cursor.fetchall()

    print("consommation")

    return render_template('/consommation/show_consommation.html', consommations=consommations)


@app.route('/consommation/etat', methods=["GET"])
def etat_consommation():
    return render_template('/consommation/etat_consommation.html')


@app.route('/consommation/new', methods=['POST'])
def new_consommation():
    cursor = get_db().cursor()

    # Retrieve form data
    date_consommation = request.form['date_consommation_2']
    consommation_hydrogene = request.form['qt_hydrogène_2'] if 'qt_hydrogène_2' in request.form else None
    kilometres_parcourus = request.form['distance_conso_2']
    id_bus = request.form['nom_bus']

    cursor.execute(requests.INSERT_NEW_CONSOMMATION, (
        date_consommation,
        consommation_hydrogene,
        kilometres_parcourus,
        id_bus
    ))

    # Commit the changes to the database
    get_db().commit()

    id_consommation = cursor.lastrowid
    flash(f"L'ajout de la consommation n°{id_consommation} a été appliqué.", "success")

    return redirect('/consommation/show')


@app.route('/consommation/delete', methods=["GET"])
def delete_consommation():
    # Retrieve form data from request.args
    id_consommation = request.args.get('id_consommation')

    cursor = get_db().cursor()
    # Delete the control
    cursor.execute(requests.DELETE_CONSOMMATIONS, (id_consommation,))

    get_db().commit()

    flash(f"La consommation n°{id_consommation} a été supprimé.", "success")

    print(f"Avant la redirection : {id_consommation}")
    return redirect('/consommation/show')

@app.route('/consommation/edit', methods=["POST"])
def edit_consommation():
    id_consommation = request.args.get('id_consommation')
    print(id_consommation)

    cursor = get_db().cursor()

    # Retrieve form data
    date_consommation = request.form['date_consommation_2'+id_consommation]
    consommation_hydrogene = request.form['qt_hydrogène_2'+id_consommation if 'qt_hydrogène_2' in request.form else None]
    kilometres_parcourus = request.form['distance_conso_2'+id_consommation]
    id_bus = request.form['id_bus'+id_consommation]

    # Edit in the database
    cursor.execute(requests.EDIT_CONTROLE, (
        date_consommation,
        consommation_hydrogene,
        kilometres_parcourus,
        id_bus,
        id_consommation
    ))

    flash(f"La consommation n°{id_consommation} a bien été modifié avec date: {date_consommation}, qt_hydrogène: {consommation_hydrogene}, distance_conso: {kilometres_parcourus}, nom_bus: {id_bus}", "success")

    get_db().commit()

    return redirect('/consommation/show')




if __name__ == '__main__':
    app.run()
