from config import db
from sqlalchemy import text
from repositories.location_repository import address_to_coordinates, update_locations_from_museums

def get_museums():
    sql = text("SELECT * FROM museums")
    result = db.session.execute(sql)
    museums = result.fetchall()
    return museums


def get_museum_by_id(museum_id):
    sql = text("SELECT * FROM museums WHERE id=:museum_id")
    result = db.session.execute(sql, {"museum_id":museum_id})
    museum = result.fetchone()
    return museum


def get_museum_by_name(name):
    sql = text("SELECT id, name FROM museums WHERE name=:name")
    result = db.session.execute(sql, {"name": name})
    return result.fetchone()


def location_for_museum(museum_id, name, address):
    lat, lon = address_to_coordinates(address)
    if lat is None or lon is None:
        return "Ei koordinaatteja"
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
            "id": museum_id,
            "name": name,
            "address": address,
            "lat": lat,
            "lon": lon})
    db.session.commit()
    

def create_museum(name, bio, address, opening_hours, museum_type, tags, img_url):
    sql = text("""INSERT INTO museums 
               (name, bio, address, opening_hours, museum_type, tags, img_url)
               VALUES 
               (:name, :bio, :address, :opening_hours, :museum_type, :tags, :img_url) RETURNING id""")
    result = db.session.execute(sql, {
        "name": name,
        "bio": bio,
        "address": address,
        "opening_hours": opening_hours,
        "museum_type": museum_type,
        "tags": tags,
        "img_url": img_url
    })
    museum_id = result.fetchone().id
    location_for_museum(museum_id, name, address)
    db.session.commit()


def del_museum(museum_id):
    sql = text("DELETE FROM museums WHERE id=:museum_id")
    db.session.execute(sql, {"museum_id": museum_id})
    db.session.commit()


def update_museum(museum_id, name, bio, address, opening_hours, museum_type, tags, img_url):
    sql = text("""UPDATE museums 
                  SET name=:name, 
                      bio=:bio, 
                      address=:address, 
                      opening_hours=:opening_hours, 
                      museum_type=:museum_type, 
                      tags=:tags, 
                      img_url=:img_url
                  WHERE id=:museum_id""")
    db.session.execute(sql, {
        "museum_id": museum_id,
        "name": name,
        "bio": bio,
        "address": address,
        "opening_hours": opening_hours,
        "museum_type": museum_type,
        "tags": tags,
        "img_url": img_url
    })
    db.session.commit()


def search_museums(search_word, search_type):
    def search_by_word(search_word):
        if not search_word:
            return []
        sql = text("SELECT * FROM museums WHERE name LIKE :search_word OR bio LIKE :search_word OR tags LIKE :search_word")
        result = db.session.execute(sql, {"search_word":"%"+search_word+"%"})
        return result.fetchall()


    def search_by_type(search_type):
        if not search_type:
            return []
        sql = text("SELECT * FROM museums WHERE museum_type=:search_type")
        result = db.session.execute(sql, {"search_type":search_type})
        return result.fetchall()


    content = search_by_word(search_word)
    content += search_by_type(search_type)
    return content
