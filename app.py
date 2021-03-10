import asyncio

from aiogram import executor, types
from aiogram.dispatcher.filters.builtin import CommandStart
from aiogram.dispatcher.filters import Text
import sqlite3
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from loader import dp, bot, admin_id, group_id, present, bot_name, time_stamp
from Dbase import Comp_table, Adding_user, Get_info, Switch, GroupM

db = sqlite3.connect('groupbase.sqlite', check_same_thread=False)


####работа в группе
@dp.message_handler(content_types=types.ContentType.NEW_CHAT_MEMBERS)
async def new_member(message: types.Message):

    # add user into table
    from_id = message.from_user.id
    from_username = message.from_user.username
    from_first_name = message.from_user.first_name
    from_last_name = message.from_user.last_name
    us_inf = Adding_user(db)
    user_info = us_inf.user_info(from_id, from_username, from_first_name, from_last_name)
    # add added_user into table
    added_id = message.new_chat_members[0].id
    added_username = message.new_chat_members[0].username
    added_first_name = message.new_chat_members[0].first_name
    added_last_name = message.new_chat_members[0].last_name
    ####проверка, был ли пользователь доавлен ранее
    # get ticket
    t = Get_info(db)
    ticket = t.new_ticket(from_id)
    id_list = Get_info(db)
    id_l = id_list.users_id_list( )
    print(added_id)
    if added_id in id_l:
        await bot.send_message(from_id,
                               "Этот пользователь уже был добавлен в чат ранее. Поробуйте пригласить кого-то еще.")
    else:
        await bot.send_message(from_id, f"Новый пользователь успешно добавлен. Вам присвоен новый номерок - №{ticket}")
    #####
    add_us_inf = Adding_user(db)
    add_user_info = add_us_inf.user_info(added_id, added_username, added_first_name, added_last_name)
    # add event
    time = message.date
    time2 = message["date"]
    print(time)
    print(time2)  # стоит ли?

    a = Adding_user(db)
    a.insert_join_message(from_id, added_id, time)

    await bot.delete_message(message.chat.id, message.message_id)



###работа в боте
@dp.message_handler(CommandStart( ))
async def bot_start(message: types.Message):
    from_id = message.from_user.id
    from_username = message.from_user.username
    from_first_name = message.from_user.first_name
    from_last_name = message.from_user.last_name
    us_inf = Adding_user(db)
    us_inf.user_info(from_id, from_username, from_first_name, from_last_name)
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item1 = types.KeyboardButton("Кого я добавил❓")
    markup.add(item1)  # добавляем кнопку на клавиатуре
    await message.answer(
        f"Привет, {message.from_user.full_name}!\nДля того, чтобы получить информацию по добавленным участникам, нажмите на кнопку⬇️ ",
        reply_markup=markup)


@dp.message_handler(Text(equals=['Кого я добавил❓']))
async def count_users(message):
    if message.chat.type == 'private':
        st = Switch(db)
        status = st.status( )
        if message.text == 'Кого я добавил❓':
            if status == True:
                count = Get_info(db)
                c = count.users_count(message.chat.id)
                inline_m = types.InlineKeyboardMarkup(row_width=1)
                list_button = types.InlineKeyboardButton("Отобразить список", callback_data='list')
                inline_m.add(list_button)
                tick_list = Get_info(db)
                tickets_list = tick_list.user_tikets(message.chat.id)
                await message.answer(
                    f"{message.from_user.full_name}, Вы добавили {c} человек(а).\nВаши номера: {tickets_list}",
                    reply_markup=inline_m)

            elif status == False:
                await message.answer("На данный момент конкурса нет")




@dp.callback_query_handler(lambda callback_query: True)
async def users_list(call):
    # try:
    if call.message:
        if call.data == 'list':
            list = Get_info(db)
            l = list.users_list(call.message.chat.id)
            await call.answer(cache_time = 10)
            await call.message.answer(f"Номерок, Username, Имя, Дата:\n{l}")


###админка

# новый №конкурса
@dp.message_handler(commands=['new_competition'])
async def new_comp(message: types.Message):
    if message.chat.id in admin_id:
        number = Comp_table(db)
        last_number = number.get_id_comp( )  # берем последнее(наибольшее) значение
        new_number = last_number + 1  # увеличиваем на 1
        print(type(new_number))
        add_num = Comp_table(db)
        add_num.id_competition(new_number)  # добавляем новое
        await message.answer(f"Новый конкурс №{new_number} успешно создан!")
    else:
        await message.answer("No info")


