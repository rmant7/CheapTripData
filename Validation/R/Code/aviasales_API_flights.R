library(tidyverse)
library(httr)
library(usethis)


# Get flight routes
run2 <- read_csv("all_direct_routes_2_run.csv") %>%
  filter(transport_id == 1)
run3 <- read_csv("all_direct_routes_3_run.csv") %>%
  filter(transport_id == 1)
run4 <- read_csv("all_direct_routes_for_validation_4run.csv") %>%
  filter(transport_id == 1) %>%
  select(from_id:duration_min)
run <- rbind(run2, run3, run4) %>%
  select(from_id,
         to_id) %>%
  distinct()
locations <- readxl::read_excel("Full_list_with_countries.xlsx", col_names = FALSE) %>%
  rename(id_city = ...1, 
         city = ...2, 
         id_country = ...3, 
         country = ...8) %>%
  select(id_city, city, id_country, country)
locations_from <- locations %>%
  rename(from_id = id_city, from_city = city,
         from_country_id = id_country, from_country = country)
locations_to <- locations %>%
  rename(to_id = id_city, to_city = city,
         to_country_id = id_country, to_country = country)
connected_from <- left_join(run, locations_from, by = "from_id")
connected_to <- left_join(connected_from, locations_to, by = "to_id")
# Get IATA codes
city_code <- GET("http://api.travelpayouts.com/data/en/cities.json")
city_code_resp <- jsonlite::fromJSON(rawToChar(city_code$content))
city_code_df <- city_code_resp %>%
  select(code:name)
city_from <- tibble(from_code = city_code_df$code,
                    from_lat = city_code_df$coordinates$lat,
                    from_lon = city_code_df$coordinates$lon,
                    from_city = city_code_df$name)
city_to <- tibble(to_code = city_code_df$code,
                  to_lat = city_code_df$coordinates$lat,
                  to_lon = city_code_df$coordinates$lon,
                  to_city = city_code_df$name)
from <- left_join(connected_to, city_from, by = "from_city")
to <- left_join(from, city_to, by = "to_city")
all_routes_with_codes <- to %>%
  select(from_code,
         to_code,
         from_city,
         to_city)
query_link <- paste0("https://api.travelpayouts.com/aviasales/v3/prices_for_dates?currency=eur&origin=",
                     all_routes_with_codes$from_code, "&destination=", 
                     all_routes_with_codes$to_code, 
                     "&unique=false&sorting=price&direct=false&limit=3&page=1&one_way=true&token=", Sys.getenv("aviasales_API_token"))

api_call <- function(link) {
  query <- GET(link)
  resp <- jsonlite::fromJSON(rawToChar(query$content))
  resp$data
}

data_with_cheap_flights <- data_frame()
for (i in 1:length(query_link)) {
  data <- api_call(query_link[i])
  data_with_cheap_flights <- rbind(data_with_cheap_flights, data)
}



write_csv(data_with_cheap_flights, "aviasales_API_flights.csv")
