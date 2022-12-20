import psycopg2
import pandas as pd

class ToolRentalApp:
    def __init__(self, user, password):
        self.conn = psycopg2.connect(dbname="tool_rental_db", user=user, password=password, host="postgres", port="5432")
        self.cur = self.conn.cursor()
    

    def iamSuperUser(self):
        query = f"""
        show is_superuser
        """
        self.cur.execute(query)

        return self.cur.fetchone()[0]

    
    def getClientInstruments(self, login):
        query = f"""
        select instrument, title, type, manufacturer, price, pledge, date_rental_end
        from all_contracts
        where login = '{login}' and
              status != true
        """
        self.cur.execute(query)

        return pd.DataFrame(self.cur.fetchall(), columns=["ID", "Название", "Тип", "Производитель", "Цена", "Залог", "Дата окончания проката"]).sort_values("ID")


    def getRentInstruments(self):
        query = f"""
        select id, title, type, manufacturer, price, pledge
        from instrument
        where status = 'ready for rent'
        """
        self.cur.execute(query)
        
        return pd.DataFrame(self.cur.fetchall(), columns=["ID", "Название", "Тип", "Производитель", "Цена", "Залог"]).sort_values("ID") 


    def getCheckInstruments(self):
        query = f"""
        select *
        from instrument
        where status not in ('in use', 'ready for rent')
        """
        self.cur.execute(query)

        return pd.DataFrame(self.cur.fetchall(), columns=["ID", "Название", "Тип", "Производитель", "Цена", "Залог", "Статус"]).sort_values("ID")

    
    def rentInstrument(self, date_rent_end, instrument, client):
        try:
            queryContract = f"""
            insert into contract (date_rental_end, instrument, client)
            values ('{date_rent_end}', {instrument}, '{client}')
            """
            self.cur.execute(queryContract)

            queryStatus = f"""
            update instrument
            set status = 'in use'
            where id = {instrument}
            """
            self.cur.execute(queryStatus)

            self.conn.commit()
            return ("Инструмент взят успешно", "-")
        except:
            self.conn.rollback()
            return ("Ошибка взятия инструмента", "warning")


    def returnInstrument(self, instrument, client):
        try:
            queryContract = f"""
            update contract
            set status = true
            where instrument = {instrument} and
                  client = '{client}'
            """
            self.cur.execute(queryContract)

            queryStatus = f"""
            update instrument
            set status = 'need check'
            where id = {instrument}
            """
            self.cur.execute(queryStatus)

            self.conn.commit()
            return ("Инструмент успешно возвращен", "-")
        except:
            self.conn.rollback()
            return ("Ошибка возврата инструмента", "warning")


    def addInstrument(self, title, type, manufacturer, price, pledge):
        try:
            query = f"""
            insert into instrument (title, type, manufacturer, price, pledge, status)
            values ('{title}', '{type}', '{manufacturer}', '{price}', '{pledge}', 'ready for rent')
            """
            self.cur.execute(query)

            self.conn.commit()
            return ("Инструмент успешно добавлен", "-")
        except:
            self.conn.rollback()
            return ("Ошибка добавления инструмента", "warning")

    
    def updateInstrument(self, login, instrument, status):
        try:
            queryVerification = f"""
            insert into verification (employee, instrument)
            values ('{login}', '{instrument}')
            """
            self.cur.execute(queryVerification)

            queryStatus = f"""
            update instrument
            set status = '{status}'
            where id = {instrument}
            """
            self.cur.execute(queryStatus)

            self.conn.commit()
            return ("Статус инструмента успешно обновлен", "-")
        except:
            self.conn.rollback()
            return ("Ошибка обновления статуса инструмента", "warning")
