#
#
#      BUS & FLOTTES
#
#


# SHOW BUS AND FLEETS
GET_BUSES_INSIDE_FLEETS = """SELECT
    Bus.id_flotte,
    Bus.id_bus,
    Bus.id_modele_bus,
    Bus.nom_bus,
    Bus.date_achat_bus,
    SUM(COALESCE(C.kilometres_parcourus, 0)) AS distance_totale,
    AVG(COALESCE(C.kilometres_parcourus, 0)) AS distance_mensuelle,
    SUM(COALESCE(C.consommation_hydrogene, 0)) AS conso_totale,
    AVG(COALESCE(C.consommation_hydrogene, 0)) AS conso_moyenne,
    COUNT(C.id_date) AS nombre_pleins
FROM Bus
LEFT JOIN Consomme C ON C.id_bus = Bus.id_bus
GROUP BY Bus.id_bus;"""

GET_FLEETS = """SELECT id_flotte, nom_flotte FROM Flotte;"""
GET_BUS_MODELS = """SELECT id_modele_bus, nom_modele_bus, nb_places_bus FROM Modele_bus;"""

# INSERT & DELETE & EDIT FLEETS AND BUS
INSERT_NEW_BUS = """INSERT INTO Bus (nom_bus, date_achat_bus, id_flotte, id_modele_bus) VALUE (%s, %s, %s, %s);"""
DELETE_BUS = """DELETE FROM Bus WHERE id_bus = %s;"""

GET_BUS_NAME = """SELECT nom_bus FROM Bus WHERE id_bus = %s;"""

EDIT_BUS = """UPDATE Bus
SET
    nom_bus = %s,
    date_achat_bus = %s,
    id_flotte = %s,
    id_modele_bus = %s
WHERE
    id_bus = %s;"""

# FILTER BUSES
GET_BUSES_STATE = """SELECT
    Bus.id_flotte,
    Bus.id_bus,
    Bus.id_modele_bus,
    Bus.nom_bus,
    Bus.date_achat_bus,
    SUM(COALESCE(C.kilometres_parcourus, 0)) AS distance_totale,
    AVG(COALESCE(C.kilometres_parcourus, 0)) AS distance_mensuelle,
    SUM(COALESCE(C.consommation_hydrogene, 0)) AS conso_totale,
    AVG(COALESCE(C.consommation_hydrogene, 0)) AS conso_moyenne,
    COUNT(C.id_date) AS nombre_pleins
FROM Bus
LEFT JOIN Consomme C ON C.id_bus = Bus.id_bus
WHERE
    (Bus.nom_bus LIKE %s)
    AND (Bus.date_achat_bus BETWEEN %s AND %s)
    AND Bus.id_modele_bus = IFNULL(%s, Bus.id_modele_bus)
    AND Bus.id_flotte = IFNULL(%s, Bus.id_flotte)
GROUP BY
    Bus.id_bus
HAVING
    (
        SUM(COALESCE(C.kilometres_parcourus, 0)) >= %s
        AND SUM(COALESCE(C.kilometres_parcourus, 0)) <= %s
    ) AND (
        AVG(COALESCE(C.consommation_hydrogene, 0)) >= %s
        AND AVG(COALESCE(C.consommation_hydrogene, 0)) <= %s
    );"""

#
#
#      RESERVOIRS
#
#

# SHOW RESERVOIRS
GET_BUSES = """SELECT Bus.id_bus, Bus.nom_bus FROM Bus;"""

