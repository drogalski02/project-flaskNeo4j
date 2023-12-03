# project-flaskNeo4j
- Projekt posiada bazę danych umieszczoną w chmurze Neo4j AuraDB
- Aplikacja została osadzona w sieci pod linkiem: https://flask-neo4j-project.onrender.com/employees
- Aplikacja wykorzystuje serwer WSGI gunicorn
- Do poprawnego działania należy zdefiniować plik .env bądź zmienne środowisku w sewisie hostingowym:
  - USERNAME="<nazwa_użytkownika_neo4j>"
  - PASSWORD="<hasło_do_bazy>"
  - URI="<uri_do_bazy>"
- Polecenie do uruchomienia aplikacji: `gunicorn -w 4 -b 0.0.0.0:6000 app:app`
## Endpointy
- [GET] /employees (wyświetla wszystkich pracowników)
- [GET] /employees/arg1=arg2 ,gdzie arg1={imię, nazwisko, stanowisko, pensja, orderbyAasc, orderbyDesc}, arg2 = szukana wartość
- (wyświetla pracówników filtrując po imieniu, nazwisku, stanowisku, pensji lub sortując rosnąco/malejąco po zadanej wartości)
- [POST] /employees (dodaje pracownika do wskazanego oddziału)
- [DELETE] /employees/employee_id (usuwa pracownika po id a jeśli jest managerem to usuwa cały oddział)
- [GET] /employees/employee_id/subordinates (wyświetla podwładnych pracowników dla pracownika o wskazanym id)
- [GET] /departments/employee_id (wyświetla informacje o oddziale pracownika o podanym id jak i liczbie pracowników i managerze)
- [GET] /departments/arg1=arg2 ,gdzie arg1={name, employees_number, orderbyAsc, orderbyDesc}, arg2 = szukana wartość
- (wyświetla oddziały filtrując po nazwie czy liczbie pracowników lub sortuje rosnąco/malejąco po zadanej wartości)
- [GET] /departments/department_id/employees (wyświetla pracownków oddziału o zadanym id)
