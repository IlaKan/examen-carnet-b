import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from scripts.lib.titulo_clase import puntos_cruzados, titulo, zona_corta, nombre_punto

CAT = [
    {"nombre": "Z2 - 3.Salida desde zona 2 (2)", "lat": 41.0, "lng": 2.0},
    {"nombre": "Z3 - 4.Túnel Esplugues", "lat": 41.0, "lng": 2.01},
]

def pt(lat, lng, s):
    return {"lat": lat, "lng": lng, "time": f"2026-11-06T10:00:{s:02d}Z"}

def test_cruza_por_el_tramo_aunque_ningun_punto_gps_este_cerca():
    # dos lecturas a ~420 m del punto, a cada lado; el tramo pasa por encima
    track = [pt(41.0, 2.005, 0), pt(41.0, 2.015, 30)]
    assert puntos_cruzados(track, CAT) == [1]

def test_salto_de_gps_no_cuenta():
    # 840 m en 1 s = salto imposible
    track = [pt(41.0, 2.005, 0), pt(41.0, 2.015, 1)]
    assert puntos_cruzados(track, CAT) == []

def test_titulo_salta_punto_generico_y_cuenta_extras():
    t = titulo("2026-11-06", ["ZONA 2 - PEDRALBES", "ZONA 3 - Z. UNIVERSIT."], [0, 1], CAT)
    assert t == "6 nov · Les Corts · Túnel Esplugues (+1)"

def test_sin_puntos_nuevos_usa_calle_no_repetida():
    t = titulo("2026-10-07", ["zona franca"], [], CAT,
               calles=["Passeig de la Zona Franca", "Carrer de l'Alumini"],
               calles_usadas={"Passeig de la Zona Franca"})
    assert t == "7 oct · Zona Franca · Carrer de l'Alumini"

def test_nombres_y_zonas():
    assert nombre_punto("Z4 - 9.1 Isleta Palmeras II") == "Isleta Palmeras II"
    assert zona_corta(["ZONA 3 - Z. UNIVERSIT.", "ZONA 4 - POBLE SEC", "ZONA 6 - MONTJÜIC"]) == "Les Corts + Poble Sec + Montjuïc"
