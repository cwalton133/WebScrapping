import asyncio
import aiosqlite
import aiohttp
from bs4 import BeautifulSoup

async def create_database():
    async with aiosqlite.connect('movies.db') as db:
        await db.execute('''CREATE TABLE IF NOT EXISTS International (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            movie_name TEXT,
                            date TEXT,
                            link TEXT,
                            Description TEXT,
                            Download_link TEXT,
                            img TEXT)''')
        await db.commit()

async def data_exists(db, title, date):
    cursor = await db.execute("SELECT COUNT(*) FROM International WHERE movie_name=? AND date=?", (title, date))
    count = (await cursor.fetchone())[0]
    return count > 0

async def insert_data(db, title, date, link, desc, download, image):
    if not await data_exists(db, title, date):
        await db.execute("INSERT INTO International (movie_name, date, link, Description, Download_link, img) VALUES(?, ?, ?, ?, ?, ?)", (title, date, link, str(desc), download, image))
        await db.commit()
        return "Data inserted"

async def fetch(session, url):
    async with session.get(url) as response:
        return await response.text()

async def fetch_movie_details(session, movie_url):
    movie_page = await fetch(session, movie_url)
    movie_soup = BeautifulSoup(movie_page, 'html.parser')

    download_link = None
    for x in movie_soup.find_all('a', {'class': "elementor-button elementor-button-link elementor-size-md"}):
        download = x.get('href')
        if 'html' in download:
            download_link = download
            break

    desc_text = None
    for item in movie_soup.find_all('div', {'class': 'overview'}):
        desc = item.find('p')
        if desc:
            desc_text = desc.text.strip()
            break

    return download_link, desc_text

async def main():
    base_url = "https://nkiri.com/category/international/"
    async with aiohttp.ClientSession() as session:
        async with aiosqlite.connect('movies.db') as db:
            await create_database()

            tasks = []
            for num in range(1, 80):
                url = f'{base_url}page/{num}'
                print(f"Getting data for page {num}")
                page_content = await fetch(session, url)
                soup = BeautifulSoup(page_content, 'html.parser')

                for movie in soup.find_all('article'):
                    title = movie.find('h2', {'class': "blog-entry-title entry-title"})
                    name = title.text.strip() if title else None

                    date = movie.find('div', {'class': 'blog-entry-date clr'})
                    f_date = date.text.strip() if date else None

                    img = movie.find('img')
                    image = img.get('src') if img else None

                    link = movie.find('a')['href']
                    tasks.append(asyncio.create_task(handle_movie(db, session, name, f_date, link, image)))

            await asyncio.gather(*tasks)
            print("Successfully added into Database! :)")

async def handle_movie(db, session, name, f_date, link, image):
    download_link, desc_text = await fetch_movie_details(session, link)
    await insert_data(db, name, f_date, link, desc_text, download_link, image)
    print(f"Inserted data for movie: {name}")


if __name__ == '__main__':
    asyncio.run(main())
    
            