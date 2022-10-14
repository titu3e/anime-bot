from telebot import types
import telebot
from config import (
    TOKEN, 
    RECENT_RELEASE_ANIME_URL, 
    POPULAR_ANIME_URL, 
    DETAILS_ANIME_URL, 
    SEARCH_ANIME_URL, 
    GENRE_ANIME_URL, 
    MOVIES_ANIME_URL, 
    TOP_AIRING_URL,
    GENRES_LIST, 
    EPISODE_LIST_PORTION, 
)
import requests
import psycopg2

# connect heroku database
conn = psycopg2.connect(
    dbname='d8inggurc6rs9', 
    user='hhajxnbkcgcdbn', 
    password='22583bff314b7029b044d043fe0ae31c4e0411c11ec3b8e4c6fe0d6589f9b8a0', 
    host='ec2-44-195-100-240.compute-1.amazonaws.com',
    port='5432'
)
cursor = conn.cursor()

# global variables
user_list = {}

bot = telebot.TeleBot(TOKEN)

# start
@bot.message_handler(commands=['start', 'help'])
def start(message):
    global user_list

    user_id = str(message.from_user.id)
    username = message.from_user.first_name
    
    user_list[user_id] = {}

    welcome_message = f'<b>Welcome, {username}!</b>\n\nThis project is implemented using by the Gogoanime API.'
    
    help_message = '\n\n Helper:' \
            '\n\n/recent - get recent release episodes' \
            '\n\n/popular - get popular anime' \
            '\n\n/search - get anime search' \
            '\n\n/movies - get anime movies' \
            '\n\n/top_airing - get top airing' \
            '\n\n/genre - get anime genres' \
            '\n\n/favorite - get favorite anime' \
            '\n\n/help - get this helper'
    
    msg = help_message
    
    if message.text == '/start':
        msg = welcome_message + help_message + '\n\nEnjoy watching you!'

    bot.send_message(message.chat.id, msg, parse_mode='html')   

# get recent release anime list
@bot.message_handler(commands=['recent'])
def get_recent(message):
    show_anime_list(message=message, url=RECENT_RELEASE_ANIME_URL, title='Recent release anime list:')

# get popular anime list
@bot.message_handler(commands=['popular'])
def get_popular(message):
    show_anime_list(message=message, url=POPULAR_ANIME_URL, title='Popular anime list:')

# search anime
@bot.message_handler(commands=['search'])
def search(message):
    bot.send_message(message.chat.id, 'Enter search text:')
    bot.register_next_step_handler(message, search_handler)

# search next step handler
def search_handler(message):
    show_anime_list(message=message, url=f'{SEARCH_ANIME_URL}?keyw={message.text.lower()}', title='Found anime list:')

# get anime movies
@bot.message_handler(commands=['movies'])
def get_movies(message):
    show_anime_list(message=message, url=MOVIES_ANIME_URL, title='Movies anime list:')

# get top airing anime
@bot.message_handler(commands=['top_airing'])
def get_top_airing(message):
    show_anime_list(message=message, url=TOP_AIRING_URL, title='Top airing anime list:')
    
# get genre anime
@bot.message_handler(commands=['genre'])
def get_genre(message):
    bot.send_message(message.chat.id, f'Enter genre from the list:{GENRES_LIST}')
    bot.register_next_step_handler(message, genre_handler)

# genre anime next step handler
def genre_handler(message):
    if message.text.lower() not in GENRES_LIST:
        bot.send_message(message.chat.id, f'This genre is not available.\nList of available genres: {GENRES_LIST}')
        return
    
    show_anime_list(message=message, url=f'{GENRE_ANIME_URL}/{message.text.lower()}', title='Genre anime list:')

# get favorite anime list
@bot.message_handler(commands=['favorite'])
def show_favorite(message):
    global user_list

    user_id = str(message.from_user.id)
       
    cursor.execute(f"SELECT * FROM user_favorites WHERE user_id={user_id}")

    rows = cursor.fetchall()

    anime_list = []
    
    for row in rows:
        anime_json = {
            "animeId": row[2],
            "animeTitle": row[3],
            "animeImg": row[4],
        }
        anime_list.append(anime_json)

    markup = types.InlineKeyboardMarkup()
    
    n = 0
    for anime in anime_list:
         markup.add(
             types.InlineKeyboardButton(anime["animeTitle"], callback_data=f'favorite_{n}')
         )
         n += 1
    
    bot.send_message(message.chat.id, 'Favorite anime list:', reply_markup=markup)

    user_list[user_id]["anime_list"] = anime_list
    user_list[user_id]["anime_number"] = 0

