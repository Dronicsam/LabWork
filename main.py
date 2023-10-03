from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from lingua import Language, LanguageDetectorBuilder
import wikipedia
import pyjokes
from pydantic import BaseModel
from requests import exceptions
from fastapi import HTTPException

app = FastAPI()

languages = [Language.ENGLISH, Language.FRENCH, Language.GERMAN, Language.SPANISH, Language.RUSSIAN]
detector = LanguageDetectorBuilder.from_languages(*languages).build()


class Coordinates(BaseModel):
    latitude: float
    longtitude: float


class PostResponse(BaseModel):
    cities: list[str]


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
def path_to_wiki_query(name: str, long: bool = False):
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
        raise HTTPException(404, detail="This page doesn`t exits or you`ve misspelled it :^(")


@app.post('/coordinates', response_model=PostResponse)
def wikigeo(coordinates: Coordinates):
    try:
        response = PostResponse(cities=wikipedia.geosearch(coordinates.latitude, coordinates.longtitude))
        return response
    except exceptions.ConnectionError:
        raise HTTPException(404, detail="I can`t find anything")
