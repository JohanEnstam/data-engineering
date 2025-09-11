-- Staging model för games data
-- Rensar och standardiserar raw games data från BigQuery

SELECT 
  id,
  name,
  summary,
  storyline,
  rating,
  rating_count,
  release_date,
  release_year,
  genres,
  genre_count,
  themes,
  theme_count,
  platforms,
  platform_count,
  game_modes,
  player_perspectives,
  cover_id,
  cover_url,
  screenshot_ids,
  screenshot_count,
  website_ids,
  
  -- Genre features (one-hot encoded)
  genre_Point_and_click,
  genre_Fighting,
  genre_Shooter,
  genre_Music,
  genre_Platform,
  genre_Puzzle,
  genre_Racing,
  genre_Real_Time_Strategy_RTS,
  genre_Role_playing_RPG,
  genre_Simulator,
  genre_Sport,
  genre_Strategy,
  genre_Turn_based_strategy_TBS,
  genre_Tactical,
  genre_Hack_and_slash_Beat_em_up,
  genre_Adventure,
  genre_Indie,
  genre_Arcade,
  genre_Visual_Novel,
  genre_Card_and_Board_Game,
  
  -- Theme features (one-hot encoded)
  theme_Action,
  theme_Fantasy,
  theme_Science_fiction,
  theme_Horror,
  theme_Thriller,
  theme_Survival,
  theme_Historical,
  theme_Stealth,
  theme_Comedy,
  theme_Drama,
  theme_Non_fiction,
  theme_Sandbox,
  theme_Educational,
  theme_Kids,
  theme_Open_world,
  theme_Party,
  theme_4X_explore_expand_exploit_and_exterminate,
  theme_Erotic,
  theme_Mystery,
  theme_Romance,
  
  -- Platform features (one-hot encoded)
  platform_Linux,
  platform_PC_Microsoft_Windows,
  platform_PlayStation_2,
  platform_PlayStation_3,
  platform_Xbox_360,
  platform_DOS,
  platform_Commodore_C64_128_MAX,
  platform_Nintendo_DS,
  platform_Turbografx_16_PC_Engine_CD,
  platform_Sega_Saturn,
  platform_Sega_Game_Gear,
  platform_SteamVR,
  platform_PlayStation_VR,
  platform_iOS,
  platform_PlayStation_5,
  platform_Wii_U,
  platform_PlayStation_Vita,
  platform_PlayStation_4,
  platform_Sega_CD,
  platform_TurboGrafx_16_PC_Engine,
  platform_Virtual_Boy,
  platform_Apple_IIGS,
  
  -- Data quality checks
  CASE 
    WHEN name IS NULL THEN 'Missing Name'
    WHEN rating IS NULL THEN 'Missing Rating'
    WHEN release_year IS NULL THEN 'Missing Release Year'
    ELSE 'Valid'
  END as data_quality_status,
  
  -- Derived fields
  CASE 
    WHEN rating >= 80 THEN 'Excellent'
    WHEN rating >= 70 THEN 'Good'
    WHEN rating >= 60 THEN 'Average'
    WHEN rating >= 50 THEN 'Below Average'
    ELSE 'Poor'
  END as rating_category,
  
  CASE 
    WHEN release_year >= 2020 THEN 'Recent'
    WHEN release_year >= 2010 THEN 'Modern'
    WHEN release_year >= 2000 THEN 'Classic'
    ELSE 'Retro'
  END as era_category

FROM {{ source('raw', 'games_raw') }}
WHERE name IS NOT NULL
