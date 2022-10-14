TOKEN = "5718147424:AAEHIFnx5WGlIogFcnbrMPzQOO8jR039G8E"
LIMIT_PAGE = 30
BASE_URL = 'https://gogoanime.herokuapp.com'
RECENT_RELEASE_ANIME_URL=f'{BASE_URL}/recent-release?type=2&page={LIMIT_PAGE}'
POPULAR_ANIME_URL = f'{BASE_URL}/popular?page={LIMIT_PAGE}'
SEARCH_ANIME_URL = f'{BASE_URL}/search'
GENRE_ANIME_URL =f'{BASE_URL}/genre'
MOVIES_ANIME_URL = f'{BASE_URL}/anime-movies?page={LIMIT_PAGE}'
TOP_AIRING_URL = f'{BASE_URL}/top-airing?page={LIMIT_PAGE}'
DETAILS_ANIME_URL = f'{BASE_URL}/anime-details'
GENRES_LIST = ['action','adventure','cars','comedy','crime','dementia','demons','drama','dub','ecchi',
    'family','fantasy','game','gourmet','harem','historical','horror','josei','kids','magic','martial-arts',
    'mecha','military','music','mystery','parody','police','psychological','romance','samurai','school',
    'sci-fi','seinen','shoujo','shoujo-ai','shounen','shounen-ai','slice-of-Life','space','sports',
    'super-power','supernatural','suspense','thriller','vampire','yaoi','yuri',
]
EPISODE_LIST_PORTION = 8