-- Mart model för game recommendations
-- Skapar en optimerad tabell för ML-rekommendationer

SELECT 
  id,
  name,
  summary,
  storyline,
  rating,
  rating_count,
  release_year,
  rating_category,
  era_category,
  data_quality_status,
  
  -- Genre features för ML
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
  
  -- Theme features för ML
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
  
  -- Platform features för ML
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
  
  -- Metadata för rekommendationer
  cover_url,
  screenshot_count,
  genre_count,
  theme_count,
  platform_count,
  
  -- ML features
  CASE 
    WHEN rating IS NULL THEN 0
    ELSE rating
  END as rating_imputed,
  
  CASE 
    WHEN release_year IS NULL THEN 2020
    ELSE release_year
  END as release_year_imputed,
  
  -- Feature vectors för similarity
  CONCAT(
    IFNULL(CAST(genre_Point_and_click AS STRING), '0'), ',',
    IFNULL(CAST(genre_Fighting AS STRING), '0'), ',',
    IFNULL(CAST(genre_Shooter AS STRING), '0'), ',',
    IFNULL(CAST(genre_Music AS STRING), '0'), ',',
    IFNULL(CAST(genre_Platform AS STRING), '0'), ',',
    IFNULL(CAST(genre_Puzzle AS STRING), '0'), ',',
    IFNULL(CAST(genre_Racing AS STRING), '0'), ',',
    IFNULL(CAST(genre_Real_Time_Strategy_RTS AS STRING), '0'), ',',
    IFNULL(CAST(genre_Role_playing_RPG AS STRING), '0'), ',',
    IFNULL(CAST(genre_Simulator AS STRING), '0'), ',',
    IFNULL(CAST(genre_Sport AS STRING), '0'), ',',
    IFNULL(CAST(genre_Strategy AS STRING), '0'), ',',
    IFNULL(CAST(genre_Turn_based_strategy_TBS AS STRING), '0'), ',',
    IFNULL(CAST(genre_Tactical AS STRING), '0'), ',',
    IFNULL(CAST(genre_Hack_and_slash_Beat_em_up AS STRING), '0'), ',',
    IFNULL(CAST(genre_Adventure AS STRING), '0'), ',',
    IFNULL(CAST(genre_Indie AS STRING), '0'), ',',
    IFNULL(CAST(genre_Arcade AS STRING), '0'), ',',
    IFNULL(CAST(genre_Visual_Novel AS STRING), '0'), ',',
    IFNULL(CAST(genre_Card_and_Board_Game AS STRING), '0')
  ) as genre_vector,
  
  -- Timestamp för data freshness
  CURRENT_TIMESTAMP() as processed_at

FROM {{ ref('stg_games') }}
WHERE data_quality_status = 'Valid'
  AND rating IS NOT NULL
  AND release_year IS NOT NULL
