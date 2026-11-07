"""Add "sector" and "habilidad" to every point in public/data/points.json.

Usage:
    python3 scripts/sectores.py

Sectors are Claude's own geographic grouping (2026-11-07) to make the catalog
easier to memorise — not an official autoescuela division. "habilidad" is the
skill each never-crossed point trains, read from its professor note; points
without one get none. Safe to re-run: it overwrites both fields.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scripts.lib.titulo_clase import nombre_punto

POINTS_PATH = Path(__file__).resolve().parent.parent / "public" / "data" / "points.json"

SECTORES = {
    "Les Corts · Eje Diagonal–Dr. Marañón": [
        "Av. Pedralbes - Diagonal", "Cruce Diagonal - Hotel Sofía", "Incorporación Avda Diagonal", "Avda Diagonal",
        "Crude Diagonal - Dr Marañón", "Avda Diagona hacia Camp Nou", "Salida y llegada Zona 3"],
    "Les Corts · Joan XXIII–Dexeus": [
        "Giro Izquierda Avda Joan XXIII", "Salida Rotonda Joan XXIII", "Stop Joan XXIII", "Túnel Hospital Dexeus",
        "Carril Bus Gran Vía Carles III"],
    "Les Corts · Pedralbes Sur–Esplugues": [
        "Rotonda en Crta. Esplgues", "Av. Esplugues - González Tapias", "González Tapias - Sor Eulàlia d'Anzizu",
        "Salida de BCN por Diagonal", "Túnel Esplugues", "B-23 salida Sant Just/Sant Joan Despí"],
    "Les Corts · Nudo Ronda de Dalt (entradas 9 y 10)": [
        "Rotonda entrada 9 Rda Dalt", "Entrada 10 ronda de dalt (Besós)", "Entrada 10 Rda Dalt (Llobregat)",
        "Salida desde zona 2 (2)", "Salida desde zona 2 (3)", "Llegada a zona 2", "carrer dels Moneders"],
    "Les Corts · Pedralbes Norte (Pearson)": [
        "Paneles complementarios", "Calle sin salida", "Avd Pearson - Panamá", "Stop sin visibilidad",
        "Avda Pearson - Joan d'Alòs"],
    "Les Corts · Ctra. de Sants–L'Hospitalet": [
        "Ctra Sants - CC. Finestrelles", "Incorporación Ctra Sants", "Cambio sentido Cardenal Reig",
        "Túnel Ctra Sants a Hospitalet", "Riera Blanca Hospitalet", "Giro obligatorio Avda Madrid"],
    "Les Corts · Ronda de Dalt Sur (salidas 13-15)": ["Salida 13 Ronda de Dalt", "Salida 14 Ronda", "Salida 15 Ronda"],
    "Montjuïc · Plaça d'Espanya–Fira": ["Hotel Intercontinental", "Semáforo calle Lleida"],
    "Poble Sec": [
        "Stop de la muerte", "Stop Poeta Cabanes", "Calle Annibal", "Isleta de las Palmeras", "Isleta Palmeras II",
        "Semáforo Basuras", "Túnel Hotel Miramar"],
    "Montjuïc · Oeste (giros a la izquierda)": [
        "Giro izquierda INEFC", "Giro izquierda Polvorín", "Giro izquierda Calle Segura", "Plaza del Caballo",
        "Calle la Guatlla"],
    "Montjuïc · Cima y Sur": [
        "Acondicionamientos antena Montjuic", "Circulación prohibida Castillo", "Cambio sentido zona Esbarjo",
        "Derecha prohibida camiones"],
    "Gran Via · Plaza Europa": ["Plaza Europa"],
}

HABILIDADES = {
    "Lee la señal y su panel": [
        "Paneles complementarios", "Calle sin salida", "Avda Pearson - Joan d'Alòs", "carrer dels Moneders",
        "Circulación prohibida Castillo", "Derecha prohibida camiones", "Giro izquierda Calle Segura"],
    "Stop y semáforo: para siempre": [
        "Stop sin visibilidad", "Incorporación Ctra Sants", "Ctra Sants - CC. Finestrelles", "Hotel Intercontinental",
        "Semáforo Basuras", "Semáforo calle Lleida"],
    "Posición y giro en L": [
        "Avd Pearson - Panamá", "Giro izquierda INEFC", "Giro izquierda Polvorín", "Salida 15 Ronda",
        "Plaza del Caballo", "Riera Blanca Hospitalet", "Cambio sentido Cardenal Reig"],
    "Túnel = luces": ["Túnel Ctra Sants a Hospitalet", "Túnel Hotel Miramar", "Salida 14 Ronda"],
    "Velocidad y control": ["Salida 13 Ronda de Dalt", "Calle la Guatlla", "Cambio sentido zona Esbarjo"],
}


def invertir(grupos):
    out = {}
    for grupo, nombres in grupos.items():
        for n in nombres:
            assert n not in out, f"{n} está en dos grupos"
            out[n] = grupo
    return out


def main():
    points = json.loads(POINTS_PATH.read_text(encoding="utf-8"))
    sector, habilidad = invertir(SECTORES), invertir(HABILIDADES)
    usados = set()
    for p in points:
        n = nombre_punto(p["nombre"])
        p["sector"] = "La Maquinista" if "MAQUINISTA" in p["zona"] else sector[n]
        p.pop("habilidad", None)
        if n in habilidad:
            p["habilidad"] = habilidad[n]
        usados.add(n)
    sobran = (set(sector) | set(habilidad)) - usados
    assert not sobran, f"nombres que no existen en el catálogo: {sobran}"
    POINTS_PATH.write_text(json.dumps(points, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"{len(points)} puntos con sector, {sum('habilidad' in p for p in points)} con habilidad")


if __name__ == "__main__":
    main()
