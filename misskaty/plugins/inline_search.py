import json
import re
import traceback
from logging import getLogger
from sys import platform
from sys import version as pyver
from unicodedata import name

from bs4 import BeautifulSoup
from deep_translator import GoogleTranslator
from motor import version as mongover
from misskaty.core.keyboard import keyboard
from pykeyboard import InlineKeyboard, InlineButton
from pyrogram import __version__ as pyrover
from pyrogram import enums, filters
from pyrogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    InlineQuery,
    InlineQueryResultArticle,
    InlineQueryResultPhoto,
    InputTextMessageContent,
)

from misskaty import BOT_USERNAME, app, user
from misskaty.helper import post_to_telegraph, http, GENRES_EMOJI, search_jw
from misskaty.plugins.misc_tools import get_content
from utils import demoji

__MODULE__ = "InlineFeature"
__HELP__ = """
To use this feature, just type bot username with following args below.
~ imdb [query] - Search movie details in IMDb.com.
~ pypi [query] - Search package from Pypi.
~ git [query] - Search in Git.
~ google [query] - Search in Google.
~ info [user id/username] - Check info about a user.
"""

keywords_list = ["imdb", "pypi", "git", "google", "secretmsg", "info", "botapi"]

PRVT_MSGS = {}
LOGGER = getLogger()

