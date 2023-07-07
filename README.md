# ENGETO_projekt_3

Třetí projekt na Python Akademii od Engeta.

## Popis projektu

Tento projekt slouží k extrahování výsledků parlamentních voleb v roce 2017.

## Instalace knihoven

Knihovny, které jsou použity v kódu jsou uložené v souboru `requirements.txt`.

```
pip3 install -r requirements.txt
```

## Spouštění projektu

Spouštění soubru `election_scaper.py` v příkazovém řádku požaduje dva argumenty.

```l
python3 election_scraper <odkaz-uzemniho-celku> <vysledny-soubor>
```

## Ukázka projektu

Výsledky hlasování pro okres Benešov.

1. argument: `https://volby.cz/pls/ps2017nss/ps32?xjazyk=CZ&xkraj=2&xnumnuts=2101`
2. argument: `Benesov_test.csv`

Spouštění programu:

```powershell
python election_scraper.py 'https://volby.cz/pls/ps2017nss/ps32?xjazyk=CZ&xkraj=2&xnumnuts=2101' 'benesov_test.csv'
```

Průběh stahování:

```
STAHUJI DATA Z VYBRANEHO URL: https://volby.cz/pls/ps2017nss/ps32?xjazyk=CZ&xkraj=2&xnumnuts=2101
UKLADAM DO SOUBORU: benesov_test.csv
UKONCUJI election_scraper
```

Částečný výstup: 

```
Kód obce;Název obce;Registrovani voliči;Vydané obálky;Platné hlasy;Občanská demokratická strana;...
529303;Benešov;13104;8476;8437;1052;10;2;624;3;802;597;109;35;112;6;11;948;3;6;414;2577;3;21;314;5;58;17;16;682;10
532568;Bernartice;191;148;148;4;0;0;17;0;6;7;1;4;0;0;0;7;0;0;3;39;0;0;37;0;3;0;0;20;0
...
```
