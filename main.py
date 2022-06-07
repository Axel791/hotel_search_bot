from aiogram.utils import executor
from loader import dp
from handlers import low_price
from handlers import welcome
from loguru import logger
from handlers import history
from handlers import best_deal
from handlers import high_price

logger.add('logger.log', format='{time} {level} {message}',
           level='ERROR')

welcome.register_welcome_handler(dp)
low_price.register_handlers_low_price(dp)
history.register_history_handler(dp)
best_deal.register_best_deal_handlers(dp)
high_price.register_high_price(dp)

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)