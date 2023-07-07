"""
vysldky_voleb.py: třetí projekt do Engeto Online Python Akademie
author: David Zitnik
email: zitnik.david@seznam.cz
discord: davidzitnik
"""
import sys
import csv
import re
from requests import get
from bs4 import BeautifulSoup


def zkontroluj_argumenty(url, nazev_souboru):
    """ kontrola argumentu:
    1 argument - kontrola spravne url adresy
    2 argument - kontrola typu souboru .csv    """
    regex = (r"https://volby.cz/pls/ps2017nss/ps32\?xjazyk=CZ&xkraj=" +
             r"\d{1,2}" +                        # cislo kraje
             r"&xnumnuts=" +
             r"\d{4}")                           # cislo obce
    regex2 = r".\.csv\Z"                         # kontrola nazvu vystupniho souboru

    if re.search(regex, url) and re.search(regex2, nazev_souboru):
        return url
    print("Špatně zadaná url adresa nebo název výstupního .csv souboru.")
    sys.exit()


def najdi_tagy_stranky(rozdelene_html):
    """ nalezeni tagu 'odkaz na dalsi HTML stranu','kody obce', 'nazev obce'"""
    tagy_odkazy = rozdelene_html.find_all("td", {"class": "center"})
    odkazy = [tag.find("a")["href"] for tag in tagy_odkazy]                 # odkazy na dalsi stranku
    tagy_obce = rozdelene_html.find_all("td", {"class": "overflow_name"})
    obce = [tag.text.strip() for tag in tagy_obce]                          # nazvy obci
    tagy_kody = rozdelene_html.find_all("td", {"class": "cislo"})
    kody_obci = [tag.text.strip() for tag in tagy_kody]                     # kody obci
    # vytvoreni list slovniku z dat stranky (odkaz na dalsi stranu, kod obce, lokace)
    odkaz_kod_obec = [{"cast_url": odkaz, "kod obce": kod, "lokace": obec} for odkaz, kod, obec in zip(odkazy, kody_obci, obce)]
    return odkaz_kod_obec


def ziskej_odpoved_url(url):
    """ kontrola jestli se jedna o celou nebo jen cast url adresy
     a ziskani jeji parsovane odpovedi"""
    cast_url = "https://volby.cz/pls/ps2017nss/"
    # kontrola, jestli argument obsahuje celou url adresu
    vysledek = re.search(cast_url, url)
    if vysledek:
        cela_url = url
        print(f"STAHUJI DATA Z VYBRANEHO URL: {cela_url}")
    else:
        cela_url = f"{cast_url}{url}"
    return BeautifulSoup(get(cela_url).text, features="html.parser")


def zkontroluj_pritomnost_okrsku(text_html):
    """ kontrola, jestli jsou na strance odkazy na dalsi okrsky obce.
    Pokud stranka odkazy na okrsky neobsahuje, vraci se html_text.
    Pokud stranka odkazy obsahuje, vraci se  seznam odkazu na tyto okrsky"""
    try:
        tagy_okrsky = text_html.find_all("td", {"class": "cislo"})
        odkazy_okrsku = [tag.find("a")["href"] for tag in tagy_okrsky]
        return odkazy_okrsku                                                # seznam odkazu na okrsky
    except TypeError:
        return vytahni_konecna_data(text_html)                              # data z HTML stranky


def ziskej_data_z_obci(obce):
    """ vytvari se list slovniku ze ziskanych dat obci nebo souctu dat vsech okrsku"""
    data_komplet = []
    for x in obce:
        data_z_hlavicky = {"Kód obce": x.get("kod obce"), "Název obce": x.get("lokace")}  # slovnik z dat hlavicky
        parsovane_html = ziskej_odpoved_url(x.get("cast_url"))                            # odkaz --> odpoved
        html_nebo_list_odkazy = zkontroluj_pritomnost_okrsku(parsovane_html)           # kontrola obsahu dalsich odkazu

        if not isinstance(html_nebo_list_odkazy, list):
            slovnik_vsech_dat = {**data_z_hlavicky, **html_nebo_list_odkazy}           # slovnik z dat hlavicky a HTML
        else:
            sectena_data = {}
            for odkaz in html_nebo_list_odkazy:                                        # vyber dat z kazdeho odkazu
                rozdelene_html = ziskej_odpoved_url(odkaz)                             # text HTML stranky
                slovnik_dat = vytahni_konecna_data(rozdelene_html)                     # pozadovana data z HTML stranky
                sectena_data = secti_hodnoty_slovniku(sectena_data, slovnik_dat)       # soucet vysledku okrsku
            slovnik_vsech_dat = {**data_z_hlavicky, **sectena_data}                    # slovnik z dat hlavicky a okrsku
        data_komplet.append(slovnik_vsech_dat)                                         # pridani dat okresu do listu
    return data_komplet


