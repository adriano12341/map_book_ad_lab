from tkinter import *
from tkinter import *

import tkintermapview
import requests
from bs4 import BeautifulSoup
import psycopg2 as ps
db_params = ps.connect(database='mapbook',
                       user='postgres',
                       password='test',
                       host='localhost',
                       port='5432'
                       )

#settings
users=[]


class User:
    def __init__(self, name, surname, posts, location):
        self.name = name
        self.surname = surname
        self.posts = posts
        self.location = location
        self.wspolrzedne = User.wspolrzedne(self)
        self.marker = map_widget.set_marker(self.wspolrzedne[0], self.wspolrzedne[1], text=f'{self.name}')

    def wspolrzedne(self)->list:
        url: str = f'https://pl.wikipedia.org/wiki/{self.location}'
        response = requests.get(url)
        response_html = BeautifulSoup(response.text, 'html.parser')
        return [float(response_html.select('.latitude')[1].text.replace(",", ".")),
                float(response_html.select('.longitude')[1].text.replace(",", "."))
                ]

def lista_uzytkownikow():
    cursor = db_params.cursor()
    sql_show_users = 'SELECT * FROM public.users'
    cursor.execute(sql_show_users)
    users = cursor.fetchall()
    cursor.close()
    listbox_lista_obiektow.delete(0, END)
    for idx, user in enumerate(users):
        listbox_lista_obiektow.insert(idx, f'{user[0]}, {user[1]}, {user[2]}, {user[3]}, {user[4]}')


def dodaj_uzytkownika():
    cursor = db_params.cursor()
    imie = entry_imie.get()
    nazwisko = entry_nazwisko.get()
    posty = entry_posty.get()
    lokalizacja = entry_lokalizacja.get()
    print(imie, nazwisko, posty, lokalizacja)
    users.append(User(imie, nazwisko, posty, lokalizacja))
    lista_uzytkownikow()
    sql_insert_user = f"INSERT INTO public.users(name, surname, posts, location) VALUES ('{imie}', '{nazwisko}', '{posty}', '{lokalizacja}');"
    cursor.execute(sql_insert_user)
    db_params.commit()
    cursor.close()



    entry_imie.delete(0, END)
    entry_nazwisko.delete(0, END)
    entry_posty.delete(0, END)
    entry_lokalizacja.delete(0, END)
    entry_imie.focus()

def usun_uzytkownika():
    #cursor = db_params.cursor()
    i = listbox_lista_obiektow.index(ACTIVE)
    print(i)
    #sql_delete_user = f"DELETE FROM public.users WHERE name='{imie}' and surname='{nazwisko}';"
    #cursor.execute(sql_delete_user)
    db_params.commit()
    users[i].marker.delete()
    users.pop(i)
    lista_uzytkownikow()

def pokaz_szczegoly_uzytkownika():
    i = listbox_lista_obiektow.index(ACTIVE)
    imie = users[i].name
    nazwisko = users[i].surname
    posty = users[i].posts
    lokalizacja = users[i].location
    label_imie_szczegoly_obiektu_wartosc.config(text=imie)
    label_nazwisko_szczegoly_obiektu_wartosc.config(text=nazwisko)
    label_posty_szczegoly_obiektu_wartosc.config(text=posty)
    label_lokalizacja_szczegoly_obiektu_wartosc.config(text=lokalizacja)
    map_widget.set_position(users[i].wspolrzedne[0], users[i].wspolrzedne[1])
    map_widget.set_zoom(8)


def edytuj_uzytkownika():
    i = listbox_lista_obiektow.index(ACTIVE)
    entry_imie.insert(0, users[i].name)
    entry_nazwisko.insert(0, users[i].surname)
    entry_posty.insert(0, users[i].posts)
    entry_lokalizacja.insert(0, users[i].location)

    button_dodaj_uzytkownika.config(text="Zapisz zmiany", command=lambda:aktualizuj_uzytkownika(i))
    entry_imie.focus()

def aktualizuj_uzytkownika(i):
    users[i].name = entry_imie.get()
    users[i].surname = entry_nazwisko.get()
    users[i].posts = entry_posty.get()
    users[i].location = entry_lokalizacja.get()
    users[i].wspolrzedne = User.wspolrzedne(users[i])
    users[i].marker.delete()
    users[i].marker = map_widget.set_marker(users[i].wspolrzedne[0], users[i].wspolrzedne[1], text=f'{users[i].name}')
    lista_uzytkownikow()
    button_dodaj_uzytkownika.config(text='Dodaj użytkownika', command=dodaj_uzytkownika)
    entry_imie.delete(0, END)
    entry_nazwisko.delete(0, END)
    entry_posty.delete(0, END)
    entry_lokalizacja.delete(0, END)
    entry_imie.focus()


#GUI
root = Tk()
root.title("MapBook")
root.geometry("1024x700")

