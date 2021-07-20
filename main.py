from typing import Optional
from fastapi import FastAPI, Request, APIRouter
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from pathlib import Path

#configurating app
app = FastAPI()
templates = Jinja2Templates(directory='templates')
app.mount("/static",
          StaticFiles(directory=Path(__file__).parent.parent.absolute()/'static'),
          name='static')

class Item(BaseModel):
    name: str
    price: float
    is_offer: Optional[bool] = None


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/register" ,response_class=HTMLResponse)
def read_item(request:Request):
    return templates.TemplateResponse('register.html',{'request':request})


@app.post('/register')
async def bruh(request:Request):
    form_data = await request.form()
    print(form_data)
    login=form_data['login']
    password=form_data['password']
    password2=form_data['password_repeated']
    if password!=password2 or password2=='' or password2=='':
        return templates.TemplateResponse('register.html', {'request': request, 'message':''})
    file=form_data['file']
    if file.filename!='':
        file = form_data['file']
        print(file)
        print(file.filename)
        print(file.filename)
    else:
        print('default')

        #default pfp

@app.put("/items/{item_id}")
def update_item(item_id: int, item: Item):
    return {"item_name": item.name, "item_id": item_id}
# Press the green button in the gutter to run the script.
#if __name__ == '__main__':
#    app.run()
# See PyCharm help at https://www.jetbrains.com/help/pycharm/