# show anime list
def show_anime_list(message, url, title):
    global user_list
    
    user_id = str(message.from_user.id)

    response = requests.get(url)
    anime_list = response.json()

    markup = types.InlineKeyboardMarkup(row_width=1)
    n = 0
    for anime in anime_list:
         markup.add(
             types.InlineKeyboardButton(anime["animeTitle"], callback_data=f'details_{n}')
         )
         n += 1
    
    bot.send_message(message.chat.id, title, reply_markup=markup)

    user_list[user_id]["anime_list"] = anime_list
    user_list[user_id]["anime_number"] = 0

# show anime detail
def show_anime_detail(message, is_favorite=False):
    global user_list
    
    user_id = str(message.chat.id)
    
    anime_list = user_list[user_id]["anime_list"]
    anime_number = user_list[user_id]["anime_number"]
    
    if len(anime_list) == 0:
        bot.send_message(message.chat.id, 'List is empty')
        return

    try:
        r = requests.get(f'{DETAILS_ANIME_URL}/{anime_list[anime_number]["animeId"]}')
        anime = r.json()

        caption = f'<b>{anime["animeTitle"]}</b>' \
            f'\n<u>Synopsis:</u> {anime["synopsis"][:200]}' \
            f'\n<u>Type:</u> {anime["type"]}' \
            f'\n<u>Released:</u> {anime["releasedDate"]}' \
            f'\n<u>Status:</u> {anime["status"]}' \
            f'\n<u>Genres:</u> {anime["genres"]}' \
            f'\n<u>Total episodes:</u> {anime["totalEpisodes"]}'
        
        user_list[user_id]["episode_list"] = anime["episodesList"]
                
        markup = types.InlineKeyboardMarkup()
        
        if is_favorite:
            markup.row(
                types.InlineKeyboardButton('📚 Episodes', callback_data=f'show_episodes'),
                types.InlineKeyboardButton('📗 Select episode', callback_data=f'select_episode'),
                types.InlineKeyboardButton('❌ Remove from favorite', callback_data=f'remove_favorite')
            )
        else:
            markup.row(
                types.InlineKeyboardButton('📚 Episodes', callback_data=f'show_episodes'),
                types.InlineKeyboardButton('📗 Select episode', callback_data=f'select_episode'),
                types.InlineKeyboardButton('⭐ Add favorite', callback_data=f'add_favorite')
            )

        bot.send_photo(message.chat.id, 
            photo=anime_list[anime_number]["animeImg"], 
            caption=caption, parse_mode='html', 
            reply_markup=markup)    

    except Exception as e:
        print(e)
        bot.send_message(message.chat.id, 'Sorry, i can\'t show anime details.')
        return

# callback query
@bot.callback_query_handler(func=lambda call:True)
def buttons_handler(call):
    global user_list
    
    user_id = str(call.message.chat.id)

    anime_list = user_list[user_id]["anime_list"]
    
    if call.data == 'show_episodes':
        try:
            user_list[user_id]["episode_number"] = 0
            show_episodes(call.message)
        except Exception as e:
            print(e)
            bot.send_message(call.message.chat.id, 'Sorry, i can\'t show anime episodes.')
            return
        return    
    elif call.data == 'next_episodes':
        try:
            show_episodes(call.message)
        except Exception as e:
            print(e)
            bot.send_message(call.message.chat.id, 'Sorry, i can\'t show anime episodes.')
            return
        return    
    elif call.data == 'select_episode':
        bot.send_message(call.message.chat.id, 'Enter episode number:')
        bot.register_next_step_handler(call.message, select_episode)
        return
    elif call.data == 'add_favorite':
        add_favorite(call.message)
        return
    elif call.data == 'remove_favorite':
        remove_favorite(call.message)    
        return

    for n in range(len(anime_list)):
        if call.data == f'details_{n}':
            user_list[user_id]["anime_number"] = n
            show_anime_detail(call.message)
            return
    
    for n in range(len(anime_list)):
        if call.data == f'favorite_{n}':
            user_list[user_id]["anime_number"] = n
            show_anime_detail(call.message, is_favorite=True)    
            return        
    
