* Käyttäjä voi kirjautua sisään ja ulos sekä luoda uuden tunnuksen.
* Käyttäjä voi antaa arvion (tähdet ja kommentti) museosta ja lukea muiden antamia arvioita.
* Ylläpitäjä voi lisätä ja poistaa museoita sekä määrittää museosta näytettävät tiedot.
* Käyttäjä voi etsiä kaikki museot, joiden kuvauksessa on annettu sana.
* Ylläpitäjä voi luoda ryhmiä, joihin museoita voi luokitella. museo voi kuulua yhteen tai useampaan ryhmään.
* Ylläpitäjä voi tarvittaessa poistaa käyttäjän antaman arvion.
* Käyttäjä näkee museot kartalla ja voi painaa museosta, jolloin siitä näytetään lisää tietoa (kuten kuvaus ja aukioloajat).
* Käyttäjä näkee myös listan, jossa museot on järjestetty parhaimmasta huonoimpaan arvioiden mukaisesti.

Sovellusta voi testata osoitteessa:
https://tsoha-museums.onrender.com/

Sovellus on isännöity Renderin ilmaisessa palvelussa, minkä vuoksi palvelin siirtyy lepotilaan, jos sitä ei käytetä aktiivisesti. Viive saattaa kestää päälle minuutin! ⏰

## Asennus paikallisesti
1. Kloonaa repository:
   ```
   git clone https://github.com/vellam0/tsoha-museums.git
   ```
2. Luo juurihakemistoon .env-tiedosto ja määritä sen sisältö seuraavasti:
  ```
  DATABASE_URL=<database-local-address>
  SECRET_KEY=<secret-key>
  ```
3. Mene projektin juurikansioon ja asennan poetryn riippuvuudet komennolla:
  ```
  poetry install
  ```
4. Mene virtuaaliympäristöön komennolla:
  ```
  poetry shell
  ```
5. Luo tietokanta ja tuo schema.sql sinne

6. Käynnistä sovellus komennolla
  ```
  python3 src/index.py
  ```
   
