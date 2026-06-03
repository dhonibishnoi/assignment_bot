from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, CallbackQuery, BufferedInputFile
from keyboards.inline import main_menu, back_button
from database.users import UserManager
from services.ai_router import AIRouter
from utils.limiter import Limiter
from utils.language import detect_language
from config import DEFAULT_WORD_LIMIT

router = Router()
ai_router = AIRouter()

class AssignmentState(StatesGroup):
    waiting_topic = State()

def split_long_message(text: str, max_len: int = 4000) -> list:
    if len(text) <= max_len:
        return [text]
    chunks = []
    while len(text) > max_len:
        split_at = text.rfind(' ', 0, max_len)
        if split_at == -1:
            split_at = max_len
        chunks.append(text[:split_at])
        text = text[split_at:].lstrip()
    if text:
        chunks.append(text)
    return chunks

@router.callback_query(F.data == "generate_assignment")
async def ask_topic(callback: CallbackQuery, state: FSMContext):
    try:
        await callback.answer()
    except Exception:
        pass
    user = await UserManager.get_user(callback.from_user.id)
    if not user:
        await callback.message.answer("Please restart with /start")
        return
    is_premium = user.get('is_premium', False)
    can_generate, msg = await Limiter.can_generate(callback.from_user.id, is_premium)
    if not can_generate:
        await callback.message.answer(msg + "\n\nUse /start to see options.")
        return
    await state.set_state(AssignmentState.waiting_topic)
    await callback.message.answer(
        "📝 Send me your assignment topic.\n\nExample: 'Effects of climate change on agriculture'",
        reply_markup=back_button()
    )

@router.message(AssignmentState.waiting_topic)
async def generate_assignment(message: Message, state: FSMContext):
    topic = message.text
    user = await UserManager.get_user(message.from_user.id)
    if not user:
        await message.answer("Please restart with /start")
        await state.clear()
        return
    is_premium = user.get('is_premium', False)
    language = detect_language(topic)
    
    if is_premium:
        word_limit = user.get('word_limit', DEFAULT_WORD_LIMIT)
    else:
        word_limit = DEFAULT_WORD_LIMIT // 2
    
    await message.answer("⏳ Generating assignment... Please wait.")
    try:
        assignment = await ai_router.generate_assignment(topic, language, word_limit)
        await Limiter.record_generation(message.from_user.id, is_premium)
        
        chunks = split_long_message(assignment)
        for i, chunk in enumerate(chunks):
            if len(chunk) > 4096:
                chunk = chunk[:4090] + "..."
            await message.answer(f"📄 *Assignment on: {topic}* (Part {i+1}/{len(chunks)})\n\n{chunk}", parse_mode="Markdown")
        
        if is_premium:
            try:
                from services.pdf_service import PDFService
                from services.docx_service import DOCXService
                pdf_bytes = await PDFService.generate_pdf(assignment, topic)
                docx_bytes = await DOCXService.generate_docx(assignment, topic)
                await message.answer_document(BufferedInputFile(pdf_bytes, filename="assignment.pdf"), caption="📑 PDF version")
                await message.answer_document(BufferedInputFile(docx_bytes, filename="assignment.docx"), caption="📝 DOCX version")
            except Exception as e:
                await message.answer(f"⚠️ File generation failed: {str(e)}")
    except Exception as e:
        await message.answer(f"❌ Error: {str(e)}\n\nPlease try again later.")
        import traceback
        traceback.print_exc()
    await state.clear()