@dp.message_handler(Text(startswith='/winner_'))
async def winner_user(message):
    if message.chat.id in admin_id:
        winner_tick = message.text
        win_ticket = winner_tick.replace("/winner_", "")
        b = Get_info(db)
        winner_info = b.winner(win_ticket)
        # added user info
        added_inf = b.winner_add(win_ticket)
        # winner_user_id
        from_id = b.winner_user_id(win_ticket)
        # # winner_added_id
        # added_id = b.winner_added_id(win_ticket)
        await message.answer(f"Билет №{win_ticket} у пользователя {winner_info}.\n(Добавление: {added_inf}.")
        await bot.send_message(from_id, f"Позравляю, Ваш билет №{win_ticket} победил в конкурсе!")
        await bot.send_message(group_id,
                               f"Ура! Конкурс завершен и по результатам выйграшный номер - №{win_ticket}, а победитель - @{winner_info}. Поздравляем! Вы выйграли {present}")
        # a = await bot.get_chat_member(group_id, added_id)
        # print(a)
        # if bot.get_chat_member(group_id, from_id)["status"] == ["member"]:
        #     if bot.get_chat_member(group_id, added_id):
        #         await message.answer(f"Оба пользователя - участники группы")
        #     else:
        #         await message.answer(f"не является участником группы")
        # elif bot.get_chat_member(group_id, from_id)["status"] == ["left"]:
        #     await message.answer(f"Победитель покинул группу")
    else:
        await message.answer("No info")


@dp.message_handler(commands=['competition_OFF'])
async def comp_off(message):
    if message.chat.id in admin_id:
        number = Comp_table(db)
        last_number = number.get_id_comp( )
        c = Get_info(db)
        count = c.all_count( )
        await message.answer(f"Конкурс №{last_number} отключен успешно. Всего участников - {count}")
        off = Switch(db)
        off.comp_off( )

    else:
        await message.answer("No info")


@dp.message_handler(commands=['competition_ON'])
async def comp_on(message):
    if message.chat.id in admin_id:
        on = Switch(db)
        on.comp_on( )
        number = Comp_table(db)
        last_number = number.get_id_comp( )
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

###Отправка уыедомления в группу
sched = AsyncIOScheduler( )

@sched.scheduled_job("interval", minutes=time_stamp)
async def comp_not():
    st = Switch(db)
    status = st.status()
    if status == True:
        number = Comp_table(db)
        last_number = number.get_id_comp()
        c = Get_info(db)
        count = c.all_count()
        ### delete last message:
        d = GroupM(db)
        mes = d.get_id()
        if type(mes) == int:
           await bot.delete_message(group_id, mes)

        res = await bot.send_message(group_id,
                              f"Участвуй в конкурсе №{last_number}! Добавляй друзей в чат и выигрывай {present}. Чем больше добавишь - тем больше шанс выйграть. Смотри свои номера в {bot_name}. Сейчас участников - {count}, так что не упусти свой шанс!")

        #res = await bot.send_message(group_id, f"{present}")
        mes_id = res.message_id
        m = GroupM(db)
        m.save_id(mes_id)


# asyncio.sched.add_job(comp_not, 'interval', seconds=5)
sched.start( )


@dp.message_handler(Text(startswith=present))
async def dele(message):
    #if message.text == present:
    await bot.send_message(group_id, "del")
    #await bot.delete_message(group_id, message.message_id)
    #await asyncio.sleep(2)





if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=False)

# async def scheduler():
#     aioschedule.every(0.1).minutes.do(comp_not())
#     # st = Switch(db)
#     # status = st.status()
#     while True:
#         await aioschedule.run_pending()
#         await asyncio.sleep(1)
#
# asyncio.run(comp_not())
#
# asyncio.set_event_loop(asyncio.new_event_loop())
# asyncio.get_event_loop()

##уведомление в группу


# @dp.message_handler(commands=['notification_on'])
# async def comp_not_m(message):
#     if message.chat.id in admin_id:
#         st = Switch(db)
#         status = st.status()
#         while status == True:
#             #while True:
#             number = Comp_table(db)
#             last_number = number.get_id_comp()
#             c = Get_info(db)
#             count = c.all_count()
#             await bot.send_message(group_id, f"Участвуй в конкурсе №{last_number}! Добавляй друзей в чат и выйграй {present}. Чем больше добавишь - тем больше шанс выйграть. Смотри свои номера в {bot_name}. Сейчас участников - {count}, так что не упусти свой шанс!")
#             time.sleep(time_stamp)
#             break
# #
#     else:
#         await message.answer("No info")
# asyncio.run(comp_not())
