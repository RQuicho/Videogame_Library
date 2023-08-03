fetch('/get_api_key')
  .then(response => response.json())
  .then(data => {
    API_KEY = data.api_key;
  })
.catch(error => console.log('Error fetching API key:', error));


isEndOfPage = () => {
  return window.innerHeight + window.scrollY >= document.documentElement.scrollHeight;
}

const gameList = document.querySelector('.gameList');

createGameCard = (game) => {
    const gameCard = document.createElement('div');
    gameCard.classList.add('col');
    gameCard.innerHTML = `      
      <div class="card">
        <img src="${game.background_image}" class="card-img-top" alt="Image of ${game.name}">
        <div class="card-body">
          <h5 class="card-title">${game.name}</h5>
          <p class="card-text">Genre: ${game.genres ? game.genres.map(genre => genre.name).join(' | ') : 'N/A'}</p>
          <p class="card-text">Platforms: ${game.platforms ? game.platforms.map(platform => platform.platform.name).join(' | ') : 'N/A'}</p>
          <p class="card-text">Released: ${game.released ? game.released : 'N/A'}</p>
          <p class="card-text">ESRB Rating: ${game.esrb_rating ? game.esrb_rating.name : 'N/A'}</p>
        </div>
        <div class="card-body">
          <div class="dropdown">
            <button class="btn btn-secondary dropdown-toggle dropdown-gamecard-btn" type="button" data-bs-toggle="dropdown" aria-expanded="false">
              Add Game
            </button>
            <ul class="dropdown-menu" data-bs-theme="dark">
              <li>
                <form method="POST" action="/all_games/${game.id}">
                  <button class="dropdown-item" href="/">All Games</button>
                </form>
              </li>
              <li>
                <form method="POST" action="/favorites/${game.id}">
                  <button class="dropdown-item" href="/">Favorites</button>
                </form>
              </li>     
              <li>
                <form method="POST" action="/played/${game.id}">
                  <button class="dropdown-item" href="/">Played</button>
                </form>
              </li>    
              <li>
                <form method="POST" action="/completed/${game.id}">
                  <button class="dropdown-item" href="/">Completed</button>
                </form>
              </li> 
              <li>
                <form method="POST" action="/planned/${game.id}">
                  <button class="dropdown-item" href="/">Plan to Play</button>
                </form>
              </li>            
            </ul>
          </div>
          <a href="/games/${game.id}" class="card-link btn btn-secondary">See Details</a>
        </div>
      </div>
    `;
    return gameCard;
}

appendGameCardToList = (gameCard) => {
  gameList.appendChild(gameCard);
}

let nextPage = 2;

loadMoreGames = () => {
    const platformFilter = selectedPlatformId ? `&parent_platforms=${selectedPlatformId}` : '';
    const url = `https://api.rawg.io/api/games?key=${API_KEY}&page=${nextPage}${platformFilter}`;
    console.log('selectedPlatformId: ', selectedPlatformId);

    fetch(url)
        .then((response) => response.json())
        .then((data) => {
            const games = data.results;

            if(games.length > 0) {
                games.forEach((game) => {
                    const gameCard = createGameCard(game);
                    appendGameCardToList(gameCard);
                });

                nextPage++;
                console.log(`nextPage: ${nextPage}`)
            }
        })
        .catch((error) => console.log('Error fetching games:', error));
}

///////////////// Scroll when platform filter clicked ///////////////

let selectedPlatformId = null;

const handlePlatformSelection = (platformID) => {
  selectedPlatformId = platformID;
  console.log('selectedPlatformId: ', selectedPlatformId);
  gameList.innerHTML = '';
  nextPage = 1;
  loadMoreGames();
}

handleScroll = () => {
    if (isEndOfPage()) {
        loadMoreGames();
    }
}

window.addEventListener('scroll', handleScroll);