import os
from typing import List, Optional
from dotenv import load_dotenv

load_dotenv()

class Config:
    BOT_TOKEN: str = os.getenv("BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")
    ADMIN_GROUP_ID: int = int(os.getenv("ADMIN_GROUP_ID", "0"))
    
    # Comma-separated admin IDs
    _super_admins_raw: str = os.getenv("SUPER_ADMIN_IDS", "")
    SUPER_ADMIN_IDS: List[int] = [
        int(x.strip()) for x in _super_admins_raw.split(",") if x.strip().isdigit()
    ]
    
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///express_tour.db")
    REDIS_URL: Optional[str] = os.getenv("REDIS_URL")
    
    # Company info
    COMPANY_NAME: str = os.getenv("COMPANY_NAME", "Express Tour")
    COMPANY_PHONE: str = os.getenv("COMPANY_PHONE", "+998 90 988 41 11")
    COMPANY_TELEGRAM: str = os.getenv("COMPANY_TELEGRAM", "@expresstouradmin")
    COMPANY_INSTAGRAM: str = os.getenv("COMPANY_INSTAGRAM", "@express_tour_uz")
    COMPANY_ADDRESS: str = os.getenv("COMPANY_ADDRESS", "Ahmad Donish 1A, Yunusobod, Toshkent")
    COMPANY_WORK_HOURS: str = os.getenv("COMPANY_WORK_HOURS", "Dushanba - Shanba: 09:00 - 19:00")
    COMPANY_LAT: float = float(os.getenv("COMPANY_LAT", "41.366488"))
    COMPANY_LON: float = float(os.getenv("COMPANY_LON", "69.293553"))
    GOOGLE_MAPS_URL: str = os.getenv("GOOGLE_MAPS_URL", "https://maps.app.goo.gl/cnQW2F6ANuaLQoj17")

config = Config()

def update_admin_group_id(group_id: int):
    config.ADMIN_GROUP_ID = group_id
    env_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
    if os.path.exists(env_file):
        try:
            with open(env_file, "r", encoding="utf-8") as f:
                content = f.read()
            import re
            if re.search(r"^ADMIN_GROUP_ID=.*", content, flags=re.MULTILINE):
                new_content = re.sub(r"^ADMIN_GROUP_ID=.*", f"ADMIN_GROUP_ID={group_id}", content, flags=re.MULTILINE)
            else:
                new_content = content + f"\nADMIN_GROUP_ID={group_id}\n"
            with open(env_file, "w", encoding="utf-8") as f:
                f.write(new_content)
        except Exception:
            pass