GET_RESERVOIRS_INSIDE_BUSES = """SELECT
    Reservoir.id_reservoir,
    Reservoir.id_bus,
    Reservoir.id_modele_reservoir,
    Reservoir.taille_reservoir,
    Reservoir.position_dans_bus,
    Reservoir.date_mise_service,
    Reservoir.date_retrait_service,
    Reservoir.nb_cycles_reels,
    COUNT(C.id_controle) AS nb_controle,
    M.modele_reservoir
FROM Reservoir
LEFT JOIN Controle AS C ON C.id_reservoir = Reservoir.id_reservoir
LEFT JOIN Modele_reservoir AS M ON M.id_modele_reservoir = Reservoir.id_modele_reservoir
WHERE Reservoir.id_bus IS NOT NULL
GROUP BY
    Reservoir.id_reservoir,
    Reservoir.id_bus,
    Reservoir.id_modele_reservoir,
    Reservoir.taille_reservoir,
    Reservoir.position_dans_bus,
    Reservoir.date_mise_service,
    Reservoir.date_retrait_service,
    Reservoir.nb_cycles_reels,
    M.modele_reservoir;
"""

GET_RESERVOIRS_WITHOUT_BUS = """SELECT
    Reservoir.id_reservoir,
    Reservoir.id_bus,
    Reservoir.id_modele_reservoir,
    Reservoir.taille_reservoir,
    Reservoir.position_dans_bus,
    Reservoir.date_mise_service,
    Reservoir.date_retrait_service,
    Reservoir.nb_cycles_reels,
    COUNT(C.id_controle) AS nb_controle,
    M.modele_reservoir
FROM Reservoir
LEFT JOIN Controle AS C ON C.id_reservoir = Reservoir.id_reservoir
LEFT JOIN Modele_reservoir AS M ON M.id_modele_reservoir = Reservoir.id_modele_reservoir
WHERE Reservoir.id_bus IS NULL
GROUP BY
    Reservoir.id_reservoir,
    Reservoir.id_bus,
    Reservoir.id_modele_reservoir,
    Reservoir.taille_reservoir,
    Reservoir.position_dans_bus,
    Reservoir.date_mise_service,
    Reservoir.date_retrait_service,
    Reservoir.nb_cycles_reels,
    M.modele_reservoir;"""

GET_RESERVOIRS_MODELS = """SELECT
    Modele_reservoir.id_modele_reservoir,
    Modele_reservoir.modele_reservoir
FROM Modele_reservoir;"""

GET_RESERVOIRS_POSITION = """SELECT
    Reservoir.position_dans_bus
FROM Reservoir;"""

# NEW & DELETE & EDIT RESERVOIRS
INSERT_NEW_RESERVOIR = """INSERT INTO Reservoir (
    id_bus,
    date_mise_service,
    date_retrait_service,
    taille_reservoir,
    id_modele_reservoir,
    position_dans_bus,
    nb_cycles_reels)
VALUE (%s, %s, %s, %s, %s, %s, %s);"""

DELETE_RESERVOIR = """DELETE FROM Reservoir WHERE id_reservoir = %s;"""
DELETE_CONTROLES = """DELETE FROM Controle WHERE id_reservoir = %s;""" # CLE ETRANGERE

EDIT_RESERVOIR = """UPDATE Reservoir
SET
    id_bus = %s,
    date_mise_service = %s,
    date_retrait_service = %s,
    taille_reservoir = %s,
    id_modele_reservoir = %s,
    position_dans_bus = %s,
    nb_cycles_reels = %s
WHERE
    id_reservoir = %s;"""

