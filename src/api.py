import sqlite3
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException, Query
from fastapi.responses import JSONResponse
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from src.auth import DUMMY_HASH, PASSWORDS, decode_token, issue_token, unauthorized
from src.config import Settings
from src.database import Database
from src.decision import DecisionService, InvalidDecision
from src.provider import GeminiProvider, ProviderUnavailable
from src.retrieval import Retriever
from src.schemas import Credentials, HistoryPage, TicketInput, TicketOut, TokenOut, UserOut


def create_app(settings: Settings | None = None, provider=None) -> FastAPI:
    settings = settings or Settings()
    db = Database(settings.database_path)
    provider = provider or GeminiProvider(settings)
    retriever = Retriever(db, provider, settings)
    service = DecisionService(retriever, provider)

    @asynccontextmanager
    async def lifespan(app):
        yield
        provider.close()

    app = FastAPI(
        title="Policy Desk API",
        version="1.0.0",
        description="Authenticated support decisions grounded in the supplied policies.",
        lifespan=lifespan,
    )
    app.state.db, app.state.service = db, service
    bearer = HTTPBearer(auto_error=False)

    def current_user(credentials: HTTPAuthorizationCredentials | None = Depends(bearer)):
        if not credentials or credentials.scheme.lower() != "bearer":
            raise unauthorized()
        user = db.user_by_id(decode_token(credentials.credentials, settings))
        if user is None:
            raise unauthorized()
        return dict(user)

    @app.exception_handler(ProviderUnavailable)
    async def provider_error(request, exc):
        return JSONResponse(status_code=503, content={"detail": str(exc)})

    @app.exception_handler(InvalidDecision)
    async def decision_error(request, exc):
        return JSONResponse(status_code=502, content={"detail": str(exc)})

    @app.get("/health", tags=["Service"])
    def health():
        return {
            "status": "ok",
            "gemini_configured": bool(settings.gemini_api_key.get_secret_value()),
            "model": settings.gemini_model,
            "embedding_model": settings.embedding_model,
            **retriever.status(),
        }

    @app.post("/register", response_model=UserOut, status_code=201, tags=["Account"])
    def register(body: Credentials):
        try:
            return db.create_user(str(body.email), PASSWORDS.hash(body.password))
        except sqlite3.IntegrityError:
            raise HTTPException(409, "An account with this email already exists.") from None

    @app.post("/login", response_model=TokenOut, tags=["Account"])
    def login(body: Credentials):
        user = db.user_by_email(str(body.email))
        valid = PASSWORDS.verify(body.password, user["password_hash"] if user else DUMMY_HASH)
        if not valid or not user:
            raise unauthorized()
        return TokenOut(
            access_token=issue_token(user["id"], settings), expires_in=settings.jwt_expiry_minutes * 60
        )

    @app.get("/me", response_model=UserOut, tags=["Account"])
    def me(user=Depends(current_user)):
        return user

    @app.post("/tickets", response_model=TicketOut, status_code=201, tags=["Tickets"])
    def create_ticket(body: TicketInput, user=Depends(current_user)):
        result = service.decide(body)
        ticket_id = db.save_ticket(
            user["id"],
            body,
            result.decision,
            result.context,
            settings.gemini_model,
            result.policy_version,
            result.latency_ms,
        )
        return db.get_ticket(user["id"], ticket_id)

    @app.get("/tickets", response_model=HistoryPage, tags=["Tickets"])
    def history(
        limit: int = Query(default=20, ge=1, le=100),
        offset: int = Query(default=0, ge=0),
        user=Depends(current_user),
    ):
        return db.list_tickets(user["id"], limit, offset)

    @app.get("/tickets/{ticket_id}", response_model=TicketOut, tags=["Tickets"])
    def get_ticket(ticket_id: int, user=Depends(current_user)):
        ticket = db.get_ticket(user["id"], ticket_id)
        if ticket is None:
            # Same response for non-existent and someone else's tickets.
            raise HTTPException(404, "Ticket not found.")
        return ticket

    return app
