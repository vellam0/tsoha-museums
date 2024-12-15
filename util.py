import re
from repositories.museum_repository import get_museum_by_name


def validate_login_info(username, password, confirm_password):
    if len(username) > 20 or len(username) < 5:
        return "Käyttäjänimen tulee olla 5-12 merkkiä pitkä."
    if len(password) > 20 or len(password) <8:
        return "Salasanan tulee olla 8-20 merkkiä pitkä."
    if not re.search(r"\d", password):
        return "Salasanassa täytyy olla vähintään yksi numero."
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        return "Salasanassa täytyy olla vähintään yksi erikoismerkki."
    if password != confirm_password:
        return "Salasanat eivät täsmää, yritä uudelleen."


def validate_review_form(title, review_text):
    if len(title) < 3 or len(title) > 150:
        return "Otsikon tulee olla 2-250 merkkiä pitkä."
    if len(review_text) < 5 or len(review_text) > 1000:
        return "Arvostelutekstin tulee olla 4-1000 merkkiä pitkä."


def validate_museum_form(name, bio, address, opening_hours, museum_type, tags=None, img_url=None, edit_id=None):
    if not name or len(name) < 3 or len(name) > 150:
        return "Museon nimen tulee olla 3-150 merkkiä pitkä."
    
    existing_museum = get_museum_by_name(name)
    if existing_museum and existing_museum.id != edit_id:
        return f"Museon nimi '{name}' on jo käytössä."

    if not bio or len(bio) < 10 or len(bio) > 2000:
        return "Kuvauksen tulee olla 10-2000 merkkiä pitkä."
    if not address or len(address) < 5 or len(address) > 250:
        return "Osoitteen tulee olla 5-250 merkkiä pitkä."
    if not opening_hours or len(opening_hours) < 3 or len(opening_hours) > 500:
        return "Aukioloaikojen tulee olla 3-500 merkkiä pitkä."
    if tags and len(tags) > 250:
        return "Tagien kokonaispituus ei saa ylittää 250 merkkiä."
    if img_url and not (img_url.startswith("http://") or img_url.startswith("https://")):
        return "Kuvan URL:n tulee alkaa http:// tai https://."