# show anime episodes
def show_episodes(message):
    global user_list
    
    user_id = str(message.chat.id)

    episode_list = user_list[user_id]["episode_list"]
    episode_number = user_list[user_id]["episode_number"]

    markup = types.InlineKeyboardMarkup(row_width=4)
    buttons = []
    while episode_number < len(episode_list):
        buttons.append(
            types.InlineKeyboardButton(f'📺 {episode_list[episode_number]["episodeNum"]}', 
                url=episode_list[episode_number]["episodeUrl"])
        )

        if len(buttons) == 4:
            markup.row(*buttons)
            buttons = []

        if (episode_number + 1) % EPISODE_LIST_PORTION == 0:
            episode_number += 1
            break
    
        episode_number += 1
    
    if len(buttons) > 0:
        markup.row(*buttons)
    
    if episode_number < len(episode_list):
        markup.row(
            types.InlineKeyboardButton('Next episodes', callback_data=f'next_episodes'),    
        )

    bot.send_message(message.chat.id, 'Last episodes: ', reply_markup=markup)      

    user_list[user_id]["episode_list"] = episode_list
    user_list[user_id]["episode_number"] = episode_number  

# select episode
def select_episode(message):
    global user_list
    
    user_id = str(message.chat.id)

    episode_list = user_list[user_id]["episode_list"]
    
    n = -1
    try:
        n = int(message.text)
    except:
        bot.send_message(message.chat.id, 'The value must be an integer!')
        return    
    
    if n < 1 or n > len(episode_list):
        bot.send_message(message.chat.id, f'The value must be between 1 and {len(episode_list)}!')
        return 
    
    for episode in episode_list:
        if episode["episodeNum"] == str(n):
            markup = types.InlineKeyboardMarkup()
            markup.row(
                types.InlineKeyboardButton(f'📺 {episode["episodeNum"]}', 
                    url=episode["episodeUrl"])    

            )
            bot.send_message(message.chat.id, 'Selected episode: ', reply_markup=markup)  
            break
    
# add anime to favorite list
def add_favorite(message):
    global user_list
    
    user_id = str(message.chat.id)
    
    anime_list = user_list[user_id]["anime_list"]
    anime_number = user_list[user_id]["anime_number"]
       
    try:
        cursor.execute(f"SELECT * FROM user_favorites WHERE user_id={user_id} \
            AND animeId='{anime_list[anime_number]['animeId']}'")
        
        rows = cursor.fetchall()
        
        if len(rows) == 0:
            cursor.execute(f"INSERT INTO user_favorites(user_id, animeId, animeTitle, animeImg) \
                VALUES({user_id}, '{anime_list[anime_number]['animeId']}', \
                '{anime_list[anime_number]['animeTitle']}', \
                '{anime_list[anime_number]['animeImg']}')")
               
            conn.commit()
            bot.send_message(message.chat.id, 'The anime added to favorites.')
        else:
            bot.send_message(message.chat.id, 'The anime already added to favorites.')    
       
    except Exception as e:
        print(e)
        bot.send_message(message.chat.id, 'Sorry, I can\'t write user favorite list')      

    user_list[user_id]["anime_list"] = anime_list
    user_list[user_id]["anime_number"] = anime_number    
            
# remove anime from favorites list
def remove_favorite(message):
    global user_list
    
    user_id = str(message.chat.id)
        
    anime_list = user_list[user_id]["anime_list"]
    anime_number = user_list[user_id]["anime_number"]

    try:
        cursor.execute(f"DELETE FROM user_favorites WHERE user_id={user_id} \
            AND animeId='{anime_list[anime_number]['animeId']}'")
        
        conn.commit()
        
        bot.send_message(message.chat.id, 'The anime removed from favorites')
    except Exception as e:
        print(e)
        bot.send_message(message.chat.id, 'Sorry, I can\'t delete from user favorite list')  

    user_list[user_id]["anime_list"] = anime_list
    user_list[user_id]["anime_number"] = anime_number    

bot.set_my_commands([
    types.BotCommand("/start", "main menu"),
    types.BotCommand("/help", "print helper"),
    types.BotCommand("/recent", "get recent release episodes"),
    types.BotCommand("/popular", "get popular anime"),
    types.BotCommand("/search", "get anime search"),
    types.BotCommand("/movies", "get anime movies"),
    types.BotCommand("/top_airing", "get top airing"),
    types.BotCommand("/genre", "get anime genres"),
    types.BotCommand("/favorite", "get favorite anime"),

])

bot.infinity_polling()