# 1. Library imports
import uvicorn
from fastapi import BackgroundTasks, FastAPI
from pydantic import BaseModel
from app.selenium_medium import getAndSaveArticle, convert_epub, convert_mobi, send2kindle
import os 

def medium2kindle(site):
    markd = getAndSaveArticle(site)
    epub = convert_epub(markd)
    mobi, epubFile = convert_mobi(epub)
    send2kindle(mobi)
    os.remove(epubFile)
    os.remove(mobi)
    return mobi

class Article(BaseModel):
    article_url : str

app = FastAPI()

@app.post('/Article')
async def medium_url(url : Article, background_tasks: BackgroundTasks):
    data = url.dict()
    background_tasks.add_task(medium2kindle, data['article_url'])
    return {'message': "Sending in background"}

if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0')
