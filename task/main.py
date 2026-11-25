import os
import random
from datetime import datetime
from typing import List, Optional, Dict, Any
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

app = FastAPI(
    title="Today's Roulette Desktop App API",
    description="Backend API for Today's Roulette - Daily Missions, Menus, and Items",
    version="1.0.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------------------------------------------------
# Data Pools
# -------------------------------------------------------------

MENU_POOL = [
    {
        "id": "menu_1",
        "title": "따끈한 유부우동 + 계란말이",
        "description": "배달이나 전자레인지로 5분 만에 준비할 수 있어 설거지 부담이 거의 없는 한 끼예요.",
        "budget": "예산 12,000원 이하",
        "modes": ["home", "any"],
        "tags": ["comfort", "easy", "soup"],
        "exclusions": []
    },
    {
        "id": "menu_2",
        "title": "바질 페스토 파스타 또는 크림 리조또",
        "description": "향긋한 허브 향으로 기분 전환이 되는 간편한 양식 브런치 메뉴예요.",
        "budget": "예산 15,000원 이하",
        "modes": ["home", "any"],
        "tags": ["brunch", "pasta"],
        "exclusions": ["dairy"]
    },
    {
        "id": "menu_3",
        "title": "편의점 훈제란 + 바나나 우유 세트",
        "description": "조리 과정 전혀 없이 3분 컷으로 가볍게 배를 채울 수 있는 꿀조합이에요.",
        "budget": "예산 6,000원 이하",
        "modes": ["home", "walk", "any"],
        "tags": ["quick", "light"],
        "exclusions": ["dairy"]
    },
    {
        "id": "menu_4",
        "title": "동네 빵집 소금빵과 따뜻한 라떼",
        "description": "가볍게 밖으로 걸어나가 갓 구운 빵 냄새를 맡으며 사 오는 소소한 행복이에요.",
        "budget": "예산 8,000원 이하",
        "modes": ["walk", "any"],
        "tags": ["bakery", "coffee", "walk"],
        "exclusions": ["caffeine", "dairy"]
    },
    {
        "id": "menu_5",
        "title": "참치마요 주먹밥 + 진한 컵라면",
        "description": "가장 익숙하지만 언제 먹어도 마음까지 편안해지는 초간단 소울푸드 조합입니다.",
        "budget": "예산 5,000원 이하",
        "modes": ["home", "any"],
        "tags": ["quick", "convenient"],
        "exclusions": ["spicy"]
    },
    {
        "id": "menu_6",
        "title": "따뜻한 계란찜과 야채 김밥",
        "description": "속이 부대끼지 않고 편안하면서도 균형 잡힌 든든한 분식 식사예요.",
        "budget": "예산 7,000원 이하",
        "modes": ["home", "walk", "any"],
        "tags": ["mild", "healthy"],
        "exclusions": []
    },
    {
        "id": "menu_7",
        "title": "신선한 연어 포케 샐러드 볼",
        "description": "몸이 무겁지 않고 상쾌한 에너지를 채워주는 알록달록한 한 그릇 요리입니다.",
        "budget": "예산 14,000원 이하",
        "modes": ["walk", "any"],
        "tags": ["salad", "healthy"],
        "exclusions": ["seafood"]
    },
    {
        "id": "menu_8",
        "title": "얼큰한 김치찌개 백반과 김",
        "description": "한국인의 소울푸드! 매콤하고 진한 국물로 잠든 입맛을 깨워보세요.",
        "budget": "예산 9,000원 이하",
        "modes": ["home", "walk", "any"],
        "tags": ["spicy", "korean"],
        "exclusions": ["spicy"]
    }
]

MISSION_POOL = [
    {
        "id": "mission_1",
        "title": "좋아하는 노래 10곡 플레이리스트 만들기",
        "description": "지금 기분에 딱 어울리는 곡들만 10개 골라 나만의 작은 플레이리스트 이름을 지어보세요.",
        "estimated_time": "15분",
        "cost_type": "무료",
        "modes": ["home", "walk", "any"],
        "tags": ["music", "healing", "easy"],
        "exclusions": []
    },
    {
        "id": "mission_2",
        "title": "관심 가는 주식 1주 살펴보고 사기",
        "description": "평소 자주 쓰는 브랜드의 주가 흐름을 5분만 구경하고, 커피 한 잔 값으로 응원해보세요.",
        "estimated_time": "10분",
        "cost_type": "소액 투자",
        "modes": ["home", "any"],
        "tags": ["finance", "learning"],
        "exclusions": []
    },
    {
        "id": "mission_3",
        "title": "창문 열고 3분 동안 바깥 공기 마시기",
        "description": "잠깐 창가에 서서 구름이나 나무를 바라보며 깊게 숨을 한 번 들이마셔 보세요.",
        "estimated_time": "3분",
        "cost_type": "무료",
        "modes": ["home", "any"],
        "tags": ["refresh", "quick"],
        "exclusions": []
    },
    {
        "id": "mission_4",
        "title": "책상 위 안 쓰는 영수증 3장만 버리기",
        "description": "주변을 전부 치우려 하지 말고, 딱 눈에 보이는 불필요한 종이 3장만 휴지통에 쏙 버려보세요.",
        "estimated_time": "5분",
        "cost_type": "무료",
        "modes": ["home", "any"],
        "tags": ["clean", "quick"],
        "exclusions": []
    },
    {
        "id": "mission_5",
        "title": "편의점 걸어가서 새로운 음료 하나 골라보기",
        "description": "햇볕을 쬐며 동네 편의점까지 천천히 걸어가서 평소 안 마셔본 색다른 음료를 골라보세요.",
        "estimated_time": "15분",
        "cost_type": "소액 (3천원 이하)",
        "modes": ["walk", "any"],
        "tags": ["walk", "drink"],
        "exclusions": []
    },
    {
        "id": "mission_6",
        "title": "동네 길목의 하늘이나 꽃 사진 1장 찍기",
        "description": "길을 걷다 우연히 시선이 머문 하늘이나 가로수를 폰 카메라에 한 장 담아보세요.",
        "estimated_time": "10분",
        "cost_type": "무료",
        "modes": ["walk", "any"],
        "tags": ["walk", "photo"],
        "exclusions": []
    },
    {
        "id": "mission_7",
        "title": "오래된 친구에게 귀여운 이모티콘 하나 보내기",
        "description": "긴 안부 인사 대신 가벼운 인사 이모티콘 하나로 따뜻한 연결감을 느껴보세요.",
        "estimated_time": "2분",
        "cost_type": "무료",
        "modes": ["home", "walk", "any"],
        "tags": ["social", "quick"],
        "exclusions": ["phone_call"]
    },
    {
        "id": "mission_8",
        "title": "따뜻한 물 한 잔 천천히 마시며 어깨 스트레칭",
        "description": "스마트폰을 내려놓고 따뜻한 물을 음미하며 굳어있던 목과 어깨를 부드럽게 풀어주세요.",
        "estimated_time": "5분",
        "cost_type": "무료",
        "modes": ["home", "any"],
        "tags": ["body", "relax"],
        "exclusions": []
    }
]

ITEM_POOL = [
    {
        "id": "item_1",
        "title": "보라색 양말 또는 포근한 담요",
        "description": "발끝이나 무릎을 따뜻하게 감싸주는 물건 하나만 곁에 두어도 기분이 한결 편안해져요.",
        "category": "오늘의 부적",
        "modes": ["home", "any"]
    },
    {
        "id": "item_2",
        "title": "민트색 머그컵 또는 촉촉한 립밤",
        "description": "자주 손이 닿는 작은 물건 하나가 오늘 하루의 산뜻한 기분 전환 포인트가 되어줄 거예요.",
        "category": "기분 전환 아이템",
        "modes": ["home", "walk", "any"]
    },
    {
        "id": "item_3",
        "title": "무선 이어폰과 작은 손거울",
        "description": "세상의 소음을 줄이고 나만의 리듬에 집중할 수 있게 도와주는 든든한 동반자입니다.",
        "category": "외출 및 집중템",
        "modes": ["walk", "any"]
    },
    {
        "id": "item_4",
        "title": "노란색 포스트잇과 부드러운 볼펜",
        "description": "머릿속에 떠오른 소소한 낙서나 문장 하나를 가볍게 적어둘 수 있는 작은 여백이에요.",
        "category": "영감 아이템",
        "modes": ["home", "any"]
    },
    {
        "id": "item_5",
        "title": "좋아하는 향의 핸드크림",
        "description": "손을 씻은 뒤 은은하게 퍼지는 향기로 순간의 스트레스를 지워보세요.",
        "category": "힐링 소지품",
        "modes": ["home", "walk", "any"]
    },
    {
        "id": "item_6",
        "title": "가벼운 면 에코백과 비상용 1만원 지폐",
        "description": "지갑 없이도 홀가분하게 동네를 탐험할 수 있는 자유를 선사합니다.",
        "category": "산책 필수템",
        "modes": ["walk", "any"]
    }
]

# Admin email whitelist
ALLOWED_ADMIN_EMAILS = {
    "admin@todaysroulette.kr",
    "admin@gmail.com",
    "gksch@gmail.com",
    "manager@todaysroulette.com"
}
# Expand with environment variable if configured
env_admins = os.getenv("ALLOWED_ADMIN_EMAILS", "")
if env_admins:
    for email in env_admins.split(","):
        if email.strip():
            ALLOWED_ADMIN_EMAILS.add(email.strip().lower())

# -------------------------------------------------------------
# Request & Response Schemas
# -------------------------------------------------------------

class DrawRequest(BaseModel):
    mode: Optional[str] = Field("home", description="에너지 모드: home(집콕), walk(산책), any(무난/상관없음)")
    exclusions: Optional[List[str]] = Field(default_factory=list, description="제외 필터 리스트")

class DrawResponse(BaseModel):
    success: bool = True
    mode: str
    mode_label: str
    menu: Dict[str, Any]
    mission: Dict[str, Any]
    item: Dict[str, Any]
    timestamp: str

class ChatRequest(BaseModel):
    message: str = Field(..., description="사용자 질문 메시지")
    context: Optional[Dict[str, Any]] = Field(default=None, description="현재 뽑힌 메뉴, 미션, 아이템 정보")

class ChatResponse(BaseModel):
    reply: str
    allowed: bool
    topic: Optional[str] = None

class AdminAuthRequest(BaseModel):
    email: str = Field(..., description="관리자 로그인 이메일")

class AdminAuthResponse(BaseModel):
    success: bool
    email: str
    role: Optional[str] = None
    message: str
    token: Optional[str] = None

# -------------------------------------------------------------
# API Endpoints
# -------------------------------------------------------------

@app.get("/")
def health_check():
    """Health check endpoint for Cloud Run and monitoring."""
    return {
        "status": "ok",
        "service": "Today's Roulette Desktop App API",
        "version": "1.0.0",
        "time": datetime.utcnow().isoformat() + "Z"
    }

@app.post("/api/draw", response_model=DrawResponse)
def api_draw(req: DrawRequest):
    """
    에너지 모드(집콕/산책/무난 등)와 제외 필터를 반영하여
    '오늘의 메뉴', '오늘의 소소한 행동', '오늘의 소지품/아이템' 3종 세트를 랜덤 반환합니다.
    """
    raw_mode = (req.mode or "home").lower().strip()
    if raw_mode in ["home", "집콕", "침대 밖은 위험해", "침대 밖은 위험해 (집콕)"]:
        mode_key = "home"
        mode_label = "침대 밖은 위험해 (집콕)"
    elif raw_mode in ["walk", "산책", "동네 산책 가능"]:
        mode_key = "walk"
        mode_label = "동네 산책 가능"
    else:
        mode_key = "any"
        mode_label = "아무거나 상관없음"

    # Normalize exclusions
    normalized_exclusions = set()
    for exc in (req.exclusions or []):
        exc_clean = exc.strip().lower()
        if "매운" in exc_clean or "spicy" in exc_clean:
            normalized_exclusions.add("spicy")
        elif "유제품" in exc_clean or "dairy" in exc_clean:
            normalized_exclusions.add("dairy")
        elif "해산물" in exc_clean or "seafood" in exc_clean:
            normalized_exclusions.add("seafood")
        elif "카페인" in exc_clean or "caffeine" in exc_clean or "커피" in exc_clean:
            normalized_exclusions.add("caffeine")
        elif "전화" in exc_clean or "call" in exc_clean:
            normalized_exclusions.add("phone_call")
        else:
            normalized_exclusions.add(exc_clean)

    # Filter Menus
    eligible_menus = [
        m for m in MENU_POOL
        if (mode_key in m["modes"] or mode_key == "any")
        and not any(tag in normalized_exclusions for tag in m.get("exclusions", []))
    ]
    if not eligible_menus:
        eligible_menus = MENU_POOL

    # Filter Missions
    eligible_missions = [
        m for m in MISSION_POOL
        if (mode_key in m["modes"] or mode_key == "any")
        and not any(tag in normalized_exclusions for tag in m.get("exclusions", []))
    ]
    if not eligible_missions:
        eligible_missions = MISSION_POOL

    # Filter Items
    eligible_items = [
        it for it in ITEM_POOL
        if (mode_key in it["modes"] or mode_key == "any")
    ]
    if not eligible_items:
        eligible_items = ITEM_POOL

    selected_menu = random.choice(eligible_menus)
    selected_mission = random.choice(eligible_missions)
    selected_item = random.choice(eligible_items)

    return DrawResponse(
        success=True,
        mode=mode_key,
        mode_label=mode_label,
        menu=selected_menu,
        mission=selected_mission,
        item=selected_item,
        timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    )

@app.post("/api/chat", response_model=ChatResponse)
def api_chat(req: ChatRequest):
    """
    미션/메뉴/소지품 등 허용된 주제 질문에는 AI 도우미 답변을 반환하고,
    무관한 주제의 질문에는 반드시 지정된 거절 문구를 반환합니다.
    """
    msg = req.message.strip().lower()
    ctx = req.context or {}

    # Strict restriction response required by specification
    STRICT_REJECT_MESSAGE = "죄송합니다. 안내된 주제와 관련된 질문에만 답변할 수 있습니다."

    # Allowed topic keywords
    allowed_keywords = [
        "미션", "행동", "할일", "소소", "추천", "플레이리스트", "음악", "노래", "곡",
        "메뉴", "음식", "밥", "우동", "라면", "파스타", "식사", "배달", "점심", "저녁", "아침",
        "소지품", "아이템", "양말", "담요", "머그컵", "립밤", "이어폰", "에코백", "부적", "준비물",
        "산책", "집콕", "컨디션", "에너지", "기분", "어디서", "어떻게", "팁", "꿀팁", "노하우",
        "주식", "1주", "책상", "영수증", "창문", "환기", "스트레칭", "이모티콘", "물",
        "룰렛", "뽑기", "다시", "완료", "도우미", "안녕", "도와줘", "뭐할까"
    ]

    # Explicit blocked domain keywords (coding, politics, general knowledge trivia, etc.)
    blocked_keywords = [
        "주식 종목 추천", "리딩방", "매수 타이밍", "코딩", "파이썬", "자바", "알고리즘", "코드 짜줘",
        "대통령", "선거", "정치", "국회", "의원", "전쟁", "비트코인 시세", "코인 리딩",
        "수학 문제", "영어 번역기", "철학이란", "사주팔자", "운세 풀이"
    ]

    # Check for explicitly blocked topics first
    if any(b in msg for b in blocked_keywords):
        return ChatResponse(
            reply=STRICT_REJECT_MESSAGE,
            allowed=False,
            topic="blocked"
        )

    # Check if the query contains any of the allowed keywords or references current context
    menu_title = str(ctx.get("menu", {}).get("title", "")).lower()
    mission_title = str(ctx.get("mission", {}).get("title", "")).lower()
    item_title = str(ctx.get("item", {}).get("title", "")).lower()

    matches_context = any(word in msg for word in [menu_title, mission_title, item_title] if len(word) > 2)
    matches_allowed = any(k in msg for k in allowed_keywords)

    if not (matches_context or matches_allowed):
        return ChatResponse(
            reply=STRICT_REJECT_MESSAGE,
            allowed=False,
            topic="unrelated"
        )

    # Generate context-aware assistant response
    if "플레이리스트" in msg or "노래" in msg or "음악" in msg:
        reply = (
            "지금 기분에 어울리는 10곡 플레이리스트 아이디어를 드릴게요!\n"
            "1. 푹신한 담요 속에서 듣는 어쿠스틱/로파이 곡 10선\n"
            "2. 따뜻한 음식을 기다리며 가볍게 흥얼거리는 인디 팝\n"
            "3. 학창 시절 가장 좋아했던 추억의 가요 모음\n"
            "곡 선정에 부담 갖지 마시고, 첫 곡은 지금 머릿속에 바로 떠오르는 노래로 채워보세요!"
        )
    elif "어디서" in msg or "장소" in msg or "위치" in msg:
        reply = (
            "집 안이라면 햇빛이 살짝 드는 창가나 소파 구석이 가장 집중하기 좋아요. "
            "외출 미션이라면 동네에서 평소 지나치기만 했던 벤치나 공원 산책로를 걸어보시는 걸 추천합니다!"
        )
    elif "메뉴" in msg or "우동" in msg or "음식" in msg or "배고파" in msg or "레시피" in msg:
        menu_name = ctx.get("menu", {}).get("title", "따끈한 국물 요리")
        reply = (
            f"오늘 뽑힌 메뉴는 [{menu_name}]예요! "
            "배달로 편하게 주문하시거나, 편의점 즉석식품으로 간편하게 준비해도 충분히 훌륭합니다. "
            "식사 후 따뜻한 차 한 잔 곁들이면 더 완벽해요."
        )
    elif "소지품" in msg or "아이템" in msg or "담요" in msg or "양말" in msg:
        item_name = ctx.get("item", {}).get("title", "포근한 아이템")
        reply = (
            f"오늘의 행운 아이템 [{item_name}]은 곁에 두는 것만으로도 안정감을 줘요. "
            "손이 닿는 책상 위나 외출용 가방 앞주머니에 가볍게 챙겨두세요!"
        )
    elif "주식" in msg:
        reply = (
            "‘관심 가는 주식 1주 살펴보기’는 큰돈을 버는 목적이 아니라, "
            "내가 자주 쓰는 서비스나 애정하는 브랜드의 주주가 되어보는 가벼운 경험이에요. "
            "평소 자주 쓰는 앱이나 커피 브랜드의 1주 가격을 구경해보는 것부터 시작해보세요!"
        )
    else:
        mission_name = ctx.get("mission", {}).get("title", "오늘의 소소한 행동")
        reply = (
            f"오늘의 미션인 [{mission_name}]은 절대 완벽하게 끝낼 필요가 없어요. "
            "3분만 발을 담가본다는 마음으로 가볍게 시작해보시면 기분 좋은 성취감을 느끼실 수 있을 거예요. 언제든 더 물어보세요!"
        )

    return ChatResponse(
        reply=reply,
        allowed=True,
        topic="mission_helper"
    )

@app.post("/api/admin/auth", response_model=AdminAuthResponse)
def api_admin_auth(req: AdminAuthRequest):
    """
    관리자 이메일 계정을 검증하고 인증 토큰을 반환합니다.
    """
    email_clean = req.email.strip().lower()

    if email_clean in ALLOWED_ADMIN_EMAILS:
        # Generate simple session token for authorized admin
        fake_token = f"roulette_adm_{abs(hash(email_clean))}_{int(datetime.utcnow().timestamp())}"
        return AdminAuthResponse(
            success=True,
            email=email_clean,
            role="admin",
            message="관리자 인증에 성공하였습니다.",
            token=fake_token
        )
    else:
        return AdminAuthResponse(
            success=False,
            email=email_clean,
            role=None,
            message="허가되지 않은 관리자 계정입니다. 등록된 이메일로 다시 시도해 주세요.",
            token=None
        )

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