#ramki do porządkowania struktury
ramka_lista_obiektow = Frame(root)
ramka_formularz = Frame(root)
ramka_szczegoly_obiektow = Frame(root)

ramka_lista_obiektow.grid(row=0, column=0, padx=50)
ramka_formularz.grid(row=0, column=1)
ramka_szczegoly_obiektow.grid(row=1, column=0, columnspan=2)

#lista obiektow
label_lista_obiektow = Label(ramka_lista_obiektow, text='Lista obiektów: ')
listbox_lista_obiektow = Listbox(ramka_lista_obiektow, width=50)
button_pokaz_szczegoly = Button(ramka_lista_obiektow, text='Pokaż szczegóły', command=pokaz_szczegoly_uzytkownika)
button_usun_obiekt = Button(ramka_lista_obiektow, text='Usuń obiekt', command=usun_uzytkownika)
button_edytuj_obiekt = Button(ramka_lista_obiektow, text='Edytuj obiekt', command=edytuj_uzytkownika)

label_lista_obiektow.grid(row=0, column=0, columnspan=3)
listbox_lista_obiektow.grid(row=1, column=0, columnspan=3)
button_pokaz_szczegoly.grid(row=2, column=0)
button_usun_obiekt.grid(row=2, column=1)
button_edytuj_obiekt.grid(row=2, column=2)

#formularz
label_formularz = Label(ramka_formularz, text='Formularz')
label_imie = Label(ramka_formularz, text='Imię: ')
label_nazwisko = Label(ramka_formularz, text='Nazwisko: ')
label_posty = Label(ramka_formularz, text='Liczba postów: ')
label_lokalizacja = Label(ramka_formularz, text='Lokalizacja: ')

entry_imie = Entry(ramka_formularz)
entry_nazwisko = Entry(ramka_formularz)
entry_posty = Entry(ramka_formularz)
entry_lokalizacja = Entry(ramka_formularz)

label_formularz.grid(row=0, column=0, columnspan=2)
label_imie.grid(row=1, column=0, sticky=W)
label_nazwisko.grid(row=2, column=0, sticky=W)
label_posty.grid(row=3, column=0, sticky=W)
label_lokalizacja.grid(row=4, column=0, sticky=W)

entry_imie.grid(row=1, column=1)
entry_nazwisko.grid(row=2, column=1)
entry_posty.grid(row=3, column=1)
entry_lokalizacja.grid(row=4, column=1)

button_dodaj_uzytkownika = Button(ramka_formularz, text='Dodaj użytkownika', command=dodaj_uzytkownika)
button_dodaj_uzytkownika.grid(row=5, column=1, columnspan=2)

#szczegóły obiektów

label_szczegoly_obiektu = Label(ramka_szczegoly_obiektow, text='Szczegóły użytkownika: ')
label_imie_szczegoly_obiektu = Label(ramka_szczegoly_obiektow, text='Imię: ')
label_nazwisko_szczegoly_obiektu = Label(ramka_szczegoly_obiektow, text='Nazwisko: ')
label_posty_szczegoly_obiektu = Label(ramka_szczegoly_obiektow, text='Liczba postów: ')
label_lokalizacja_szczegoly_obiektu = Label(ramka_szczegoly_obiektow, text='Lokalizacja: ')

label_imie_szczegoly_obiektu_wartosc = Label(ramka_szczegoly_obiektow, text='...')
label_nazwisko_szczegoly_obiektu_wartosc = Label(ramka_szczegoly_obiektow, text='...')
label_posty_szczegoly_obiektu_wartosc = Label(ramka_szczegoly_obiektow, text='...')
label_lokalizacja_szczegoly_obiektu_wartosc = Label(ramka_szczegoly_obiektow, text='...')

label_szczegoly_obiektu.grid(row=0, column=0, sticky=W)
label_imie_szczegoly_obiektu.grid(row=1, column=0, sticky=W)
label_posty_szczegoly_obiektu_wartosc.grid(row=1, column=1)
label_nazwisko_szczegoly_obiektu.grid(row=1, column=2)
label_nazwisko_szczegoly_obiektu_wartosc.grid(row=1, column=3)
label_posty_szczegoly_obiektu.grid(row=1, column=4)
label_posty_szczegoly_obiektu_wartosc.grid(row=1, column=5)
label_lokalizacja_szczegoly_obiektu.grid(row=1, column=6)
label_lokalizacja_szczegoly_obiektu_wartosc.grid(row=1, column=7)

map_widget = tkintermapview.TkinterMapView(ramka_szczegoly_obiektow, width=1000, height=500)
map_widget.set_position(52.2, 21.0)
map_widget.set_zoom(8)
marker_WAT = map_widget.set_marker(52.25376421641225, 20.904509204119396, text="WAT")



map_widget.grid(row=2, column=0, columnspan=8)


root.mainloop()
