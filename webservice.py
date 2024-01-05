import json
import sys
from datetime import datetime
from pathlib import Path

import uvicorn
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from starlette.requests import Request
from starlette.responses import HTMLResponse
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from starlette.templating import Jinja2Templates

from pdu import PDU

app = FastAPI()
templates = Jinja2Templates(directory="web")


@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "sockets": app.state.plug_data})


class PlugData(BaseModel):
    name: str
    state: int


@app.get("/api/devices/plugs")
def getPlugData():
    plug_data = app.state.plug_data
    for state, i in zip(app.state.pdu.getRelayState(), range(16)):
        plug_data[i]["state"] = int(state)

    return JSONResponse(plug_data)


@app.post("/api/devices/plugs/{plug_id}")
def setPlugData(plug_id: int, plug_data: PlugData):
    plug = app.state.plug_data[plug_id - 1]
    plug["name"] = plug_data.name

    if app.state.pdu.getRelayState()[plug_id - 1] != plug_data.state:
        plug["stateLastUpdated"] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        app.state.pdu.modifyRelayState(plug_id, plug_data.state)
        app.state.pdu.updateRelays()

    savePlugData()
    return JSONResponse({"state": app.state.pdu.getRelayState()[plug_id - 1]})


def createDefaultPlugData() -> list:
    data = []
    for i in range(1, 17):
        data.append({
            "id": i,
            "name": f"plug_{i}",
            "stateLastUpdated": ""
        })

    with open("plug_data.json", "w+") as file:
        file.write(json.dumps(data, indent=4))
        file.flush()

    return data


def savePlugData():
    with open("plug_data.json", "w+") as file:
        file.write(json.dumps(app.state.plug_data, indent=4))
        file.flush()


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Missing args: Serial Port")
        sys.exit(1)

    app.state.pdu = PDU(sys.argv[1])

    if not Path("plug_data.json").exists():
        app.state.plug_data = createDefaultPlugData()
    else:
        with open("plug_data.json", "r") as file:
            app.state.plug_data = json.loads(file.read())

    uvicorn.run(app, port=80)
