from aiogram.fsm.state import State, StatesGroup

class VisaStates(StatesGroup):
    country = State()
    custom_country = State()
    purpose = State()
    timeframe = State()
    refusal = State()
    refusal_count = State()
    name = State()
    phone = State()
    convenient_time = State()

class StudyStates(StatesGroup):
    stage = State()
    country = State()
    custom_country = State()
    ielts = State()
    ielts_score = State()
    budget = State()
    name = State()
    phone = State()
    convenient_time = State()

class TourStates(StatesGroup):
    destination = State()
    tour_select = State()
    departure_date = State()
    name = State()
    phone = State()

class ConsultationStates(StatesGroup):
    service = State()
    name = State()
    phone = State()
    convenient_time = State()

class StatusCheckStates(StatesGroup):
    lead_number = State()

class AdminStates(StatesGroup):
    # Tour add
    tour_destination = State()
    tour_title = State()
    tour_price = State()
    tour_description = State()
    tour_included = State()
    
    # FAQ add
    faq_country = State()
    faq_topic = State()
    faq_content = State()

    # Result add
    result_name = State()
    result_country = State()
    result_service = State()
    result_content = State()
    result_photo = State()

    # Broadcast
    broadcast_text = State()

    # Reminder
    reminder_lead_id = State()
    reminder_time = State()
    reminder_note = State()
