from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from lingua import Language, LanguageDetectorBuilder
import wikipedia
import pyjokes
from pydantic import BaseModel
from requests import exceptions

app = FastAPI()

languages = [Language.ENGLISH, Language.FRENCH, Language.GERMAN, Language.SPANISH, Language.RUSSIAN]
detector = LanguageDetectorBuilder.from_languages(*languages).build()


class Coordinates(BaseModel):
    latitude: float
    longtitude: float


@app.get("/")
def main():
    return f"Joker says: {pyjokes.get_joke()}"


@app.get('/ptw/{name}', response_class=HTMLResponse)
def path_to_wiki(name: str):
    try:
        check_lang = detector.detect_language_of(name)
        lang = str(check_lang)[9:11].lower()
        wikipedia.set_lang(lang)
        result = wikipedia.search(name)[0]
        if lang == 'ru':
            return f"Вы нашли {result} в Википедия"
        else:
            return f"You have found {result} in Wikipedia"
    except IndexError:
        return f"This page doesn`t exits or you`ve misspelled it :^("


@app.get('/ptwq/{name}', response_class=HTMLResponse)
def path_to_wiki(name: str, long: bool = False):
    try:
        check_lang = detector.detect_language_of(name)
        lang = str(check_lang)[9:11].lower()
        wikipedia.set_lang(lang)
        if not long:
            result = wikipedia.search(name)[0]
            definition = wikipedia.summary(result, auto_suggest=False, redirect=True)
            return str(definition).replace("\n", "<br/>")
        result = wikipedia.page(name).content
        return str(result).replace("\n", "<br/>")
    except exceptions.ConnectionError:
        return f"This page doesn`t exits or you`ve misspelled it :^("


@app.post('/coordinates')
def wikigeo(coordinates: Coordinates):
    try:
        return wikipedia.geosearch(coordinates.latitude, coordinates.longtitude)
    except exceptions.ConnectionError:
        return f"I can`t find anything with this coordinates"
