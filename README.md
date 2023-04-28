> ### Test_TZ

    1. git clone https://github.com/softicer-67/tz_28_04-23.git
    2. cd tz_28_04-23

### Postman
    
    Прочитать данные из таблицы:
        GET 127.0.0.1:8080/table
        
    Добавить строки:
        POST 127.0.0.1:8080/table/add
        Body -> raw --> JSON
          
          {
              "id": "5",
              "name": "AAA",
              "price": 0.111
          }
        
    Удалить строки: 
        127.0.0.1:8080/table/remove?id=5
        
        
