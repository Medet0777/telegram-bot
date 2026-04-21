import os
import secrets
from pathlib import Path
from fastapi import FastAPI, Request, Form, Depends, HTTPException, status
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware
from sqlalchemy import select, desc, func
from dotenv import load_dotenv

from shared.db import SessionLocal, init_db
from shared.models import Message, Session as SessionModel, AdminReply, Status, Category
from shared.models import CATEGORY_LABELS_KZ, STATUS_LABELS_KZ
from admin.telegram_send import send_admin_reply

load_dotenv()

BASE_DIR = Path(__file__).parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

app = FastAPI(title="Анонимді қолдау — Әкімші панелі")
app.add_middleware(SessionMiddleware, secret_key=os.getenv("SESSION_SECRET", secrets.token_hex(16)))
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")


def _admin_creds() -> tuple[str, str]:
    return os.getenv("ADMIN_USERNAME", "admin"), os.getenv("ADMIN_PASSWORD", "admin")


def require_auth(request: Request):
    if not request.session.get("user"):
        raise HTTPException(status_code=status.HTTP_303_SEE_OTHER, headers={"Location": "/login"})


@app.on_event("startup")
async def _startup():
    await init_db()


@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request, "error": None})


@app.post("/login")
async def login_submit(request: Request, username: str = Form(...), password: str = Form(...)):
    u, p = _admin_creds()
    if secrets.compare_digest(username, u) and secrets.compare_digest(password, p):
        request.session["user"] = username
        return RedirectResponse("/", status_code=303)
    return templates.TemplateResponse(
        "login.html", {"request": request, "error": "Қате логин немесе құпиясөз"}, status_code=401
    )


@app.get("/logout")
async def logout(request: Request):
    request.session.clear()
    return RedirectResponse("/login", status_code=303)


@app.get("/", response_class=HTMLResponse)
async def index(request: Request, status_filter: str = "", category_filter: str = "", _: None = Depends(require_auth)):
    async with SessionLocal() as db:
        stmt = select(Message).order_by(desc(Message.created_at))
        if status_filter:
            stmt = stmt.where(Message.status == status_filter)
        if category_filter:
            stmt = stmt.where(Message.category == category_filter)
        result = await db.execute(stmt)
        messages = result.scalars().all()

        counts_stmt = select(Message.status, func.count()).group_by(Message.status)
        counts = dict((await db.execute(counts_stmt)).all())

    return templates.TemplateResponse(
        "list.html",
        {
            "request": request,
            "messages": messages,
            "categories": list(Category),
            "statuses": list(Status),
            "cat_labels": CATEGORY_LABELS_KZ,
            "status_labels": STATUS_LABELS_KZ,
            "status_filter": status_filter,
            "category_filter": category_filter,
            "counts": counts,
        },
    )


@app.get("/msg/{msg_id}", response_class=HTMLResponse)
async def view_message(msg_id: int, request: Request, _: None = Depends(require_auth)):
    async with SessionLocal() as db:
        msg = await db.get(Message, msg_id)
        if not msg:
            raise HTTPException(404)
        session = await db.get(SessionModel, msg.session_id)
        replies_stmt = select(AdminReply).where(AdminReply.message_id == msg_id).order_by(AdminReply.sent_at)
        replies = (await db.execute(replies_stmt)).scalars().all()

    return templates.TemplateResponse(
        "view.html",
        {
            "request": request,
            "msg": msg,
            "session": session,
            "replies": replies,
            "statuses": list(Status),
            "cat_labels": CATEGORY_LABELS_KZ,
            "status_labels": STATUS_LABELS_KZ,
        },
    )


@app.post("/msg/{msg_id}/status")
async def change_status(msg_id: int, new_status: str = Form(...), _: None = Depends(require_auth)):
    async with SessionLocal() as db:
        msg = await db.get(Message, msg_id)
        if not msg:
            raise HTTPException(404)
        msg.status = new_status
        await db.commit()
    return RedirectResponse(f"/msg/{msg_id}", status_code=303)


@app.post("/msg/{msg_id}/reply")
async def reply_to_msg(msg_id: int, reply_text: str = Form(...), _: None = Depends(require_auth)):
    reply_text = reply_text.strip()
    if not reply_text:
        return RedirectResponse(f"/msg/{msg_id}", status_code=303)

    async with SessionLocal() as db:
        msg = await db.get(Message, msg_id)
        if not msg:
            raise HTTPException(404)
        session = await db.get(SessionModel, msg.session_id)
        db.add(AdminReply(message_id=msg_id, content=reply_text))
        if msg.status == Status.NEW.value:
            msg.status = Status.IN_PROGRESS.value
        await db.commit()
        chat_id = session.tg_chat_id

    await send_admin_reply(chat_id, reply_text)
    return RedirectResponse(f"/msg/{msg_id}", status_code=303)