@app.on_inline_query()
async def inline_menu(_, inline_query: InlineQuery):
    if inline_query.query.strip().lower().strip() == "":
        buttons = InlineKeyboard(row_width=2)
        buttons.add(*[(InlineKeyboardButton(text=i, switch_inline_query_current_chat=i)) for i in keywords_list])

        btn = InlineKeyboard(row_width=2)
        bot_state = "Alive" if await app.get_me() else "Dead"
        ubot_state = "Alive" if await user.get_me() else "Dead"
        btn.add(
            InlineKeyboardButton("Stats", callback_data="stats_callback"),
            InlineKeyboardButton("Go Inline!", switch_inline_query_current_chat=""),
        )

        msg = f"""
**[MissKaty✨](https://github.com/yasirarism):**
**MainBot:** `{bot_state}`
**UserBot:** `{ubot_state}`
**Python:** `{pyver.split()[0]}`
**Pyrogram:** `{pyrover}`
**MongoDB:** `{mongover}`
**Platform:** `{platform}`
**Profiles:** {(await app.get_me()).username} | {(await user.get_me()).first_name}
        """
        answerss = [
            InlineQueryResultArticle(
                title="Inline Commands",
                description="Help Related To Inline Usage.",
                input_message_content=InputTextMessageContent("Click A Button To Get Started."),
                thumb_url="https://hamker.me/cy00x5x.png",
                reply_markup=buttons,
            ),
            InlineQueryResultArticle(
                title="Github Repo",
                description="Github Repo of This Bot.",
                input_message_content=InputTextMessageContent(f"<b>Github Repo @{BOT_USERNAME}</b>\n\nhttps://github.com/yasirarism/MissKatyPyro"),
                thumb_url="https://hamker.me/gjc9fo3.png",
            ),
            InlineQueryResultArticle(
                title="Alive",
                description="Check Bot's Stats",
                thumb_url="https://yt3.ggpht.com/ytc/AMLnZu-zbtIsllERaGYY8Aecww3uWUASPMjLUUEt7ecu=s900-c-k-c0x00ffffff-no-rj",
                input_message_content=InputTextMessageContent(msg, disable_web_page_preview=True),
                reply_markup=btn,
            ),
        ]
        await inline_query.answer(results=answerss)
    elif inline_query.query.strip().lower().split()[0] == "botapi":
        if len(inline_query.query.strip().lower().split()) < 2:
            return await inline_query.answer(
                results=[],
                switch_pm_text="Bot Api Docs | botapi [QUERY]",
                switch_pm_parameter="inline",
            )
        kueri = inline_query.query.split(None, 1)[1].strip()
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) " "Chrome/61.0.3163.100 Safari/537.36"}
        jsonapi = await http.get(f"https://github.com/yasirarism/telegram-bot-api-spec/raw/main/api.json", headers=headers, follow_redirects=True)
        parsemethod = jsonapi.json().get("methods")
        parsetypes = jsonapi.json().get("types")
        datajson = []
        for method in parsemethod:
            if kueri.lower() in method.lower():
                link = parsemethod[method]["href"]
                description = parsemethod[method]["description"][0]
                buttons = InlineKeyboard()
                buttons.row(
                    InlineButton("Open Docs", url=link),
                    InlineButton("Search Again", switch_inline_query_current_chat=inline_query.query),
                )
                buttons.row(
                    InlineButton("Give Coffee", url="https://yasirpedia.eu.org"),
                )
                returns = "".join(f"{i}, " for i in parsemethod[method]["returns"])
                msg = f"<b>{method}</b> (<code>{returns[:-2]}</code>)\n"
                msg += f"{description}\n\n"
                msg += f"<b>Variables:</b>\n"
                if parsemethod[method].get("fields"):
                    for i in parsemethod[method]["fields"]:
                        msg += f"<code>{i['name']}</code> (<b>{i['types'][0]}</b>)\n<b>Required:</b> <code>{i['required']}</code>\n{i['description']}\n\n"
                if len(msg.encode("utf-8")) > 4096:
                    body_text = f"""
                        <pre>{msg}</pre>
                        """
                    msg = await post_to_telegraph(False, method, body_text)
                datajson.append(
                    InlineQueryResultArticle(
                        title=method,
                        input_message_content=InputTextMessageContent(
                            message_text=msg,
                            parse_mode=enums.ParseMode.HTML,
                            disable_web_page_preview=True,
                        ),
                        url=link,
                        description=description,
                        thumb_url="https://img.freepik.com/premium-vector/open-folder-folder-with-documents-document-protection-concept_183665-104.jpg",
                        reply_markup=buttons,
                    )
                )
        for types in parsetypes:
            if kueri.lower() in types.lower():
                link = parsetypes[types]["href"]
                description = parsetypes[types]["description"][0]
                buttons = InlineKeyboard()
                buttons.row(
                    InlineButton("Open Docs", url=link),
                    InlineButton("Search Again", switch_inline_query_current_chat=inline_query.query),
                )
                buttons.row(
                    InlineButton("Give Coffee", url="https://yasirpedia.eu.org"),
                )
                msg = f"<b>{types}</b>\n"
                msg += f"{description}\n\n"
                msg += f"<b>Variables:</b>\n"
                if parsetypes[types].get("fields"):
                    for i in parsetypes[types]["fields"]:
                        msg += f"<code>{i['name']}</code> (<b>{i['types'][0]}</b>)\n<b>Required:</b> <code>{i['required']}</code>\n{i['description']}\n\n"
                if len(msg.encode("utf-8")) > 4096:
                    body_text = f"""
                        <pre>{msg}</pre>
                        """
                    msg = await post_to_telegraph(False, method, body_text)
                datajson.append(
                    InlineQueryResultArticle(
                        title=types,
                        input_message_content=InputTextMessageContent(
                            message_text=msg,
                            parse_mode=enums.ParseMode.HTML,
                            disable_web_page_preview=True,
                        ),
                        url=link,
                        description=description,
                        thumb_url="https://img.freepik.com/premium-vector/open-folder-folder-with-documents-document-protection-concept_183665-104.jpg",
                        reply_markup=buttons,
                    )
                )
        await inline_query.answer(
            results=datajson[:50],
            is_gallery=False,
            is_personal=False,
            next_offset="",
            cache_time=5,
            switch_pm_text=f"Found {len(datajson)} results",
            switch_pm_parameter="help",
        )
    elif inline_query.query.strip().lower().split()[0] == "google":
        if len(inline_query.query.strip().lower().split()) < 2:
            return await inline_query.answer(
                results=[],
                switch_pm_text="Google Search | google [QUERY]",
                switch_pm_parameter="inline",
            )
        judul = inline_query.query.split(None, 1)[1].strip()
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) " "Chrome/61.0.3163.100 Safari/537.36"}
        search_results = await http.get(f"https://www.google.com/search?q={judul}&num=20", headers=headers)
        soup = BeautifulSoup(search_results.text, "lxml")
        data = []
        for result in soup.select(".tF2Cxc"):
            title = result.select_one(".DKV0Md").text
            link = result.select_one(".yuRUbf a")["href"]
            try:
                snippet = result.select_one("#rso .lyLwlc").text
            except:
                snippet = "-"
            message_text = f"<a href='{link}'>{title}</a>\n"
            message_text += f"Deskription: {snippet}"
            data.append(
                InlineQueryResultArticle(
                    title=f"{title}",
                    input_message_content=InputTextMessageContent(
                        message_text=message_text,
                        parse_mode=enums.ParseMode.HTML,
                        disable_web_page_preview=False,
                    ),
                    url=link,
                    description=snippet,
                    thumb_url="https://te.legra.ph/file/ed8ea62ae636793000bb4.jpg",
                    reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(text="Open Website", url=link)]]),
                )
            )
        await inline_query.answer(
            results=data,
            is_gallery=False,
            is_personal=False,
            next_offset="",
            switch_pm_text=f"Found {len(data)} results",
            switch_pm_parameter="google",
        )
    elif inline_query.query.strip().lower().split()[0] == "info":
        if len(inline_query.query.strip().lower().split()) < 2:
            return await inline_query.answer(
                results=[],
                switch_pm_text="User Info | info [id/username]",
                switch_pm_parameter="inline",
            )
        userr = inline_query.query.split(None, 1)[1].strip()
        if "t.me" in userr:
            r = re.search(r"t.me/(\w+)", userr)
            userr = r[1]
        try:
            diaa = await app.get_users(userr)
        except Exception:  # pylint: disable=broad-except
            inline_query.stop_propagation()
            return
        namanya = f"{diaa.first_name} {diaa.last_name}" if diaa.last_name else diaa.first_name
        msg = f"<b>🏷 Name:</b> {namanya}\n<b>🆔 ID:</b> <code>{diaa.id}</code>\n"
        if diaa.username:
            msg += f"<b>🌐 Username:</b> <code>@{diaa.username}</code>\n"
        if diaa.status:
            msg += f"<b>🕰 User Status:</b> {diaa.status}\n"
        if diaa.dc_id:
            msg += f"<b>🌏 DC:</b> {diaa.dc_id}\n"
        msg += f"<b>✨ Premium:</b> {diaa.is_premium}\n"
        msg += f"<b>⭐️ Verified:</b> {diaa.is_verified}\n"
        msg += f"<b>🤖 Bot:</b> {diaa.is_bot}\n"
        if diaa.language_code:
            msg += f"<b>🇮🇩 Language:</b> {diaa.language_code}"
        results = [
            InlineQueryResultArticle(
                title=f"Get information off {diaa.id}",
                input_message_content=InputTextMessageContent(msg),
                description=f"Get information off {diaa.id}",
            )
        ]
        await inline_query.answer(results=results, cache_time=3)
    elif inline_query.query.strip().lower().split()[0] == "secretmsg":
        if len(inline_query.query.strip().lower().split()) < 3:
            return await inline_query.answer(
                results=[],
                switch_pm_text="SecretMsg | secretmsg [USERNAME/ID] [MESSAGE]",
                switch_pm_parameter="inline",
            )
        _id = inline_query.query.split()[1]
        msg = inline_query.query.split(None, 2)[2].strip()

        if not msg or not msg.endswith(":"):
            inline_query.stop_propagation()

        try:
            penerima = await app.get_users(_id.strip())
        except Exception:  # pylint: disable=broad-except
            inline_query.stop_propagation()
            return

        PRVT_MSGS[inline_query.id] = (
            penerima.id,
            penerima.first_name,
            inline_query.from_user.id,
            msg.strip(": "),
        )
        prvte_msg = InlineKeyboardMarkup(
            [
                [InlineKeyboardButton("Show Message 🔐", callback_data=f"prvtmsg({inline_query.id})")],
                [
                    InlineKeyboardButton(
                        "Destroy☠️ this msg",
                        callback_data=f"destroy({inline_query.id})",
                    )
                ],
            ]
        )
        mention = f"@{penerima.username}" if penerima.username else f"<a href='tg://user?id={penerima.id}'>{penerima.first_name}</a>"
        msg_c = f"🔒 A <b>private message</b> to {mention} [<code>{penerima.id}</code>], "
        msg_c += "Only he/she can open it."
        results = [
            InlineQueryResultArticle(
                title=f"A Private Msg to {penerima.first_name}",
                input_message_content=InputTextMessageContent(msg_c),
                description="Only he/she can open it",
                thumb_url="https://te.legra.ph/file/16133ab3297b3f73c8da5.png",
                reply_markup=prvte_msg,
            )
        ]
        await inline_query.answer(results=results, cache_time=3)
    elif inline_query.query.strip().lower().split()[0] == "git":
        if len(inline_query.query.strip().lower().split()) < 2:
            return await inline_query.answer(
                results=[],
                switch_pm_text="Github Search | git [QUERY]",
                switch_pm_parameter="inline",
            )
        query = inline_query.query.split(None, 1)[1].strip()
        search_results = await http.get(f"https://api.github.com/search/repositories?q={query}")
        srch_results = json.loads(search_results.text)
        item = srch_results.get("items")
        data = []
        for sraeo in item:
            title = sraeo.get("full_name")
            link = sraeo.get("html_url")
            deskripsi = sraeo.get("description")
            lang = sraeo.get("language")
            message_text = f"🔗: {sraeo.get('html_url')}\n│\n└─🍴Forks: {sraeo.get('forks')}    ┃┃    🌟Stars: {sraeo.get('stargazers_count')}\n\n"
            message_text += f"<b>Description:</b> {deskripsi}\n"
            message_text += f"<b>Language:</b> {lang}"
            data.append(
                InlineQueryResultArticle(
                    title=f"{title}",
                    input_message_content=InputTextMessageContent(
                        message_text=message_text,
                        parse_mode=enums.ParseMode.HTML,
                        disable_web_page_preview=False,
                    ),
                    url=link,
                    description=deskripsi,
                    thumb_url="https://github.githubassets.com/images/modules/logos_page/GitHub-Mark.png",
                    reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(text="Open Github Link", url=link)]]),
                )
            )
        await inline_query.answer(
            results=data,
            is_gallery=False,
            is_personal=False,
            next_offset="",
            switch_pm_text=f"Found {len(data)} results",
            switch_pm_parameter="github",
        )
    elif inline_query.query.strip().lower().split()[0] == "pypi":
        if len(inline_query.query.strip().lower().split()) < 2:
            return await inline_query.answer(
                results=[],
                switch_pm_text="Pypi Search | pypi [QUERY]",
                switch_pm_parameter="inline",
            )
        query = inline_query.query.split(None, 1)[1].strip()
        search_results = await http.get(f"https://api.hayo.my.id/api/pypi?package={query}")
        srch_results = json.loads(search_results.text)
        data = []
        for sraeo in srch_results:
            title = sraeo.get("title")
            link = sraeo.get("link")
            deskripsi = sraeo.get("desc")
            version = sraeo.get("version")
            message_text = f"<a href='{link}'>{title} {version}</a>\n"
            message_text += f"Description: {deskripsi}\n"
            data.append(
                InlineQueryResultArticle(
                    title=f"{title}",
                    input_message_content=InputTextMessageContent(
                        message_text=message_text,
                        parse_mode=enums.ParseMode.HTML,
                        disable_web_page_preview=False,
                    ),
                    url=link,
                    description=deskripsi,
                    thumb_url="https://raw.githubusercontent.com/github/explore/666de02829613e0244e9441b114edb85781e972c/topics/pip/pip.png",
                    reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(text="Open Link", url=link)]]),
                )
            )
        await inline_query.answer(
            results=data,
            is_gallery=False,
            is_personal=False,
            next_offset="",
            switch_pm_text=f"Found {len(data)} results",
            switch_pm_parameter="pypi",
        )
    elif inline_query.query.strip().lower().split()[0] == "yt":
        if len(inline_query.query.strip().lower().split()) < 2:
            return await inline_query.answer(
                results=[],
                switch_pm_text="YouTube Search | yt [QUERY]",
                switch_pm_parameter="inline",
            )
        judul = inline_query.query.split(None, 1)[1].strip()
        search_results = await http.get(f"https://api.abir-hasan.tk/youtube?query={judul}")
        srch_results = json.loads(search_results.text)
        asroe = srch_results.get("results")
        oorse = []
        for sraeo in asroe:
            title = sraeo.get("title")
            link = sraeo.get("link")
            view = sraeo.get("viewCount").get("text")
            thumb = sraeo.get("thumbnails")[0].get("url")
            durasi = sraeo.get("accessibility").get("duration")
            publishTime = sraeo.get("publishedTime")
            try:
                deskripsi = "".join(f"{i['text']} " for i in sraeo.get("descriptionSnippet"))
            except:
                deskripsi = "-"
            message_text = f"<a href='{link}'>{title}</a>\n"
            message_text += f"Description: {deskripsi}\n"
            message_text += f"Total View: {view}\n"
            message_text += f"Duration: {durasi}\n"
            message_text += f"Published Time: {publishTime}"
            oorse.append(
                InlineQueryResultArticle(
                    title=f"{title}",
                    input_message_content=InputTextMessageContent(
                        message_text=message_text,
                        parse_mode=enums.ParseMode.HTML,
                        disable_web_page_preview=False,
                    ),
                    url=link,
                    description=deskripsi,
                    thumb_url=thumb,
                    reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(text="Watch Video 📹", url=link)]]),
                )
            )
        await inline_query.answer(
            results=oorse,
            is_gallery=False,
            is_personal=False,
            next_offset="",
            switch_pm_text=f"Found {len(asroe)} results",
            switch_pm_parameter="yt",
        )
    elif inline_query.query.strip().lower().split()[0] == "imdb":
        if len(inline_query.query.strip().lower().split()) < 2:
            return await inline_query.answer(
                results=[],
                switch_pm_text="IMDB Search | imdb [QUERY]",
                switch_pm_parameter="inline",
            )
        movie_name = inline_query.query.split(None, 1)[1].strip()
        search_results = await http.get(f"https://yasirapi.eu.org/imdb-search?q={movie_name}")
        res = json.loads(search_results.text).get("result")
        oorse = []
        for midb in res:
            title = midb.get("l", "")
            description = midb.get("q", "")
            stars = midb.get("s", "")
            imdb_url = f"https://imdb.com/title/{midb.get('id')}"
            year = f"({midb.get('y', '')})"
            image_url = midb.get("i").get("imageUrl").replace(".jpg", "._V1_UX360.jpg") if midb.get("i") else "https://te.legra.ph/file/e263d10ff4f4426a7c664.jpg"
            caption = f"<a href='{image_url}'>🎬</a>"
            caption += f"<a href='{imdb_url}'>{title} {year}</a>"
            oorse.append(
                InlineQueryResultPhoto(
                    title=f"{title} {year}",
                    caption=caption,
                    description=f" {description} | {stars}",
                    photo_url=image_url,
                    reply_markup=InlineKeyboardMarkup(
                        [
                            [
                                InlineKeyboardButton(
                                    text="Get IMDB details",
                                    callback_data=f"imdbinl#{inline_query.from_user.id}#{midb.get('id')}",
                                )
                            ]
                        ]
                    ),
                )
            )
        resfo = json.loads(search_results.text).get("q")
        await inline_query.answer(
            results=oorse,
            is_gallery=False,
            is_personal=False,
            next_offset="",
            switch_pm_text=f"Found {len(oorse)} results for {resfo}",
            switch_pm_parameter="imdb",
        )


