SELECT
    name,
    brand,
    terabeer_style,
    abv,
    ibu,
    ratings_count,
    ratings_avg,
    style_description,
    figure,
    ratings_source,
    ratings_url,
    COALESCE(origin_state, '???') AS origin_state,
    offer_url,
    harmonization
FROM
    beer_list
WHERE
    offer_url IS NOT NULL
    AND ratings_count > 0
    AND ratings_avg > 0
    AND ratings_url IS NOT NULL
    AND ratings_source IS NOT NULL
