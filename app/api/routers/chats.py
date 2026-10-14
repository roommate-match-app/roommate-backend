"""Чаты и сообщения (UC-7): REST-эндпоинты и WebSocket."""

import uuid

from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.security import decode_access_token
from app.db.database import SessionLocal, get_db
from app.db.models import Chat, Match, Message, Profile, User
from app.db.schemas import ChatOut, MessageCreate, MessageOut, ProfileOut
from app.services.notifications import notify

router = APIRouter(prefix="/api/chats", tags=["Чат (UC-7)"])


class ConnectionManager:
    """Простое хранилище активных WebSocket-подключений по чатам."""

    def __init__(self) -> None:
        self.active: dict[str, list[WebSocket]] = {}

    async def connect(self, chat_id: str, websocket: WebSocket) -> None:
        await websocket.accept()
        self.active.setdefault(chat_id, []).append(websocket)

    def disconnect(self, chat_id: str, websocket: WebSocket) -> None:
        connections = self.active.get(chat_id)
        if connections and websocket in connections:
            connections.remove(websocket)

    async def broadcast(self, chat_id: str, payload: dict) -> None:
        for websocket in list(self.active.get(chat_id, [])):
            await websocket.send_json(payload)


manager = ConnectionManager()


def _participant_chat(db: Session, chat_id: uuid.UUID, user_id: uuid.UUID) -> Chat:
    chat = db.get(Chat, chat_id)
    if chat is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Чат не найден")
    match = db.get(Match, chat.match_id)
    if match is None or user_id not in (match.user1_id, match.user2_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Нет доступа к чату"
        )
    return chat


def _peer_id(chat: Chat, db: Session, user_id: uuid.UUID) -> uuid.UUID:
    match = db.get(Match, chat.match_id)
    return match.user2_id if match.user1_id == user_id else match.user1_id


@router.get("", response_model=list[ChatOut])
def list_chats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[ChatOut]:
    matches = (
        db.query(Match)
        .filter(
            (Match.user1_id == current_user.id) | (Match.user2_id == current_user.id)
        )
        .all()
    )
    result: list[ChatOut] = []
    for match in matches:
        chat = db.query(Chat).filter(Chat.match_id == match.id).first()
        if chat is None:
            continue
        peer_id = match.user2_id if match.user1_id == current_user.id else match.user1_id
        peer = db.query(Profile).filter(Profile.user_id == peer_id).first()
        last = (
            db.query(Message)
            .filter(Message.chat_id == chat.id)
            .order_by(Message.sent_at.desc())
            .first()
        )
        unread = (
            db.query(func.count(Message.id))
            .filter(
                Message.chat_id == chat.id,
                Message.sender_id != current_user.id,
                Message.is_read.is_(False),
            )
            .scalar()
            or 0
        )
        result.append(
            ChatOut(
                id=chat.id,
                match_id=chat.match_id,
                created_at=chat.created_at,
                peer=ProfileOut.model_validate(peer) if peer else None,
                last_message=MessageOut.model_validate(last) if last else None,
                unread_count=int(unread),
            )
        )
    return result


@router.get("/unread-count")
def chats_unread_count(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    """Суммарное число непрочитанных входящих сообщений по всем чатам."""
    total = (
        db.query(func.count(Message.id))
        .join(Chat, Chat.id == Message.chat_id)
        .join(Match, Match.id == Chat.match_id)
        .filter(
            (Match.user1_id == current_user.id) | (Match.user2_id == current_user.id),
            Message.sender_id != current_user.id,
            Message.is_read.is_(False),
        )
        .scalar()
        or 0
    )
    return {"count": int(total)}


@router.get("/{chat_id}/messages", response_model=list[MessageOut])
def read_messages(
    chat_id: uuid.UUID,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[Message]:
    _participant_chat(db, chat_id, current_user.id)
    return (
        db.query(Message)
        .filter(Message.chat_id == chat_id)
        .order_by(Message.sent_at.asc())
        .limit(max(1, min(limit, 500)))
        .all()
    )


@router.post(
    "/{chat_id}/messages",
    response_model=MessageOut,
    status_code=status.HTTP_201_CREATED,
)
def send_message(
    chat_id: uuid.UUID,
    payload: MessageCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Message:
    """Отправить сообщение (UC-7)."""
    chat = _participant_chat(db, chat_id, current_user.id)
    message = Message(chat_id=chat_id, sender_id=current_user.id, content=payload.content)
    db.add(message)
    notify(db, _peer_id(chat, db, current_user.id), "message", "Новое сообщение в чате")
    db.commit()
    db.refresh(message)
    return message


@router.post("/{chat_id}/read", status_code=status.HTTP_204_NO_CONTENT)
def mark_read(
    chat_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> None:
    """Отметить входящие сообщения чата прочитанными."""
    _participant_chat(db, chat_id, current_user.id)
    db.query(Message).filter(
        Message.chat_id == chat_id,
        Message.sender_id != current_user.id,
        Message.is_read.is_(False),
    ).update({"is_read": True})
    db.commit()


@router.websocket("/ws/{chat_id}")
async def chat_websocket(
    websocket: WebSocket, chat_id: uuid.UUID, token: str = ""
) -> None:
    """WebSocket-канал чата. Токен передаётся query-параметром ``token``."""
    subject = decode_access_token(token)
    if subject is None:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    db = SessionLocal()
    try:
        try:
            user_id = uuid.UUID(subject)
        except (ValueError, TypeError):
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return

        chat = db.get(Chat, chat_id)
        match = db.get(Match, chat.match_id) if chat else None
        if match is None or user_id not in (match.user1_id, match.user2_id):
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return

        await manager.connect(str(chat_id), websocket)
        try:
            while True:
                data = await websocket.receive_json()
                content = str(data.get("content", "")).strip()
                if not content:
                    continue
                message = Message(chat_id=chat_id, sender_id=user_id, content=content)
                db.add(message)
                db.commit()
                db.refresh(message)
                await manager.broadcast(
                    str(chat_id),
                    {
                        "id": str(message.id),
                        "chat_id": str(chat_id),
                        "sender_id": str(user_id),
                        "content": content,
                        "sent_at": message.sent_at.isoformat() if message.sent_at else None,
                        "is_read": message.is_read,
                    },
                )
        except WebSocketDisconnect:
            manager.disconnect(str(chat_id), websocket)
    finally:
        db.close()