@app.on_callback_query(filters.regex(r"prvtmsg\((.+)\)"))
async def prvt_msg(_, c_q):
    msg_id = str(c_q.matches[0].group(1))

    if msg_id not in PRVT_MSGS:
        await c_q.answer("message now outdated !", show_alert=True)
        return

    user_id, flname, sender_id, msg = PRVT_MSGS[msg_id]

    if c_q.from_user.id in (user_id, sender_id):
        await c_q.answer(msg, show_alert=True)
    else:
        await c_q.answer(f"only {flname} can see this Private Msg!", show_alert=True)


@app.on_callback_query(filters.regex(r"destroy\((.+)\)"))
async def destroy_msg(_, c_q):
    msg_id = str(c_q.matches[0].group(1))

    if msg_id not in PRVT_MSGS:
        await c_q.answer("message now outdated !", show_alert=True)
        return

    user_id, flname, sender_id, msg = PRVT_MSGS[msg_id]

    if c_q.from_user.id in (user_id, sender_id):
        del PRVT_MSGS[msg_id]
        by = "receiver" if c_q.from_user.id == user_id else "sender"
        await c_q.edit_message_text(f"This secret message is ☠️destroyed☠️ by msg {by}")
    else:
        await c_q.answer(f"only {flname} can see this Private Msg!", show_alert=True)


