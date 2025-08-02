# lainaussovellus

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
