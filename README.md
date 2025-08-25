# lainaussovellus

Sovellus on yleiskäyttövaraston lainausjärjestelmä. Tällä kehitysversiollä sovelluksella onnistuvat seuraavat toiminnot:
+  Käyttäjä pystyy luomaan tunnuksen ja kirjautumaan sisään sovellukseen.
+  Käyttäjä pystyy lisäämään, muokkaamaan ja poistamaan tietokohteita.
+  Käyttäjä näkee sovellukseen lisätyt tietokohteet.
+  Käyttäjä pystyy etsimään tietokohteita hakusanalla tai muulla perusteella.
+  Sovelluksessa on käyttäjäsivut, jotka näyttävät tilastoja ja käyttäjän lisäämät tietokohteet.
+  Käyttäjä pystyy valitsemaan tietokohteelle yhden tai useamman luokittelun. Mahdolliset luokat ovat tietokannassa.
+  Käyttäjä pystyy lähettämään toisen käyttäjän tietokohteeseen liittyen jotain lisätietoa, joka tulee näkyviin sovelluksessa.

Lopullista palautusta varten täytyy vielä kehittää mm.
-  toimintojen parannus
-  tietoturvan parannus
-  yksityiskohdat, ulkoasut, siisteys
  
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

Repositoriossa on tiedosto seed.py jonka avulla voit testata suuren tietomäärän käsittely. Testaus toimii parhaiten ilman aloitustestaustietoja, eli älä suorita sqlite3 database.db < data.sql. Sen sijaan, vertailua varten voit ensiksi kommentoida "CREATE INDEX" syntaksit pois schema.sql:stä, luoda & täyttää tietokantaa kommennoilla sqlite3 database.db < schema.sql ja sen jälkeen python3 seed.py. Sen jälkeen pystyt luomaan uuden tunnuksen ja kirjautumaan sisään. Huom: seed.py:n avulla ilman indeksisyntakseja luotu database.db:n koko on noin 350 MB, ja indeksien kanssa noin 1GB!

Testauksen aikana huomattiin seuraavia parannuksia (huomaa että tiedostossa seed.py käytetään satunaista elementtejä, eli jokainen testaus tuottaa erilaisia tuloksia):
-  käyttäjäsivuilla (/user/usertest1) ilman indekseja siinä aikana ladatun tavaran määrä oli 100.323 ja vei 0.6 sekuntia. Indekseillä ladatun tavaran määrä oli 100.035 ja vei 0.03 sekuntia. Vastaavanlainen esimerkki löytyi usertest90:stä (99.678 tavaraa, 0.56 sekuntia ilman; 100.044 tavaraa, 0.01 sekuntia indekseillä). Tämä johtuu indeksistä items(owner_id) (CREATE INDEX idx_items_ownerid ON items(owner_id)) koska forum.user_uploads kyselee owner_id:n perusteella.
  
-  käyttäjänlainaussivuilla (user_borrowings/usertest1) ilman indekseja siinä aikana ladatun tavaran määrä oli 9.958 ja vei 0.22 sekuntia. Indekseillä laadatun tavaran määrä oli 9.952 ja vei 0.01 sekuntia. Vastaavanlainen esimerkki löytyi usertest90:stä (9.980 tavaraa, 0.21 sekuntia ilman; 9.828 tavaraa, 0.00 sekuntia indekseillä). Tämä johtuu indekseistä borrower_id ja borrow_time (CREATE INDEX idx_borrowings_borrowerid_borrowtime
  ON borrowings(borrower_id, borrow_time DESC)) koska forum.user_borrowings kyselee borrower_id:n perusteella ja järjestää borrow_time laskevaan järjestykseen.
  
-  haku hakusanalla 'itemt' ilman indekseja siinä aikana vei 14.05 sekuntia. Indekseillä vei 10.29 sekuntia. Tämä johtuu indeksistä items(item_name) (CREATE INDEX idx_items_itemname ON items(item_name)) koska forum.search hakee tavarannimen perusteella jonka nimi sisältää 'itemt'
