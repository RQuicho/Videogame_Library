## Project Proposal

1. What goal will your website be designed to achieve?  
   This website will help users organize video games that they want to play, have played, or are planning to play.
2. What kind of users will visit your site? In other words, what is the demographic of your users?  
   People who play video games, specifically people who play enough video games who would want to organize them in some way.
3. What data do you plan on using?  
   I will be using this api: https://api.rawg.io/docs/.
4. Outline of approach?  
   a. What does your database schema look like?  
   Creators, Developers, Game, Genre, Platforms, Publishers, Store. Many-To-Many relationships  
   b. What kinds of issues might you run into with your API?  
   Can't think of any yet. The API seems pretty comprehensive. Will update answer after working more with API.  
   c. Is there any sensitive information you need to secure?  
   I am planning on having a user login/logout feature so they can sign in and see what their library looks like. Need to make sure passwords are hashed properly.  
   d. What functionality will your app include?  
   CRUD games to their library, rate games, sort by info (rating, alphabetically, developer, genre, etc), filter games so only some display, favorite games  
   e. What will the user flow look like?  
   User will create an account or sign in. Their library should appear. They can CRUD a game by selecting different search filters. Favorite games. Sort games.  
   f. What features make your site more than CRUD? Do you have any stretch goals?  
   Favorite games. Sort/filter games.