# FILTER RESERVOIRS
GET_RESERVOIRS_FILTER = """SELECT
    Reservoir.id_reservoir,
    Reservoir.id_bus,
    Reservoir.id_modele_reservoir,
    Reservoir.taille_reservoir,
    Reservoir.position_dans_bus,
    Reservoir.date_mise_service,
    Reservoir.date_retrait_service,
    Reservoir.nb_cycles_reels,
    COUNT(C.id_controle) AS nb_controle,
    M.modele_reservoir
FROM Reservoir
LEFT JOIN Controle AS C ON C.id_reservoir = Reservoir.id_reservoir
LEFT JOIN Modele_reservoir AS M ON M.id_modele_reservoir = Reservoir.id_modele_reservoir
WHERE
    (Reservoir.id_reservoir LIKE %s)
    AND (Reservoir.date_mise_service BETWEEN %s AND %s)
    AND Reservoir.id_modele_reservoir = IFNULL(%s, Reservoir.id_modele_reservoir)
    AND Reservoir.position_dans_bus = IFNULL(%s, Reservoir.position_dans_bus)
    AND (Reservoir.id_bus LIKE %s OR Reservoir.id_bus IS NULL)
GROUP BY
    Reservoir.id_reservoir,
    Reservoir.id_bus,
    Reservoir.id_modele_reservoir,
    Reservoir.taille_reservoir,
    Reservoir.position_dans_bus,
    Reservoir.date_mise_service,
    Reservoir.date_retrait_service,
    Reservoir.nb_cycles_reels,
    M.modele_reservoir
HAVING
    (
        SUM(COALESCE(Reservoir.taille_reservoir, 0)) >= %s
        AND SUM(COALESCE(Reservoir.taille_reservoir, 0)) <= %s
    ) AND (
        AVG(COALESCE(Reservoir.nb_cycles_reels, 0)) >= %s
        AND AVG(COALESCE(Reservoir.nb_cycles_reels, 0)) <= %s
    );"""

#
#
# Contrôles
#
#

#show controles
GET_CONTROLE ="""SELECT
    Controle.id_controle,
    Controle.date_controle,
    Controle.analyse_rendue,
    Controle.prix,
    Reservoir.id_reservoir,
    Reservoir.id_modele_reservoir,
    Modele_reservoir.modele_reservoir
FROM
    Controle
INNER JOIN Reservoir ON Controle.id_reservoir = Reservoir.id_reservoir
INNER JOIN Modele_reservoir ON Reservoir.id_modele_reservoir = Modele_reservoir.id_modele_reservoir
ORDER BY Controle.id_controle;
"""

#add controle
INSERT_NEW_CONTROLE = """INSERT INTO Controle(
date_controle,
analyse_rendue,
id_reservoir,
prix)
VALUES(%s,%s,%s,%s)"""

DELETE_CONTROLE = """DELETE FROM Controle WHERE id_controle = %s;"""

EDIT_CONTROLE = """UPDATE Controle
SET
    date_controle = NULLIF(%s, ''),
    analyse_rendue = %s,
    id_reservoir = %s,
    prix = %s
WHERE
    id_controle = %s;"""


GET_CONTROLE_FILTER ="""SELECT
    id_controle,
    date_controle,
    analyse_rendue,
    id_reservoir,
    prix
FROM Controle
WHERE
    id_controle = %s
    AND (date_controle IS NULL OR (date_controle BETWEEN %s AND %s))
    AND id_reservoir = %s
    AND (prix BETWEEN %s AND %s);

"""
#
#
# Mois
#
#

GET_MOIS = """SELECT
    Mois.id_mois,
    Mois.date_plein,


FROM
    Mois"""

#
#
# Consommation
#
#

#show consommation
GET_CONSOMMATION ="""SELECT
    Consomme.id_bus,
    Consomme.id_date,
    Consomme.consommation_hydrogene,
    Consomme.kilometres_parcourus,
    Bus.nom_bus,
    Mois.date_plein
FROM
    Consomme
    INNER JOIN Bus ON Consomme.id_bus = Bus.id_bus
    INNER JOIN Mois ON Consomme.id_date = Mois.id_mois
"""

INSERT_NEW_CONSOMMATION = """INSERT INTO Consomme(
id_consommation,
id_date,
consommation_hydrogene,
kilometres_parcourus,
id_bus),
VALUES(%s,%s,%s,%s,%s)"""

DELETE_CONSOMMATION = """DELETE FROM Consomme WHERE id_bus = %s;"""

EDIT_CONSOMMATION = """UPDATE Consomme
SET
    id_bus = %s,
    consommation_hydrogene = %s,
    kilometres_parcourus = %s,
    id_date = %s,
WHERE
    id_date = %s,
    id_bus = %s,"""

