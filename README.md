# lainaussovellus
# välipalautus 3

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

**KÄYNNISTYS JA TEHTAUSOHJEET**

+  Ensiksi lataa kaikki tiedostot repositoriosta tietokoneellesi.
  
+  Tarvitset samaan kansioon myös Pythonin virtuaaliympäristön, flask-asennuksen (kuvattu kurssin materiaalin 1. osassa), ja sqlite-asennuksen (kuvattu kurssin materiaalin 2. osassa).
  
+  Tietokannat luodaan schema.sql-tiedostolla, ja alustavasti täytetään init.sql-tiedostolla.
  
+  Asennusten jälkeen, voit aloittaa testauksen.Sovelluksessa pitäisi ensiksi pystyä luomaan uuden tunnuksen. Sisään kirjautumisen jälkeen, pääset lisäämään, tarkastamaan, muokkaamaan, ja poistamaan tietokohteita. Pääset myös lisäämään kuvia, testamaan lainausjärjestelmää ja hakutoimintoa.

**KOMMENNOT TESTAUSTA VARTEN**

**Linuxilla**

$ cd "kansion osoite johon latasit sovelluksen"

$ python3 -m venv venv

$ source venv/bin/activate

$ pip install flask

$ sqlite3 database.db < schema.sql

$ sqlite3 database.db < init.sql

$ flask run tai $ flask run --debug


**Windowsilla**

cd "kansion osoite johon latasit sovelluksen"

python -m venv venv

venv\Scripts\activate

pip install flask

sqlite3 database.db < schema.sql

sqlite3 database.db < init.sql

flask run tai flask run --debug



#välipalautus 2

Sovellus on yleiskäyttövaraston lainausjärjestelmä. Tällä kehitysversiollä sovelluksella onnistuvat seuraavat toiminnot:

-  Käyttäjä pystyy luomaan tunnuksen ja kirjautumaan sisään sovellukseen.
-  Käyttäjä pystyy lisäämään ja muokkaamaan tietokohteita.
-  Käyttäjä näkee sovellukseen lisätyt tietokohteet.
-  Sovelluksessa on käyttäjäsivut, jotka näyttävät varastoon lisätyt tietokohteet.
-  Käyttäjä pystyy valitsemaan tietokohteelle yhden tai useamman luokittelun. Mahdolliset luokat ovat tietokannassa.

Lopullista palautusta varten täytyy vielä kehittää mm.

-  tietokohteiden poistaminen
-  lainausjärjestelmä
-  tietokannan lajennus
-  hakutoiminnat
-  tilastot tietokohteista käyttäjäsivussa
-  tietoturvan parannus
-  ulkoasut

Sovellus on kehitetty kurssin esimerkkisoveluksen kehyksestä, käytetyt tiedostot viittavat esimerkkisoveluksen tiedostoihin ja sovelluksen rakenne on samanlaista.

Testaa ensin luomalla database.db schema.sql:stä, sitten käynnistämällä flask. Sen jälkeen pitäisi pystyä luomaan uuden tunnuksen, lisäämään ja muokkaamaan tietokohteita.

#välipalautus 1

-  Sovelluksessa käyttäjät pystyvät ylläpitämään yhteiskäyttövaraston tavaroiden lainaustoiminnat.
-  Käyttäjä pystyy luomaan tunnuksen ja kirjautumaan sisään sovellukseen.
-  Käyttäjä pystyy lisäämään ja poistamaan tavaroita, kirjaamaan lainaustoimintaa, sekä laittamaan kommentteja tavaroihin.
-  Käyttäjä näkee sovellukseen lisätyt tavarat, niiden omistajat, lainaustoiminnat/historiat, sekä kommentit.
-  Käyttäjä pystyy etsimään tavaroita niiden ominaisuuksien perusteella.
-  Käyttäjäsivu näyttää, montako tavaraa, lainaustoimintaa ja kommenttia käyttäjä on lähettänyt. Tiedot näytetään myös listana.
-  Käyttäjä pystyy valitsemaan tavaroille yhden tai useamman luokittelun (esim. tavaroiden laji, tuotemerkki, väri, jne.).
-  Käyttäjä pystyy kirjaamaan lainaustoimintaa. Lainausilmoituksessa näytetään, milloin tavarat lainataan ja palautetaan.
-  Käyttäjä pystyy kirjoittamaan kommentteja tavaroiden kunnosta.

Tässä pääasiallinen tietokohde on tavarailmoitus ja toissijainen tietokohde on omistaja, lainaustoiminnat, ja kommentit.
