# lainaussovellus

Sovellus on yleiskäyttövaraston lainausjärjestelmä. Sovelluksella onnistuvat seuraavat toiminnot:
+  Käyttäjä pystyy luomaan tunnuksen ja kirjautumaan sisään sovellukseen.
+  Käyttäjä pystyy lisäämään, muokkaamaan ja poistamaan tavaratietokohteita.
+  Käyttäjä pystyy lisäämään sekä tavarakuva että käyttäjäkuva.
+  Käyttäjä pystyy lisäämään lisätietoja tavaratietokohteisiin, kuten luokkitellut, ominaisuudet, ja tavaran sijainti. Mahdolliset luokat ovat tietokannassa.
+  Käyttäjä näkee sovellukseen lisätyt tietokohteet.
+  Käyttäjä pystyy etsimään tietokohteita hakusanalla.
+  Sovelluksessa on käyttäjäsivut, jotka näyttävät tilastoja ja käyttäjän lisäämät tavaratietokohteet.
+  Käyttäjä pystyy kirjaamaan lainaustoiminnat tavaratietokohteisiin, joka tulee näkyviin sovelluksessa.
+  Sovelluksessa on tilastot tavaratietokohteiden määrästä ja lainaustoiminnasta.

--------------------------------------------------------------------------------------------------------------------------------------------------------------

**KÄYNNISTYS JA TEHTAUSOHJEET**

+  Ensiksi lataa kaikki tiedostot repositoriosta tietokoneellesi.
  
+  Tarvitset samaan kansioon myös Pythonin virtuaaliympäristön, flask-asennuksen (kuvattu kurssin materiaalin 1. osassa), ja sqlite-asennuksen (kuvattu kurssin materiaalin 2. osassa).
  
+  Tietokannat luodaan schema.sql-tiedostolla, ja alustavasti täytetään init.sql-tiedostolla.
  
+  Asennusten jälkeen, voit aloittaa testauksen. Sovelluksessa pitäisi ensiksi pystyä luomaan uuden tunnuksen. Sisään kirjautumisen jälkeen, pääset lisäämään, tarkastamaan, muokkaamaan, ja poistamaan tietokohteita. Pääset myös lisäämään kuvia, testamaan lainausjärjestelmää ja hakutoimintoa.

+  On myös saatavilla data.sql-tiedosto jonka avulla voit lisätä aloitustietoja testausta varten.

**KOMMENNOT TESTAUSTA VARTEN**

**Linuxilla**

$ cd "kansion osoite johon latasit sovelluksen"

$ python3 -m venv venv

$ source venv/bin/activate

$ pip install flask

$ sqlite3 database.db < schema.sql

$ sqlite3 database.db < init.sql

$ sqlite3 database.db < data.sql (vain jos haluat käyttää aloitustestaustiedot)

$ flask run tai $ flask run --debug


**Windowsilla**

cd "kansion osoite johon latasit sovelluksen"

python -m venv venv

venv\Scripts\activate

pip install flask

sqlite3 database.db < schema.sql

sqlite3 database.db < init.sql

sqlite3 database.db < data.sql (vain jos haluat käyttää aloitustestaustiedot)

flask run tai flask run --debug

--------------------------------------------------------------------------------------------------------------------------------------------------------------

**SUUREN TIETOMÄÄRÄN TESTAUS**
(testattu 30.08.2025 versiolla)

Repositoriossa on tiedosto seed.py jonka avulla voit testata suuren tietomäärän käsittely. Testaus toimii parhaiten ilman aloitustestaustietoja, eli älä suorita sqlite3 database.db < data.sql. Sen sijaan, vertailua varten voit ensiksi kommentoida "CREATE INDEX" syntaksit pois schema.sql:stä, luoda & täyttää tietokantaa kommennoilla sqlite3 database.db < schema.sql ja sen jälkeen python3 seed.py. Sen jälkeen pystyt luomaan uuden tunnuksen ja kirjautumaan sisään. Huom: seed.py:n avulla ilman indeksisyntakseja luotu database.db:n koko on noin 360 MB, ja indeksien kanssa noin 1GB!

Testauksen aikana huomattiin seuraavia parannuksia (huomaa että tiedostossa seed.py käytetään satunaista elementtejä, eli jokainen testaus tuottaa erilaisia tuloksia):
-  käyttäjäsivuilla (/user/usertest1) ilman indekseja siinä aikana ladatun tavaran määrä oli 99.823 ja vei 0.54 sekuntia. Indekseillä ladatun tavaran määrä oli 100.2385 ja vei 0.03 sekuntia. Vastaavanlainen esimerkki löytyi usertest90:stä (99.925 tavaraa, 0.59 sekuntia ilman indeksejä; 99.826 tavaraa, 0.01 sekuntia indekseillä). Tämä johtuu indeksistä items(owner_id) (CREATE INDEX idx_items_ownerid ON items(owner_id)) koska forum.user_uploads kyselee owner_id:n perusteella.
  
-  käyttäjänlainaussivuilla (user_borrowings/usertest1) ilman indekseja siinä aikana ladatun tavaran määrä oli 10.146 ja vei 0.21 sekuntia. Indekseillä laadatun tavaran määrä oli 9.908 ja vei 0.02 sekuntia. Vastaavanlainen esimerkki löytyi usertest90:stä (9.929 tavaraa, 0.19 sekuntia ilman indeksejä; 10.045 tavaraa, 0.00 sekuntia indekseillä). Tämä johtuu indekseistä borrower_id ja borrow_time (CREATE INDEX idx_borrowings_borrowerid_borrowtime
  ON borrowings(borrower_id, borrow_time DESC)) koska forum.user_borrowings kyselee borrower_id:n perusteella ja järjestää borrow_time laskevaan järjestykseen.
  
-  haku hakusanalla 'itemt' ilman indekseja siinä aikana vei 13.54 sekuntia. Indekseillä vei 10.39 sekuntia. Tämä johtuu indeksistä items(item_name) (CREATE INDEX idx_items_itemname ON items(item_name)) koska forum.search hakee tavarannimen perusteella jonka nimi sisältää 'itemt'
