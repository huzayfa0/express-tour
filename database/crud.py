from datetime import datetime, date, timedelta
from typing import Optional, List, Dict, Any
from sqlalchemy import select, update, func, desc, and_
from sqlalchemy.orm import selectinload
from .base import AsyncSessionLocal
from .models import User, Lead, StatusHistory, Manager, Reminder, Tour, FAQ, Result

async def get_or_create_user(
    user_id: int,
    full_name: str,
    username: Optional[str] = None,
    source: str = "direct"
) -> User:
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        if not user:
            user = User(
                id=user_id,
                full_name=full_name,
                username=username,
                source=source,
                first_seen=datetime.now(),
                last_active=datetime.now(),
                total_leads=0
            )
            session.add(user)
        else:
            user.full_name = full_name
            user.username = username
            user.last_active = datetime.now()
        await session.commit()
        await session.refresh(user)
        return user


async def generate_next_lead_number(session) -> str:
    result = await session.execute(select(func.max(Lead.id)))
    max_id = result.scalar() or 0
    next_num = 1001 + max_id
    return f"ET-{next_num}"


async def create_lead(
    user_id: int,
    service: str,
    country: Optional[str] = None,
    purpose: Optional[str] = None,
    timeframe: Optional[str] = None,
    refusal_count: int = 0,
    stage: Optional[str] = None,
    ielts_score: Optional[str] = None,
    budget: Optional[str] = None,
    name: Optional[str] = None,
    phone: Optional[str] = None,
    convenient_time: Optional[str] = None,
    source: str = "direct",
    notes: Optional[str] = None
) -> Lead:
    async with AsyncSessionLocal() as session:
        lead_num = await generate_next_lead_number(session)
        lead = Lead(
            lead_number=lead_num,
            user_id=user_id,
            service=service,
            country=country,
            purpose=purpose,
            timeframe=timeframe,
            refusal_count=refusal_count,
            stage=stage,
            ielts_score=ielts_score,
            budget=budget,
            name=name,
            phone=phone,
            convenient_time=convenient_time,
            source=source,
            status="YANGI",
            notes=notes,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        session.add(lead)
        await session.flush()

        # Update user total_leads & phone if provided
        user_res = await session.execute(select(User).where(User.id == user_id))
        user = user_res.scalar_one_or_none()
        if user:
            user.total_leads += 1
            if phone:
                user.phone = phone

        # Add initial status history
        history = StatusHistory(
            lead_id=lead.id,
            old_status="START",
            new_status="YANGI",
            note="Lid bot orqali yaratildi",
            created_at=datetime.now()
        )
        session.add(history)

        await session.commit()
        await session.refresh(lead)
        return lead


async def get_lead_by_number(lead_number: str) -> Optional[Lead]:
    clean_number = lead_number.strip().upper()
    if not clean_number.startswith("ET-") and clean_number.isdigit():
        clean_number = f"ET-{clean_number}"
    elif clean_number.startswith("#"):
        clean_number = clean_number[1:]

    async with AsyncSessionLocal() as session:
        stmt = (
            select(Lead)
            .where(Lead.lead_number == clean_number)
            .options(
                selectinload(Lead.history),
                selectinload(Lead.manager),
                selectinload(Lead.user)
            )
        )
        result = await session.execute(stmt)
        return result.scalar_one_or_none()


async def get_lead_by_id(lead_id: int) -> Optional[Lead]:
    async with AsyncSessionLocal() as session:
        stmt = (
            select(Lead)
            .where(Lead.id == lead_id)
            .options(
                selectinload(Lead.history),
                selectinload(Lead.manager),
                selectinload(Lead.user)
            )
        )
        result = await session.execute(stmt)
        return result.scalar_one_or_none()


async def update_lead_status(
    lead_id: int,
    new_status: str,
    changed_by: Optional[int] = None,
    note: Optional[str] = None
) -> Optional[Lead]:
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(Lead).where(Lead.id == lead_id))
        lead = result.scalar_one_or_none()
        if not lead:
            return None

        old_status = lead.status
        lead.status = new_status
        lead.updated_at = datetime.now()

        history = StatusHistory(
            lead_id=lead.id,
            old_status=old_status,
            new_status=new_status,
            changed_by=changed_by,
            note=note,
            created_at=datetime.now()
        )
        session.add(history)
        await session.commit()
        await session.refresh(lead)
        return lead


async def assign_lead_manager(lead_id: int, manager_id: int) -> Optional[Lead]:
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(Lead).where(Lead.id == lead_id))
        lead = result.scalar_one_or_none()
        if not lead:
            return None
        lead.assigned_to = manager_id
        lead.updated_at = datetime.now()
        await session.commit()
        await session.refresh(lead)
        return lead


async def create_reminder(
    lead_id: int,
    manager_id: Optional[int],
    remind_at: datetime,
    note: Optional[str] = None
) -> Reminder:
    async with AsyncSessionLocal() as session:
        reminder = Reminder(
            lead_id=lead_id,
            manager_id=manager_id,
            remind_at=remind_at,
            note=note,
            is_sent=False,
            created_at=datetime.now()
        )
        session.add(reminder)
        await session.commit()
        await session.refresh(reminder)
        return reminder


async def get_pending_reminders() -> List[Reminder]:
    now = datetime.now()
    async with AsyncSessionLocal() as session:
        stmt = (
            select(Reminder)
            .where(and_(Reminder.remind_at <= now, Reminder.is_sent == False))
            .options(selectinload(Reminder.lead))
        )
        result = await session.execute(stmt)
        return list(result.scalars().all())


