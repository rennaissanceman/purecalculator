Pure Calculator

Projekt napisany w języku Python, realizujący podstawowe operacje 
matematyczne: dodawanie, odejmowanie, mnożenie i dzielenie.
Kod został przygotowany zgodnie z konwencją PEP8 i przetestowany 
przy użyciu frameworka pytest z raportowaniem pokrycia kodu 
(coverage).

Opis projektu

Kalkulator obsługuje przypadki szczególne, takie jak:
- próba dzielenia przez zero (ZeroDivision),
- wartości specjalne NaN i Inf,
- liczby zmiennoprzecinkowe bliskie zera 
- (porównywane z tolerancją 1e-12).

Program zawiera przykłady wywołań klasy Calculator oraz 
zestaw testów jednostkowych w katalogu tests/.

Licencja

Projekt edukacyjny realizowany w ramach nauki języka Python.
Można dowolnie używać i modyfikować do celów naukowych lub testowych.