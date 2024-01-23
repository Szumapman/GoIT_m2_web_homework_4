# Zadanie domowe #4
## GoIT moduł 2 web

Twoim celem jest zaimplementowanie prostej aplikacji internetowej. Skorzystaj z poniższych plików jako podstawy.

Analogicznie do przykładu w konspekcie, stwórz aplikację internetową z routingiem dla dwóch stron html : index.html imessage.html.

Ponadto:

- Przetwórz podczas uruchamiania aplikacji statyczne zasoby: style.css, logo.png;
- Zorganizuj pracę z formularzem na stronie message.html;
- W przypadku błędu 404 Not Found zwróć stronę error.html;
- Twoja aplikacja działa na porcie 3000;

Aby pracować z formularzem, utwórz serwer Socket na porcie 5000. Algorytm pracy jest następujący: wprowadzasz dane do formularza, trafiają one do Twojej aplikacji webowej, która wysyła je dalej do przetworzenia za pomocą socket (protokół UDP), serwera Socket. Serwer Socket przetwarza otrzymany ciąg bajtów na słownik i zapisuje go w pliku data.json w folderze storage.
Format pliku data.json jest następujący:
```json
{
  "2022-10-29 20:20:58.020261": {
    "username": "krabaton",
    "message": "First message"
  },
  "2022-10-29 20:21:11.812177": {
    "username": "Krabat",
    "message": "Second message"
  }
}
```
Kluczem każdej wiadomości jest czas jej otrzymania: datetime.now(). Oznacza to, że każda nowa wiadomość z aplikacji internetowej jest dodawana do pliku storage/data.json z czasem jej otrzymania.

Do utworzenia aplikacji internetowej użyj jednego pliku main.py. Uruchom serwer HTTP i serwer Socket w różnych wątkach.

## Zadanie dodatkowe
Jest to zadanie opcjonalne i nie musisz go wykonywać, aby zaliczyć tę pracę domową.

1. Utwórz plik Dockerfile i uruchom swoją aplikację jako kontener Docker.
2. Korzystając z mechanizmu volumes, zapisz dane z pliku storage/data.json poza kontenerem.

WSKAZÓWKA

Aby zaimplementować mechanizm volumes należy na początku działania aplikacji sprawdzić istnienie katalogu storage i pliku data.json. Jeśli ich nie ma, należy je utworzyć.