async def mark_reminder_sent(reminder_id: int):
    async with AsyncSessionLocal() as session:
        await session.execute(
            update(Reminder).where(Reminder.id == reminder_id).values(is_sent=True)
        )
        await session.commit()


async def get_today_stats() -> Dict[str, Any]:
    today_start = datetime.combine(date.today(), datetime.min.time())
    today_end = datetime.combine(date.today(), datetime.max.time())

    async with AsyncSessionLocal() as session:
        # All leads today
        stmt = select(Lead).where(between_leads := and_(Lead.created_at >= today_start, Lead.created_at <= today_end))
        result = await session.execute(stmt)
        today_leads = list(result.scalars().all())

        total = len(today_leads)
        visa_count = sum(1 for l in today_leads if l.service == "visa")
        study_count = sum(1 for l in today_leads if l.service == "study")
        tour_count = sum(1 for l in today_leads if l.service == "tour")
        consult_count = sum(1 for l in today_leads if l.service == "consult")

        contacted = sum(1 for l in today_leads if l.status not in ("YANGI", "KEYINROQ"))
        not_contacted = total - contacted
        consultations = sum(1 for l in today_leads if l.status in ("KONSULT", "QUALIF", "SHARTNOMA", "ELCHIXONA", "VIZA_OLDI"))
        contracts = sum(1 for l in today_leads if l.status in ("SHARTNOMA", "ELCHIXONA", "VIZA_OLDI"))

        # Sources
        sources = {}
        for l in today_leads:
            src = l.source or "direct"
            sources[src] = sources.get(src, 0) + 1

        return {
            "total": total,
            "visa": visa_count,
            "study": study_count,
            "tour": tour_count,
            "consult": consult_count,
            "contacted": contacted,
            "not_contacted": not_contacted,
            "contacted_percent": round((contacted / total * 100), 1) if total > 0 else 0,
            "consultations": consultations,
            "contracts": contracts,
            "sources": sources
        }


async def get_recent_leads(limit: int = 10) -> List[Lead]:
    async with AsyncSessionLocal() as session:
        stmt = (
            select(Lead)
            .order_by(desc(Lead.created_at))
            .limit(limit)
            .options(selectinload(Lead.user), selectinload(Lead.manager))
        )
        result = await session.execute(stmt)
        return list(result.scalars().all())


async def get_hot_leads(limit: int = 10) -> List[Lead]:
    async with AsyncSessionLocal() as session:
        stmt = (
            select(Lead)
            .where(Lead.status.in_(["YANGI", "KEYINROQ"]))
            .order_by(desc(Lead.created_at))
            .limit(limit)
            .options(selectinload(Lead.user))
        )
        result = await session.execute(stmt)
        return list(result.scalars().all())


async def get_managers(active_only: bool = True) -> List[Manager]:
    async with AsyncSessionLocal() as session:
        stmt = select(Manager)
        if active_only:
            stmt = stmt.where(Manager.is_active == True)
        result = await session.execute(stmt)
        return list(result.scalars().all())


async def add_or_update_manager(manager_id: int, name: str, role: str = "manager") -> Manager:
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(Manager).where(Manager.id == manager_id))
        mgr = result.scalar_one_or_none()
        if not mgr:
            mgr = Manager(id=manager_id, name=name, role=role, is_active=True, created_at=datetime.now())
            session.add(mgr)
        else:
            mgr.name = name
            mgr.role = role
            mgr.is_active = True
        await session.commit()
        await session.refresh(mgr)
        return mgr


async def get_active_tours(destination: Optional[str] = None) -> List[Tour]:
    async with AsyncSessionLocal() as session:
        stmt = select(Tour).where(Tour.is_active == True)
        if destination:
            stmt = stmt.where(Tour.destination.ilike(f"%{destination}%"))
        result = await session.execute(stmt)
        return list(result.scalars().all())


async def add_tour(
    destination: str,
    title: str,
    price_usd: float,
    description: str,
    whats_included: str,
    slots_total: int = 20,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None
) -> Tour:
    async with AsyncSessionLocal() as session:
        tour = Tour(
            destination=destination,
            title=title,
            price_usd=price_usd,
            description=description,
            whats_included=whats_included,
            slots_total=slots_total,
            slots_left=slots_total,
            start_date=start_date,
            end_date=end_date,
            is_active=True,
            created_at=datetime.now()
        )
        session.add(tour)
        await session.commit()
        await session.refresh(tour)
        return tour


async def get_faqs(country: Optional[str] = None) -> List[FAQ]:
    async with AsyncSessionLocal() as session:
        stmt = select(FAQ)
        if country:
            stmt = stmt.where(FAQ.country.ilike(f"%{country}%"))
        result = await session.execute(stmt)
        return list(result.scalars().all())


async def add_faq(country: str, topic: str, content: str) -> FAQ:
    async with AsyncSessionLocal() as session:
        faq = FAQ(country=country, topic=topic, content=content, created_at=datetime.now())
        session.add(faq)
        await session.commit()
        await session.refresh(faq)
        return faq


async def get_results(limit: int = 5) -> List[Result]:
    async with AsyncSessionLocal() as session:
        stmt = select(Result).order_by(desc(Result.created_at)).limit(limit)
        res = await session.execute(stmt)
        return list(res.scalars().all())


async def add_result(
    full_name: str,
    country: str,
    service: str,
    content: str,
    photo_id: Optional[str] = None
) -> Result:
    async with AsyncSessionLocal() as session:
        r = Result(
            full_name=full_name,
            country=country,
            service=service,
            content=content,
            photo_id=photo_id,
            created_at=datetime.now()
        )
        session.add(r)
        await session.commit()
        await session.refresh(r)
        return r