def vytahni_konecna_data(data_obce):
    """ scrapuji pozadovana data z textu HTML stranky
    a z techto dat vytvarim slovnik """
    tagy_registrovani_volici = data_obce.find("td", {"headers": "sa2"})
    registrovani_volici = tagy_registrovani_volici.text.strip().replace('\xa0', '')             # registrovani volici
    tagy_vydane_obalky = data_obce.find("td", {"headers": "sa5"})
    vydane_obalky = tagy_vydane_obalky.text.strip().replace('\xa0', '')                         # vydane obalky
    tagy_platne_obalky = data_obce.find("td", {"headers": "sa6"})
    platne_obalky = tagy_platne_obalky.text.strip().replace('\xa0', '')                         # platne obalky
    tagy_vysledky_tab1 = data_obce.find_all("td", {"headers": re.compile('t[12]sa2 t[12]sb3')})
    vysledky = [tag.text.strip().replace('\xa0', '') for tag in tagy_vysledky_tab1]             # pocty hlasu
    tagy_nazev_strany = data_obce.find_all("td", {"class": "overflow_name"})
    nazev_strany = [tag.text.strip() for tag in tagy_nazev_strany]                              # nazvy strany

    # vytvoreni slovniku z udaju hlavicky stranky (volici, obalky, hlasy)
    data_z_hlavicky = {"Registrovani voliči": registrovani_volici,
                       "Vydané obálky": vydane_obalky,
                       "Platné hlasy": platne_obalky}
    # vytvoreni slovniku z nazvu strany a poctem hlasu
    vysledky_slovnik = {x[0]: x[1] for x in zip(nazev_strany, vysledky)}
    # vytvoreni kopletniho slovniku se vsemi pozadovanymi udaji
    data_z_hlavicky.update(vysledky_slovnik)
    return data_z_hlavicky


def secti_hodnoty_slovniku(okrsky_celkem, okrsek):
    """ secteni hodnot hlasu stran ze slovniku jednotlivych okrsku obce.
    Po secteni hodnot se vysledek opet prevede na string"""
    celkem = {}
    for klic in list(okrsek.keys()):
        celkem[klic] = str(int(okrsky_celkem.get(klic, 0)) + int(okrsek.get(klic, 0)))
    return celkem


def uloz_do_csv(data, soubor):
    """ ulozeni listu slovniku do csv souboru"""
    print("UKLADAM DO SOUBORU:", soubor)
    with open(soubor, 'w', newline="") as f:
        writer = csv.DictWriter(f, fieldnames=data[0].keys(), delimiter=";")
        writer.writeheader()
        for radek in data:
            writer.writerow(radek)


def main(url_adresa, nazev_csv_souboru):
    """ kontrola argumentu, parsovany text z url, ziskani pozadovanych dat, vytvoreni slovniku z dat,
      ulozeni vsech slovniku do listu, zapis listu do .csv souboru"""
    validni_adresa = zkontroluj_argumenty(url_adresa, nazev_csv_souboru)
    text_html = ziskej_odpoved_url(validni_adresa)
    seznam_obci = najdi_tagy_stranky(text_html)
    list_vsech_dat = ziskej_data_z_obci(seznam_obci)
    uloz_do_csv(list_vsech_dat, nazev_csv_souboru)
    print("UKONCUJI election_scraper")


if __name__ == "__main__":
    try:
        ADRESA = sys.argv[1]
        CSV_SOUBOR = sys.argv[2]
    except IndexError:
        print("Chyba argumentu")
    else:
        # adresa = "https://volby.cz/pls/ps2017nss/ps32?xjazyk=CZ&xkraj=2&xnumnuts=2101"
        # csv_soubor = "benesov_test.csv"
        main(ADRESA, CSV_SOUBOR)
