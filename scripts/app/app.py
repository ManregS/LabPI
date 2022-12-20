import pandas as pd
from toolrental import ToolRentalApp
from shiny import App, render, reactive, ui

toolrental = ToolRentalApp("postgres", "postgres")

app_ui = ui.page_fluid(
    ui.row(
        ui.column(
            2,
            ui.input_text("login", "Логин")
        ),
        ui.column(
            2,
            ui.input_password("password", "Пароль")
        ),
        ui.column(
            2,
            ui.br(),
            ui.input_action_button("button_login", "Войти", class_="btn-success")
        )
    ),
    ui.output_ui("user_ui")
)


def server(input, output, session):
    @output
    @render.ui
    @reactive.event(input.button_login)
    def user_ui():
        try:
            toolrental = ToolRentalApp(input.login(), input.password())
            ui.notification_show("Авторизация успешна")
            if toolrental.iamSuperUser() == "on":
                return ui.TagList(
                    ui.navset_tab(
                        ui.nav(
                            "Проверить инструмент",
                            ui.layout_sidebar(
                                ui.panel_sidebar(
                                    ui.input_select("select_instrument_check", "ID инструмента", dict([(id, id) for id in toolrental.getCheckInstruments()["ID"]])),
                                    ui.input_select("select_statuses_check", "Статус", {
                                        "ready for rent": "Готов к прокату",
                                        "need repair": "Нуждается в починке",
                                        "scrapped": "Списан"
                                    }),
                                    ui.input_action_button("button_set_status", "Установить статус", class_="btn-success")
                                ),
                                ui.panel_main(
                                    ui.output_table("employee_instruments_check")
                                )
                            )
                        ),
                        ui.nav(
                            "Добавить инструмент",
                            ui.input_text("instrument_title", "Название"),
                            ui.input_text("instrument_type", "Тип"),
                            ui.input_text("instrument_manufacturer", "Производитель"),
                            ui.input_numeric("instrument_price", "Стоимость", 1, min=1),
                            ui.input_numeric("instrument_pledge", "Залог", 1, min=1),
                            ui.input_action_button("button_add_instrument", "Добавить инструмент", class_="btn-success")
                        )
                    )
                ).tagify()
            else:
                return ui.TagList(
                    ui.navset_tab(
                        ui.nav(
                            "Мои инструменты",
                            ui.layout_sidebar(
                                ui.panel_sidebar(
                                    ui.input_select("select_instrument_myself", "ID инструмента", dict([(id, id) for id in toolrental.getClientInstruments(input.login())["ID"]])),
                                    ui.input_action_button("button_return_instrument", "Вернуть", class_="btn-success")
                                ),
                                ui.panel_main(
                                    ui.output_table("client_instruments_myself")
                                )
                            )
                        ),
                        ui.nav(
                            "Каталог инструментов",
                            ui.layout_sidebar(
                                ui.panel_sidebar(
                                    ui.input_select("filter_select_type", "Тип", 
                                                    dict([(type, type) for type in ["-"] + toolrental.getRentInstruments()["Тип"].drop_duplicates().tolist()])),
                                    ui.input_select("filter_select_manufacturer", "Производитель", 
                                                    dict([(manufacturer, manufacturer) for manufacturer in ["-"] + toolrental.getRentInstruments()["Производитель"].drop_duplicates().tolist()])),
                                    ui.input_slider("filter_slider_price", "Цена", 
                                                    min=int(toolrental.getRentInstruments()["Цена"].replace("[$,]", "", regex=True).astype(float).min()), 
                                                    max=int(toolrental.getRentInstruments()["Цена"].replace("[$,]", "", regex=True).astype(float).max()), 
                                                    value=[int(toolrental.getRentInstruments()["Цена"].replace("[$,]", "", regex=True).astype(float).min()), 
                                                           int(toolrental.getRentInstruments()["Цена"].replace("[$,]", "", regex=True).astype(float).max())],
                                                    drag_range=True)
                                ),
                                ui.panel_main(
                                    ui.output_table("client_instruments_rent")
                                )
                            ),
                            ui.hr(),
                            ui.row(
                                ui.column(
                                    2,
                                    ui.input_select("select_instrument_rent", "ID инструмента", dict([(id, id) for id in toolrental.getRentInstruments()["ID"]]))
                                ),
                                ui.column(
                                    2,
                                    ui.input_date("date_instrument_rent", "Конец аренды")
                                ),
                                ui.column(
                                    2,
                                    ui.br(),
                                    ui.input_action_button("button_rent_instrument", "Арендовать", class_="btn-success")
                                )
                            )
                        )
                    )
                ).tagify()
        except:
            ui.notification_show("Неверный логин или пароль", type="warning")


    _employee_instruments_check = reactive.Value(pd.DataFrame())  
    _client_instruments_myself = reactive.Value(pd.DataFrame())
    _client_instruments_rent = reactive.Value(pd.DataFrame())  

    
    @output
    @render.table
    def employee_instruments_check():
        output = toolrental.getCheckInstruments()

        if not _employee_instruments_check.get().empty:
            output = _employee_instruments_check.get()
            _employee_instruments_check.set(pd.DataFrame())

        return output


    @output
    @render.table
    def client_instruments_myself():
        output = toolrental.getClientInstruments(input.login())

        if not _client_instruments_myself.get().empty:
            output = _client_instruments_myself.get()
            _client_instruments_myself.set(pd.DataFrame())

        return output

    
    @output
    @render.table
    def client_instruments_rent():
        output = toolrental.getRentInstruments()

        if not _client_instruments_rent.get().empty:
            output = _client_instruments_rent.get()
            _client_instruments_rent.set(pd.DataFrame())

        output = output[output["Цена"].replace("[$,]", "", regex=True).astype(float).between(input.filter_slider_price()[0], input.filter_slider_price()[1])]

        if input.filter_select_type() != "-":
            output = output[output["Тип"] == input.filter_select_type()]
        
        if input.filter_select_manufacturer() != "-":
            output = output[output["Производитель"] == input.filter_select_manufacturer()]

        ui.update_select("select_instrument_rent", choices=dict([(id, id) for id in output["ID"]]))

        return output


    @reactive.Effect
    @reactive.event(input.button_set_status)
    def _():
        operation = toolrental.updateInstrument(input.login(), input.select_instrument_check(), input.select_statuses_check())
        ui.notification_show(operation[0], type=operation[1])
        if operation[1] != "warning":
            _employee_instruments_check.set(toolrental.getCheckInstruments())
            _client_instruments_myself.set(toolrental.getClientInstruments(input.login()))
            _client_instruments_rent.set(toolrental.getRentInstruments())
            ui.update_select("select_instrument_check", choices=dict([(id, id) for id in toolrental.getCheckInstruments()["ID"]]))


    @reactive.Effect
    @reactive.event(input.button_add_instrument)
    def _():
        operation = toolrental.addInstrument(input.instrument_title(), 
                                             input.instrument_type(), 
                                             input.instrument_manufacturer(), 
                                             float("{:.2f}".format(input.instrument_price(), 2)), 
                                             float("{:.2f}".format(input.instrument_pledge(), 2)))
        ui.notification_show(operation[0], type=operation[1])
        if operation[1] != "warning":
            _employee_instruments_check.set(toolrental.getCheckInstruments())

    
    @reactive.Effect
    @reactive.event(input.button_return_instrument)
    def _():
        operation = toolrental.returnInstrument(input.select_instrument_myself(), input.login())
        ui.notification_show(operation[0], type=operation[1])
        if operation[1] != "warning":
            _employee_instruments_check.set(toolrental.getCheckInstruments())
            _client_instruments_myself.set(toolrental.getClientInstruments(input.login()))
            ui.update_select("select_instrument_myself", choices=dict([(id, id) for id in toolrental.getClientInstruments(input.login())["ID"]]))

    
    @reactive.Effect
    @reactive.event(input.button_rent_instrument)
    def _():
        operation = toolrental.rentInstrument(input.date_instrument_rent(), input.select_instrument_rent(), input.login())
        ui.notification_show(operation[0], type=operation[1])
        if operation[1] != "warning":
            _employee_instruments_check.set(toolrental.getCheckInstruments())
            _client_instruments_myself.set(toolrental.getClientInstruments(input.login()))
            _client_instruments_rent.set(toolrental.getRentInstruments())
            ui.update_select("select_instrument_myself", choices=dict([(id, id) for id in toolrental.getClientInstruments(input.login())["ID"]]))
            ui.update_select("select_instrument_rent", choices=dict([(id, id) for id in toolrental.getRentInstruments()["ID"]]))


app = App(app_ui, server)
