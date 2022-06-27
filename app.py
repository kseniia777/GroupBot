import asyncio

from aiogram import executor, types
from aiogram.dispatcher.filters.builtin import CommandStart
from aiogram.dispatcher.filters import Text
import sqlite3
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from loader import dp, bot, admin_id, group_id, present, bot_name, time_stamp
from Dbase import create_tables, Competition, AddUser, GetInfo, SwitchCompetition, GroupMessage


db = sqlite3.connect('groupbase.sqlite', check_same_thread=False)


# work in chat
@dp.message_handler(content_types=types.ContentType.NEW_CHAT_MEMBERS)
async def new_member(message: types.Message):

    # add user into table
    add_user = AddUser(db)
    get_info = GetInfo(db)
    from_user_id = message.from_user.id
    add_user.add_new_user(from_user_id, message.from_user.first_name, message.from_user.first_name, message.from_user.last_name)
    # add added_user into table
    added_id = message.new_chat_members[0].id
    added_username = message.new_chat_members[0].username
    added_first_name = message.new_chat_members[0].first_name
    added_last_name = message.new_chat_members[0].last_name

    if added_id in get_info.users_id_list():
        await bot.send_message(from_user_id, "Этот пользователь уже был добавлен в чат ранее. Поробуйте пригласить кого-то еще.")
    else:
        await bot.send_message(from_user_id, f"Новый пользователь успешно добавлен. Вам присвоен новый номерок - №{get_info.new_ticket(from_user_id)}")

    add_user.add_new_user(added_id, added_username, added_first_name, added_last_name)

    # add event
    add_user.insert_join_message(from_user_id, added_id, message.date)

    await bot.delete_message(message.chat.id, message.message_id)


# delete service messege
@dp.message_handler(content_types=types.ContentType.LEFT_CHAT_MEMBER)
async def new_member(message: types.Message):
    await bot.delete_message(message.chat.id, message.message_id)


# work in bot
@dp.message_handler(CommandStart( ))
async def bot_start(message: types.Message):
    from_id = message.from_user.id
    from_username = message.from_user.username
    from_first_name = message.from_user.first_name
    from_last_name = message.from_user.last_name
    AddUser(db).add_new_user(from_id, from_username, from_first_name, from_last_name)
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item1 = types.KeyboardButton("Кого я добавил❓")
    markup.add(item1)  # add btn to keyboard
    await message.answer(
        f"Привет, {message.from_user.full_name}!\nДля того, чтобы получить информацию по добавленным участникам, нажмите на кнопку⬇️ ",
        reply_markup=markup)


@dp.message_handler(Text(equals=['Кого я добавил❓']))
async def count_users(message):
    if message.chat.type == 'private':
        status = SwitchCompetition(db).status( )
        if message.text == 'Кого я добавил❓':
            if status:
                count = GetInfo(db).users_count(message.chat.id)
                inline_m = types.InlineKeyboardMarkup(row_width=1)
                list_button = types.InlineKeyboardButton("Отобразить список", callback_data='list')
                inline_m.add(list_button)
                tick_list = GetInfo(db)
                tickets_list = tick_list.user_tikets(message.chat.id)
                await message.answer(
                    f"{message.from_user.full_name}, Вы добавили {count} человек(а).\nВаши номера: {tickets_list}",
                    reply_markup=inline_m)
            else:
                await message.answer("На данный момент конкурса нет")


@dp.callback_query_handler(lambda callback_query: True)
async def users_list(call):
    if call.message:
        if call.data == 'list':
            users_list = GetInfo(db).users_list(call.message.chat.id)
            await call.answer(cache_time = 10)
            await call.message.answer(f"Номерок, Username, Имя, Дата:\n{users_list}")


###Admin

# New competition number
@dp.message_handler(commands=['new_competition'])
async def new_comp(message: types.Message):
    if message.chat.id in admin_id:
        last_number = Competition(db).get_competition()  # max value
        new_number = last_number + 1
        add_num = Competition(db)
        Competition(db).set_competition(new_number)
        await message.answer(f"Новый конкурс №{new_number} успешно создан!")
    else:
        await message.answer("No info")


@dp.message_handler(Text(startswith='/winner_'))
async def winner_user(message):
    if message.chat.id in admin_id:
        winner_tick = message.text
        win_ticket = winner_tick.replace("/winner_", "")
        info = GetInfo(db)
        winner_info = info.winner(win_ticket)
        # added user info
        added_inf = info.winner_add(win_ticket)
        # winner_user_id
        from_id = info.winner_user_id(win_ticket)
        await message.answer(f"Билет №{win_ticket} у пользователя {winner_info}.\n(Добавление: {added_inf}.")
        await bot.send_message(from_id, f"Позравляю, Ваш билет №{win_ticket} победил в конкурсе!")
        await bot.send_message(group_id, f"Ура! Конкурс завершен и по результатам выйграшный номер - №{win_ticket}, а победитель - @{winner_info}. Поздравляем! Вы выйграли {present}")
    else:
        await message.answer("No info")


@dp.message_handler(commands=['competition_OFF'])
async def comp_off(message):
    if message.chat.id in admin_id:
        last_number = Competition(db).get_competition()
        count = GetInfo(db).all_count( )
        await message.answer(f"Конкурс №{last_number} отключен успешно. Всего участников - {count}")
        SwitchCompetition(db).comp_off( )
    else:
        await message.answer("No info")


@dp.message_handler(commands=['competition_ON'])
async def comp_on(message):
    if message.chat.id in admin_id:
        SwitchCompetition(db).comp_on( )
        last_number = Competition(db).get_competition( )
        await message.answer(f"Конкурс №{last_number} подключен успешно.\nДля начала вы можете добавить новый конкурс - /new_competition")
    else:
        await message.answer("No info")


@dp.message_handler(commands=['admin_help'])
async def new_comp(message: types.Message):
    if message.chat.id in admin_id:
        await message.answer(
            "Новый конкурс - /new_competition\nПобедитель - /winner_%номерок%\nВыкл - /competition_OFF\nВкл - /competition_ON")
    else:
        await message.answer("No info")


# Send notification to the group
sched = AsyncIOScheduler( )


@sched.scheduled_job("interval", minutes=time_stamp)
async def comp_not():
    status = SwitchCompetition(db).status()
    if status:
        last_number = Comp_table(db).get_competition()
        count = GetInfo(db).all_count()
        # delete last message
        mes = GroupMessage(db).get_id()
        if mes:
           await bot.delete_message(group_id, mes)

        res = await bot.send_message(group_id, f"Участвуй в конкурсе №{last_number}! Добавляй друзей в чат и выигрывай {present}. Чем больше добавишь - тем больше шанс выйграть. Смотри свои номера в {bot_name}. Сейчас участников - {count}, так что не упусти свой шанс!")

        # save message id
        mes_id = res.message_id
        GroupMessage(db).save_id(mes_id)


sched.start( )


@dp.message_handler(Text(startswith=present))
async def dele(message):
    await bot.send_message(group_id, "del")


if __name__ == '__main__':
    create_tables(db)
    executor.start_polling(dp, skip_updates=False)
