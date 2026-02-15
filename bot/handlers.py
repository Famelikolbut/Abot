import os
from aiogram import Router, F, Bot
from aiogram.types import Message
from aiogram.filters import CommandStart
from services.llm_service import GroqSQLGenerator
from services.query_executor import QueryExecutor
from services.data_loader import DataLoader

router = Router()
llm_service = GroqSQLGenerator()
query_executor = QueryExecutor()
data_loader = DataLoader()

@router.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    await message.answer(
        "Привет! Я бот аналитики видео.\n"
        "1. Отправь мне JSON файл с данными (например, videos.json), чтобы загрузить их в базу (старые данные будут удалены).\n"
        "2. Задай мне любой вопрос о своих видео на естественном языке."
    )

@router.message(F.document)
async def handle_document(message: Message, bot: Bot):
    document = message.document

    if document.mime_type != 'application/json' and not document.file_name.endswith('.json'):
        await message.answer("Пожалуйста, отправьте файл в формате JSON.")
        return

    await message.answer("Скачиваю и обрабатываю файл... Это может занять некоторое время.")
    
    try:
        file_id = document.file_id
        file = await bot.get_file(file_id)
        file_path = file.file_path

        temp_filename = f"temp_{document.file_name}"
        await bot.download_file(file_path, temp_filename)

        await data_loader.clear_data()
        await data_loader.load_from_file(temp_filename)

        if os.path.exists(temp_filename):
            os.remove(temp_filename)
            
        await message.answer(f"Данные из файла {document.file_name} успешно загружены! Старые данные удалены.")
        
    except Exception as e:
        await message.answer(f"Ошибка при обработке файла: {str(e)}")

@router.message(F.text)
async def analytics_handler(message: Message) -> None:
    try:
        user_query = message.text
        
        sql_query = await llm_service.generate_sql(user_query)
        print(f"Generated SQL: {sql_query}")
        
        result = await query_executor.execute_query(sql_query)
        
        if result is None:
            await message.answer("Ничего не найдено или ответ 0.")
        else:
            await message.answer(str(result))
            
    except Exception as e:
        await message.answer(f"Произошла ошибка: {str(e)}")
