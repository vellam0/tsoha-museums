from config import db
from sqlalchemy import text
import requests


def address_to_coordinates(address):
    url = "https://nominatim.openstreetmap.org/search"
    params = {'q': address, 'format': 'json', 'countrycodes': 'fi'}
    headers = {'User-Agent': 'Museosovellus/1.0 (18c06ve7l@mozmail.com)'}
    response = requests.get(url, params=params, headers=headers)
    if response.status_code == 200 and response.json():
        data = response.json()[0]
        return float(data['lat']), float(data['lon'])
    return None, None


def update_locations_from_museums():
    sql_fetch = text("SELECT id, name, address FROM museums")
    museums = db.session.execute(sql_fetch).fetchall()

    for museum in museums:
        museum_id, name, address = museum.id, museum.name, museum.address

        lat, lon = address_to_coordinates(address)
        if lat is not None and lon is not None:
            sql_insert = text("""
                INSERT INTO locations (id, name, address, lat, lon)
                VALUES (:id, :name, :address, :lat, :lon)
                ON CONFLICT (id)
                DO UPDATE SET
                    name = EXCLUDED.name,
                    address = EXCLUDED.address,
                    lat = EXCLUDED.lat,
                    lon = EXCLUDED.lon""")
            db.session.execute(sql_insert, {
                'id': museum_id,
                'name': name,
                'address': address,
                'lat': lat,
                'lon': lon
            })

    db.session.commit()


def get_map_details():
    sql = text("""
        SELECT l.name, l.lat, l.lon, COALESCE(AVG(r.stars), 0) AS avg_stars, m.id AS museum_id
        FROM locations l
        LEFT JOIN museums m ON l.name = m.name
        LEFT JOIN reviews r ON m.id = r.museum_id
        GROUP BY l.name, l.lat, l.lon, m.id""")
    result = db.session.execute(sql).fetchall()
    locations = [
        {"name": row.name,
        "lat": row.lat,
        "lon": row.lon,
        "avg_stars": round(row.avg_stars, 0),
        "museum_id": row.museum_id}
        for row in result]
    return locations