@app.on_callback_query(filters.regex("^imdbinl#"))
async def imdb_inl(_, query):
    i, user, movie = query.data.split("#")
    if user == f"{query.from_user.id}":
        await query.edit_message_caption("⏳ <i>Permintaan kamu sedang diproses.. </i>")
        try:
            url = f"https://www.imdb.com/title/{movie}/"
            resp = await get_content(url)
            sop = BeautifulSoup(resp, "lxml")
            r_json = json.loads(sop.find("script", attrs={"type": "application/ld+json"}).contents[0])
            ott = await search_jw(r_json["name"], "en_ID")
            res_str = ""
            typee = r_json.get('@type', '')
            if r_json.get("name"):
                try:
                    tahun = sop.select('ul[data-testid="hero-title-block__metadata"]')[0].find("span", class_="sc-8c396aa2-2 jwaBvf").text
                except:
                    tahun = "N/A"
                res_str += f"<b>📹 Judul:</b> <a href='{url}'>{r_json['name']} [{tahun}]</a> (<code>{typee}</code>)\n"
            if r_json.get("alternateName"):
                res_str += f"<b>📢 AKA:</b> <code>{r_json.get('alternateName')}</code>\n\n"
            else:
                res_str += "\n"
            if durasi := sop.select('li[data-testid="title-techspec_runtime"]'):
                durasi = durasi[0].find(class_="ipc-metadata-list-item__content-container").text
                res_str += f"<b>Durasi:</b> <code>{GoogleTranslator('auto', 'id').translate(durasi)}</code>\n"
            if r_json.get("contentRating"):
                res_str += f"<b>Kategori:</b> <code>{r_json['contentRating']}</code> \n"
            if r_json.get("aggregateRating"):
                res_str += f"<b>Peringkat:</b> <code>{r_json['aggregateRating']['ratingValue']}⭐️ dari {r_json['aggregateRating']['ratingCount']} pengguna</code> \n"
            if release := sop.select('li[data-testid="title-details-releasedate"]'):
                rilis = release[0].find(class_="ipc-metadata-list-item__list-content-item ipc-metadata-list-item__list-content-item--link").text
                rilis_url = release[0].find(class_="ipc-metadata-list-item__list-content-item ipc-metadata-list-item__list-content-item--link")["href"]
                res_str += f"<b>Rilis:</b> <a href='https://www.imdb.com{rilis_url}'>{rilis}</a>\n"
            if r_json.get("genre"):
                genre = "".join(f"{GENRES_EMOJI[i]} #{i.replace('-', '_').replace(' ', '_')}, " if i in GENRES_EMOJI else f"#{i.replace('-', '_').replace(' ', '_')}, " for i in r_json["genre"])
                genre = genre[:-2]
                res_str += f"<b>Genre:</b> {genre}\n"
            if negara := sop.select('li[data-testid="title-details-origin"]'):
                country = "".join(
                    f"{demoji(country.text)} #{country.text.replace(' ', '_').replace('-', '_')}, "
                    for country in negara[0].findAll(class_="ipc-metadata-list-item__list-content-item ipc-metadata-list-item__list-content-item--link")
                )
                country = country[:-2]
                res_str += f"<b>Negara:</b> {country}\n"
            if bahasa := sop.select('li[data-testid="title-details-languages"]'):
                language = "".join(
                    f"#{lang.text.replace(' ', '_').replace('-', '_')}, "
                    for lang in bahasa[0].findAll(class_="ipc-metadata-list-item__list-content-item ipc-metadata-list-item__list-content-item--link")
                )
                language = language[:-2]
                res_str += f"<b>Bahasa:</b> {language}\n"
            res_str += "\n<b>🙎 Info Cast:</b>\n"
            if r_json.get("director"):
                director = ""
                for i in r_json["director"]:
                    name = i["name"]
                    url = i["url"]
                    director += f"<a href='https://www.imdb.com{url}'>{name}</a>, "
                director = director[:-2]
                res_str += f"<b>Sutradara:</b> {director}\n"
            if r_json.get("creator"):
                creator = ""
                for i in r_json["creator"]:
                    if i["@type"] == "Person":
                        name = i["name"]
                        url = i["url"]
                        creator += f"<a href='https://www.imdb.com{url}'>{name}</a>, "
                creator = creator[:-2]
                res_str += f"<b>Penulis:</b> {creator}\n"
            if r_json.get("actor"):
                actors = ""
                for i in r_json["actor"]:
                    name = i["name"]
                    url = i["url"]
                    actors += f"<a href='https://www.imdb.com{url}'>{name}</a>, "
                actors = actors[:-2]
                res_str += f"<b>Pemeran:</b> {actors}\n\n"
            if r_json.get("description"):
                summary = GoogleTranslator("auto", "id").translate(r_json.get("description"))
                res_str += f"<b>📜 Plot: </b> <code>{summary}</code>\n\n"
            if r_json.get("keywords"):
                keywords = r_json["keywords"].split(",")
                key_ = ""
                for i in keywords:
                    i = i.replace(" ", "_").replace("-", "_")
                    key_ += f"#{i}, "
                key_ = key_[:-2]
                res_str += f"<b>🔥 Kata Kunci:</b> {key_} \n"
            if award := sop.select('li[data-testid="award_information"]'):
                awards = award[0].find(class_="ipc-metadata-list-item__list-content-item").text
                res_str += f"<b>🏆 Penghargaan:</b> <code>{GoogleTranslator('auto', 'id').translate(awards)}</code>\n"
            else:
                res_str += "\n"
            if ott != "":
                res_str += f"Available On:\n{ott}\n"
            res_str += "<b>©️ IMDb by</b> @MissKatyRoBot"
            if r_json.get("trailer"):
                trailer_url = r_json["trailer"]["url"]
                markup = InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(
                                "🎬 Buka IMDB",
                                url=f"https://www.imdb.com{r_json['url']}",
                            ),
                            InlineKeyboardButton("▶️ Trailer", url=trailer_url),
                        ]
                    ]
                )
            else:
                markup = InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(
                                "🎬 Open IMDB",
                                url=f"https://www.imdb.com{r_json['url']}",
                            )
                        ]
                    ]
                )
            await query.edit_message_caption(res_str, parse_mode=enums.ParseMode.HTML, reply_markup=markup)
        except Exception:
            exc = traceback.format_exc()
            await query.edit_message_caption(f"<b>ERROR:</b>\n<code>{exc}</code>")
    else:
        await query.answer("⚠️ Akses Ditolak!", True)
